import os

pdf_path = r"C:\Users\admin\.gemini\antigravity\scratch\gtu_ai_academic_bot\sample_notes\AI_Machine_Learning_GTU_Notes.pdf"
os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Page 1
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "GTU B.E. Computer Engineering - Artificial Intelligence Notes")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 70, "Subject Code: 3170716 | Module 1 & 2: Fundamentals of AI & Problem Solving")
    c.setStrokeColor(colors.gray)
    c.line(50, height - 78, width - 50, height - 78)

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, height - 105, "1. Foundations of AI & Intelligent Agents")
    c.setFont("Helvetica", 10)
    text_p1 = [
        "- Artificial Intelligence (AI) is the branch of computer science focused on creating systems capable of performing",
        "  tasks that typically require human intelligence, such as reasoning, learning, perception, and decision making.",
        "- Intelligent Agent: An agent is anything that perceives its environment through sensors and acts upon it through actuators.",
        "- PEAS Framework: Performance measure, Environment, Actuators, Sensors. Essential for defining agent tasks.",
        "  Example for Automated Taxi: P = Safety/Speed, E = Roads/Traffic, A = Steering/Brake, S = Cameras/Lidar.",
        "- Types of Agents: Simple Reflex Agent, Model-based Reflex Agent, Goal-based Agent, and Utility-based Agent."
    ]
    y = height - 125
    for line in text_p1:
        c.drawString(50, y, line)
        y -= 16

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y - 10, "2. Search Algorithms in AI")
    y -= 30
    text_p2 = [
        "- Breadth-First Search (BFS): Explores nodes level-by-level using a FIFO queue. It is complete and optimal for unweighted graphs.",
        "  Time Complexity: O(b^d), Space Complexity: O(b^d), where b is branching factor and d is depth.",
        "- Depth-First Search (DFS): Explores deepest node first using a LIFO stack. Space complexity is low: O(b*m), but not optimal.",
        "- A* Search: Best-known form of heuristic search. Evaluation function: f(n) = g(n) + h(n).",
        "  where g(n) is the exact cost to reach node n, and h(n) is the estimated heuristic cost from n to goal.",
        "  A* is complete and optimal if heuristic h(n) is admissible (never overestimates true cost) and consistent."
    ]
    for line in text_p2:
        c.drawString(50, y, line)
        y -= 16

    c.drawString(width - 100, 30, "Page 1 of 2")
    c.showPage()

    # Page 2
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "GTU AI Notes - Module 3 & 4: Machine Learning & Classification")
    c.setStrokeColor(colors.gray)
    c.line(50, height - 60, width - 50, height - 60)

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, height - 90, "3. Supervised vs Unsupervised Learning")
    y = height - 110
    text_p3 = [
        "- Supervised Learning: Model is trained on labeled dataset where both inputs (X) and ground-truth targets (y) are provided.",
        "  Common tasks: Classification (Spam detection, Disease diagnosis) and Regression (House price prediction).",
        "- Unsupervised Learning: Finds hidden patterns, structures, and groupings in unlabeled data. Tasks: K-Means Clustering, PCA.",
        "- Bias-Variance Tradeoff: High Bias leads to Underfitting (oversimplified model). High Variance leads to Overfitting (memorization).",
        "- Overfitting Prevention Techniques: Regularization (L1 Lasso, L2 Ridge), Cross-Validation (K-Fold), Early Stopping, and Pruning."
    ]
    for line in text_p3:
        c.drawString(50, y, line)
        y -= 16

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y - 10, "4. Decision Trees & Entropy")
    y -= 30
    text_p4 = [
        "- Decision Tree: Non-parametric supervised learning method used for classification and regression.",
        "- Entropy: Measures impurity/uncertainty in a dataset. Formula: H(S) = - sum( p_i * log2(p_i) ).",
        "- Information Gain (IG): Expected reduction in entropy from partitioning data on an attribute. Formula: IG(S, A) = H(S) - Remainder(A).",
        "- The attribute with the highest Information Gain is chosen as the splitting root node at each step."
    ]
    for line in text_p4:
        c.drawString(50, y, line)
        y -= 16

    c.drawString(width - 100, 30, "Page 2 of 2")
    c.showPage()
    c.save()
    print("Successfully generated sample notes PDF at:", pdf_path)
except Exception as e:
    print("PDF generation with reportlab skipped or waiting for reportlab install:", e)
