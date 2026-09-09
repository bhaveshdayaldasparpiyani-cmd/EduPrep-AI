import os
import io
import json
import re
import math
import base64
from typing import List, Dict, Any, Tuple
import requests
import pypdf
from gtts import gTTS

from prompts import (
    MULTILINGUAL_QA_SYSTEM_PROMPT,
    GTU_EXAM_PAPER_PROMPT,
    MCQ_QUIZ_PROMPT,
    FLASHCARD_PROMPT,
    MOCK_VIVA_EVALUATE_PROMPT,
    SYLLABUS_COVERAGE_PROMPT,
    VISION_NOTES_PROMPT,
    REVISION_SUMMARY_PROMPT
)

# Text chunk representation
class DocumentChunk:
    def __init__(self, text: str, source: str, page: int, chunk_id: int):
        self.text = text
        self.source = source
        self.page = page
        self.chunk_id = chunk_id
        self.embedding = None

class RAGEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key.strip() if api_key else ""
        self.chunks: List[DocumentChunk] = []
        self.faiss_index = None
        self.discovered_models: List[str] = []

    def set_api_key(self, api_key: str):
        self.api_key = api_key.strip() if api_key else ""
        self.discovered_models = []

    def extract_text_from_pdfs(self, uploaded_files) -> List[Dict[str, Any]]:
        extracted_pages = []
        for file in uploaded_files:
            try:
                reader = pypdf.PdfReader(file)
                source_name = getattr(file, "name", os.path.basename(str(file)))
                for page_idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        extracted_pages.append({
                            "source": source_name,
                            "page": page_idx + 1,
                            "text": page_text
                        })
            except Exception as e:
                print(f"Error reading PDF {file}: {e}")
        return extracted_pages

    def split_into_chunks(self, pages: List[Dict[str, Any]], chunk_size: int = 800, overlap: int = 150) -> List[DocumentChunk]:
        chunks = []
        chunk_id = len(self.chunks)
        
        for page_info in pages:
            text = page_info["text"]
            source = page_info["source"]
            page_num = page_info["page"]
            
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                chunk_text = text[start:end].strip()
                if len(chunk_text) > 30:
                    chunks.append(DocumentChunk(
                        text=chunk_text,
                        source=source,
                        page=page_num,
                        chunk_id=chunk_id
                    ))
                    chunk_id += 1
                start += chunk_size - overlap
                if end == len(text):
                    break
        self.chunks = chunks
        return chunks

    def add_custom_chunk(self, text: str, source: str = "Image Notes", page: int = 1):
        chunk_id = len(self.chunks)
        chunk = DocumentChunk(text=text, source=source, page=page, chunk_id=chunk_id)
        self.chunks.append(chunk)
        return chunk

    def _get_supported_generation_models(self) -> List[str]:
        if self.discovered_models:
            return self.discovered_models

        found_models = []
        for ver in ["v1beta", "v1"]:
            try:
                url = f"https://generativelanguage.googleapis.com/{ver}/models?key={self.api_key}"
                resp = requests.get(url, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    for m in data.get("models", []):
                        methods = m.get("supportedGenerationMethods", [])
                        if "generateContent" in methods:
                            m_name = m["name"]
                            if m_name not in found_models:
                                found_models.append(m_name)
                    if found_models:
                        break
            except Exception as e:
                print("Model discovery note:", e)

        def model_priority(m_name: str) -> int:
            name = m_name.lower()
            if "2.5-flash" in name: return 1
            if "2.0-flash" in name: return 2
            if "1.5-flash" in name: return 3
            if "flash" in name: return 4
            if "pro" in name: return 5
            return 10

        found_models.sort(key=model_priority)
        
        if not found_models:
            found_models = [
                "models/gemini-2.5-flash",
                "models/gemini-2.0-flash",
                "models/gemini-1.5-flash",
                "models/gemini-1.5-flash-8b",
                "models/gemini-1.5-pro",
                "models/gemini-pro"
            ]

        self.discovered_models = found_models
        return self.discovered_models

    def _embed_content(self, content_list: List[str]) -> List[List[float]]:
        if not self.api_key:
            return None

        embedding_models = ["models/text-embedding-004", "models/embedding-001"]

        for em in embedding_models:
            for ver in ["v1beta", "v1"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/{ver}/{em}:batchEmbedContents?key={self.api_key}"
                    payload = {
                        "requests": [
                            {
                                "model": em,
                                "content": {"parts": [{"text": text[:2000]}]},
                                "taskType": "RETRIEVAL_DOCUMENT"
                            }
                            for text in content_list
                        ]
                    }
                    r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
                    if r.status_code == 200:
                        data = r.json()
                        embs = [item["values"] for item in data.get("embeddings", [])]
                        if len(embs) == len(content_list):
                            return embs
                except Exception:
                    continue
        return None

    def build_vector_index(self, chunks: List[DocumentChunk]):
        if not self.api_key:
            raise ValueError("Gemini API key is required.")
        
        try:
            batch_texts = [c.text for c in chunks]
            batch_size = 15
            all_embeddings = []
            
            for i in range(0, len(batch_texts), batch_size):
                batch = batch_texts[i:i + batch_size]
                emb_res = self._embed_content(batch)
                if emb_res:
                    all_embeddings.extend(emb_res)
                else:
                    break

            if len(all_embeddings) == len(chunks):
                for idx, emb in enumerate(all_embeddings):
                    self.chunks[idx].embedding = emb
        except Exception as e:
            print(f"Embedding build note: {e}")

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def retrieve_relevant_chunks(self, query: str, top_k: int = 4) -> List[DocumentChunk]:
        if not self.chunks:
            return []

        if self.chunks[0].embedding is not None and self.api_key:
            query_embs = self._embed_content([query])
            if query_embs and len(query_embs) > 0:
                query_emb = query_embs[0]
                scored_chunks = []
                for chunk in self.chunks:
                    if chunk.embedding:
                        score = self.cosine_similarity(query_emb, chunk.embedding)
                        scored_chunks.append((score, chunk))
                scored_chunks.sort(key=lambda x: x[0], reverse=True)
                return [item[1] for item in scored_chunks[:top_k]]

        query_words = set(re.findall(r"\w+", query.lower()))
        scored = []
        for chunk in self.chunks:
            chunk_words = set(re.findall(r"\w+", chunk.text.lower()))
            overlap = len(query_words.intersection(chunk_words))
            scored.append((overlap, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def get_aggregated_context(self, max_chunks: int = 6) -> str:
        sample_chunks = self.chunks[:max_chunks]
        return "\n\n".join([f"[Source: {c.source}, Page {c.page}]\n{c.text}" for c in sample_chunks])

    def _generate_content(self, prompt: str, is_json: bool = False, image_bytes: bytes = None, mime_type: str = "image/jpeg") -> str:
        if not self.api_key:
            raise ValueError("Gemini API key is required.")

        models = self._get_supported_generation_models()
        last_error = None

        parts = [{"text": prompt}]
        if image_bytes:
            b64_data = base64.b64encode(image_bytes).decode("utf-8")
            parts.insert(0, {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64_data
                }
            })

        for model_path in models:
            clean_name = model_path if model_path.startswith("models/") else f"models/{model_path}"
            
            for ver in ["v1beta", "v1"]:
                url = f"https://generativelanguage.googleapis.com/{ver}/{clean_name}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"role": "user", "parts": parts}]
                }
                if is_json:
                    payload["generationConfig"] = {"responseMimeType": "application/json"}
                
                try:
                    resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=40)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts_out = candidates[0].get("content", {}).get("parts", [])
                            if parts_out:
                                return parts_out[0].get("text", "")
                    else:
                        last_error = f"HTTP {resp.status_code}: {resp.text}"
                except Exception as e:
                    last_error = str(e)
                    continue

        raise RuntimeError(f"Unable to generate response: {last_error}")

    # --- 1. MULTILINGUAL CHAT & AUDIO ---
    def query_multilingual(self, question: str, language: str = "English") -> Dict[str, Any]:
        relevant_chunks = self.retrieve_relevant_chunks(question, top_k=4)
        context_parts = [f"[File: {c.source} | Page: {c.page}]\n{c.text}" for c in relevant_chunks]
        citations = [{"source": c.source, "page": c.page, "snippet": c.text[:180] + "..."} for c in relevant_chunks]
        
        prompt = MULTILINGUAL_QA_SYSTEM_PROMPT.format(
            context="\n\n".join(context_parts),
            question=question,
            language=language
        )
        answer_text = self._generate_content(prompt, is_json=False)
        return {"answer": answer_text, "citations": citations}

    def generate_audio_speech(self, text: str, language: str = "English") -> bytes:
        """Convert explanation text to MP3 audio bytes using gTTS."""
        # Clean markdown symbols for natural speech
        clean_text = re.sub(r"[#*_`>\-]", " ", text)
        clean_text = clean_text[:600] # Take first 600 chars for fast concise audio
        
        lang_code = "en"
        if "gujarati" in language.lower():
            lang_code = "gu"
        elif "hindi" in language.lower():
            lang_code = "hi"
            
        try:
            tts = gTTS(text=clean_text, lang=lang_code, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception as e:
            print("TTS error fallback to en:", e)
            tts = gTTS(text=clean_text, lang="en", slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()

    # --- 2. MULTIMODAL VISION OCR & DIAGRAM SCANNER ---
    def scan_handwritten_notes_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        prompt = VISION_NOTES_PROMPT
        analysis = self._generate_content(prompt, is_json=False, image_bytes=image_bytes, mime_type=mime_type)
        # Add to knowledge chunks automatically
        self.add_custom_chunk(analysis, source="Handwritten Notes / Diagram Photo", page=1)
        return analysis

    # --- 3. DIGITAL FLASHCARDS ---
    def generate_flashcards(self, num_cards: int = 6) -> List[Dict[str, Any]]:
        context = self.get_aggregated_context(max_chunks=8)
        prompt = FLASHCARD_PROMPT.format(context=context, num_cards=num_cards)
        try:
            raw_text = self._generate_content(prompt, is_json=True).strip()
            raw_text = re.sub(r"^```json\s*", "", raw_text)
            raw_text = re.sub(r"^```\s*", "", raw_text)
            raw_text = re.sub(r"```$", "", raw_text).strip()
            match = re.search(r"\[\s*\{.*\}\s*\]", raw_text, re.DOTALL)
            if match:
                raw_text = match.group(0)
            cards = json.loads(raw_text)
            return cards
        except Exception as e:
            print("Flashcards JSON error:", e)
            return [
                {
                    "id": 1,
                    "category": "Definition",
                    "front": "What is Supervised Learning?",
                    "back": "Machine learning task of learning a function that maps an input to an output based on example input-output pairs."
                },
                {
                    "id": 2,
                    "category": "Formula",
                    "front": "Entropy Formula in Decision Trees",
                    "back": "H(S) = - sum( p_i * log2(p_i) ). Measures dataset impurity/disorder."
                }
            ]

    # --- 4. GTU MOCK VIVA EXAMINER ---
    def generate_viva_questions(self, num_questions: int = 5) -> List[str]:
        context = self.get_aggregated_context(max_chunks=6)
        prompt = f"Based on this engineering study context, generate {num_questions} tricky and conceptual GTU External Viva oral questions for a student. Return ONLY a JSON array of strings: [\"Question 1?\", \"Question 2?\"]\n\nContext:\n{context}"
        try:
            raw_text = self._generate_content(prompt, is_json=True).strip()
            raw_text = re.sub(r"^```json\s*", "", raw_text)
            raw_text = re.sub(r"^```\s*", "", raw_text)
            raw_text = re.sub(r"```$", "", raw_text).strip()
            match = re.search(r"\[.*\]", raw_text, re.DOTALL)
            if match:
                raw_text = match.group(0)
            return json.loads(raw_text)
        except Exception:
            return [
                "Explain the PEAS framework of an intelligent agent with a real-world example.",
                "Why is A* search considered both optimal and complete?",
                "What is the difference between Overfitting and Underfitting and how do you resolve them?",
                "How does Entropy help in selecting the root node of a Decision Tree?",
                "What is the role of Activation Functions in Neural Networks?"
            ]

    def evaluate_viva_exam(self, student_name: str, branch: str, semester: str, transcript: str) -> str:
        context = self.get_aggregated_context(max_chunks=8)
        prompt = MOCK_VIVA_EVALUATE_PROMPT.format(
            student_name=student_name,
            branch=branch,
            semester=semester,
            viva_transcript=transcript,
            context=context
        )
        return self._generate_content(prompt, is_json=False)

    # --- 5. SYLLABUS COVERAGE AUDIT ---
    def audit_syllabus_coverage(self, custom_syllabus: str = "Standard GTU Syllabus") -> str:
        context = self.get_aggregated_context(max_chunks=8)
        prompt = SYLLABUS_COVERAGE_PROMPT.format(
            context=context,
            custom_syllabus=custom_syllabus
        )
        return self._generate_content(prompt, is_json=False)

    # --- 6. GTU EXAM PAPER & REVISION ---
    def generate_gtu_paper(self, topic_focus: str = "All Chapters", difficulty: str = "Standard GTU Level") -> str:
        context = self.get_aggregated_context(max_chunks=8)
        prompt = GTU_EXAM_PAPER_PROMPT.format(context=context, topic_focus=topic_focus, difficulty=difficulty)
        return self._generate_content(prompt, is_json=False)

    def generate_mcq_quiz(self, num_questions: int = 5) -> List[Dict[str, Any]]:
        context = self.get_aggregated_context(max_chunks=8)
        prompt = MCQ_QUIZ_PROMPT.format(context=context, num_questions=num_questions)
        try:
            raw_text = self._generate_content(prompt, is_json=True).strip()
            raw_text = re.sub(r"^```json\s*", "", raw_text)
            raw_text = re.sub(r"^```\s*", "", raw_text)
            raw_text = re.sub(r"```$", "", raw_text).strip()
            match = re.search(r"\[\s*\{.*\}\s*\]", raw_text, re.DOTALL)
            if match:
                raw_text = match.group(0)
            quiz_data = json.loads(raw_text)
            if isinstance(quiz_data, dict) and "questions" in quiz_data:
                return quiz_data["questions"]
            return quiz_data
        except Exception as e:
            print("MCQ JSON error:", e)
            return [
                {
                    "id": 1,
                    "question": "What is the primary characteristic of Supervised Learning?",
                    "options": ["Learning from labeled training data", "Grouping unlabeled data", "Trial-and-error reward learning", "None of the above"],
                    "correct_index": 0,
                    "explanation": "Supervised learning maps inputs to targets using labeled examples."
                }
            ]

    def generate_revision_notes(self) -> str:
        context = self.get_aggregated_context(max_chunks=8)
        prompt = REVISION_SUMMARY_PROMPT.format(context=context)
        return self._generate_content(prompt, is_json=False)
