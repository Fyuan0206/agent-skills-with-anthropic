---
name: generating-practice-questions
description: Generate educational practice questions from lecture notes to test student understanding. Use when users request practice questions, exam preparation materials, study guides, or assessment items based on lecture content.
--- 

# Practice Question Generator

Generate comprehensive practice questions from lecture notes to test student understanding of learning objectives and key concepts.

## Input 

**Supported formats**: LaTeX (.tex), PDF, Markdown (.md), plain text (.txt)

- **PDF**: Use `pdfplumber` for text extraction

- **LaTeX**: Read as text, strip preamble (everything before `\begin{document}`), preserve math environments (`$...$`, `\[...\]`, `\begin{equation}`, etc.)

- **Markdown/Text**

**Content to extract**:

1. **Learning objectives** - Usually at beginning: "After this lecture, you should be able to..." or may be in section: "Learning Outcomes","Objectives", "Goals". If absent, derive from main topics.
2. **Main topics** - Section headings, bold terms, definitions, algorithms.
3. **Examples** - Use for realistic scenarios in questions.

## Question Structure

Generate questions in this order:

1. **True/False** (one per learning objective, or 3-5 if no objectives) 
2. **Explanatory Questions** (3-5 covering main topics)
3. **Coding Question**  (1 algorithm implementation or concept simulation)
4. **Use Case** (1 realistic application)

For each question type, follow guidelines below, and never include answer key.

## Question Guidelines

### Type 1: True/False

Test factual understanding and common misconceptions.

**Coverage**:

- One per learning objective, or 3-5 covering main topics if no objectives

**Difficulty progression**:

- Start with 1-2 simple definitional questions
- Include 2-3 reasoning-based questions requiring concept application or testing relationships between concepts

**Quality criteria**:

- Unambiguous with one correct interpretation
- Clear language without complex nested clauses
- Answer directly found in lecture notes
- Wrong answer reveals common misconception

**Examples**:

- *Easy*: "In supervised learning, the training data includes both input features and their corresponding labels."
- *Medium*: "A model with high training accuracy but low test accuracy is likely underfitting the data."

### Type 2: Explanatory Questions

Test deeper understanding by requiring students to articulate concepts, compare approaches, and explain reasoning.

**Topic selection**:

- Choose 3-5 main topics (key algorithms and their implementations, Advantages/limitations of approaches, Relationships between concepts)
- Avoid repetition: If topic appears in T/F, ask about a *different aspect*

**Question formulations**:

- "Explain..." - requires description in student's words
- "Compare and contrast..." - tests understanding of differences
- "Why does..." - tests causal reasoning
- "What are the advantages/disadvantages..." - tests critical analysis
- "Describe the steps..." - tests procedural knowledge

**Quality criteria**:

- Open-ended but focused
- Cannot be answered with simple yes/no
- Requires 3-5 sentences to answer well

**Examples**:

- "Explain the bias-variance tradeoff. How does increasing model complexity affect bias and variance?"
- "Compare K-Nearest Neighbors and Decision Trees in terms of decision boundaries, training time, and prediction time."

### Type 3: Coding Question

Test practical implementation through code.

**Scope**:

- Implementation of an algorithm discussed in lecture
- Simulation of a concept or process
- Must be achievable with lecture knowledge only
- Should take 15-30 minutes for prepared student

**Required structure**:

1. Clear objective
2. Step-by-step instructions (3-5 steps)
3. Function signature (if applicable)
4. Expected behavior with input/output examples
5. Hints (optional but helpful)

**Language**:

- Python (default) with standard library.
- If using external libraries: NumPy, pandas, matplotlib, scikit-learn.
- Should not require advanced Python features

### Type 4: Use Case Question

Test ability to apply concepts or algorithms explained in lecture notes to realistic scenarios.

**Components**:

1. **Context** - Realistic scenario description
2. **Data description** - What data is available (provide generation code if needed)
3. **Task** - What needs accomplishment
4. **Constraints** (optional) - Time, space, accuracy requirements
5. **Hints** (2-3) - Guidance without giving solution
6. **Libraries** - Can use scikit-learn, pandas, NumPy

**Data generation**: If needed, provide simple, clear code to generate appropriate data.

## Output Format Guidelines

Output format depends on user request (LaTeX, PDF, Markdown, plain text).

**General structure for all formats**:

1. Title with document name
2. Instructions section
3. Part 1: True/False Questions (numbered sequentially)
4. Part 2: Explanatory Questions (numbered sequentially)
5. Part 3: Coding Question (with steps, signature, examples, hints)
6. Part 4: Use Case Application (with scenario, data, task, requirements, hints)

**For specific formats**: For LaTeX and Markdown document structures, use the following templates (in `assets/` folder):
- `questions_template.tex` - Complete LaTeX document structure with formatting
- `markdown_template.md` - Complete Markdown document structure

## Supporting Resources

**References** (in `references/` folder):

- `examples_by_topic.md` - Domain-specific question examples for ML topics (algorithms, preprocessing, evaluation, etc.)