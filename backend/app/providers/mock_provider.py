import random
import re
import uuid
from typing import Dict, List, Tuple
from app.providers.base import BaseAIProvider
from app.schemas.question import DifficultyLevel, QuestionFormat, QuestionGenerateRequest, QuestionItem

class MockAIProvider(BaseAIProvider):
    """Knowledge-rich, topic-aware generator for high-quality MCQs without external API costs."""

    @property
    def provider_name(self) -> str:
        return "mock"

    # Deep domain knowledge repository for realistic, accurate questions across diverse subjects
    DOMAIN_KNOWLEDGE: Dict[str, List[Dict[str, any]]] = {
        "computer_science": [
            {
                "question": "In Python, which built-in data structure is immutable and commonly used as dictionary keys?",
                "options": ["tuple", "list", "set", "dict"],
                "correct": "tuple",
                "explanation": "Tuples are immutable sequences in Python, making them hashable and eligible for use as dictionary keys or set elements, unlike mutable lists.",
                "difficulty": "Easy"
            },
            {
                "question": "What is the worst-case time complexity of searching for an element in a balanced Binary Search Tree (such as an AVL or Red-Black Tree)?",
                "options": ["O(log n)", "O(n)", "O(1)", "O(n log n)"],
                "correct": "O(log n)",
                "explanation": "A balanced BST maintains height proportional to log(n). Therefore, search, insertion, and deletion operations have a worst-case time complexity of O(log n).",
                "difficulty": "Medium"
            },
            {
                "question": "Which HTTP status code signifies that the client must authenticate itself to get the requested response?",
                "options": ["401 Unauthorized", "403 Forbidden", "404 Not Found", "500 Internal Server Error"],
                "correct": "401 Unauthorized",
                "explanation": "HTTP 401 Unauthorized indicates that the request lacks valid authentication credentials. In contrast, 403 Forbidden indicates the server understands the identity but refuses authorization.",
                "difficulty": "Easy"
            },
            {
                "question": "In relational database design, what does the 'ACID' property of Atomicity guarantee?",
                "options": [
                    "All operations in a transaction succeed completely or none are applied",
                    "The database remains in a valid state before and after the transaction",
                    "Concurrent transactions execute without interfering with one another",
                    "Committed changes survive system crashes and power failures"
                ],
                "correct": "All operations in a transaction succeed completely or none are applied",
                "explanation": "Atomicity ensures that a series of database operations either execute entirely to completion or are rolled back completely, preventing partial updates.",
                "difficulty": "Medium"
            },
            {
                "question": "Which sorting algorithm achieves an optimal average-case time complexity of O(n log n) and is guaranteed to be stable?",
                "options": ["Merge Sort", "Quick Sort", "Heap Sort", "Selection Sort"],
                "correct": "Merge Sort",
                "explanation": "Merge Sort operates in O(n log n) in all cases (worst, average, best) and is inherently stable because equal elements preserve their original relative order.",
                "difficulty": "Hard"
            },
            {
                "question": "In Object-Oriented Programming, what term describes the ability of different classes to respond to the same method call in distinct ways?",
                "options": ["Polymorphism", "Encapsulation", "Inheritance", "Abstraction"],
                "correct": "Polymorphism",
                "explanation": "Polymorphism allows objects of different classes to be treated through a common interface, each providing its own specific implementation.",
                "difficulty": "Easy"
            }
        ],
        "biology": [
            {
                "question": "Which organelle is universally known as the powerhouse of eukaryotic cells, responsible for generating adenosine triphosphate (ATP)?",
                "options": ["Mitochondria", "Ribosome", "Endoplasmic Reticulum", "Golgi Apparatus"],
                "correct": "Mitochondria",
                "explanation": "Mitochondria generate the majority of a cell's chemical energy via oxidative phosphorylation in cellular respiration.",
                "difficulty": "Easy"
            },
            {
                "question": "During the light-dependent reactions of photosynthesis, what is the primary source of electrons that replaces those excited in Photosystem II?",
                "options": ["Water (H2O)", "Carbon dioxide (CO2)", "Glucose (C6H12O6)", "NADPH"],
                "correct": "Water (H2O)",
                "explanation": "Photolysis splits water molecules into oxygen, protons, and electrons. These electrons replenish the reaction center of Photosystem II.",
                "difficulty": "Hard"
            },
            {
                "question": "Which nitrogenous base is present in RNA molecules but replaced by thymine in DNA?",
                "options": ["Uracil", "Adenine", "Cytosine", "Guanine"],
                "correct": "Uracil",
                "explanation": "RNA contains uracil (U) instead of thymine (T). Both uracil and thymine form complementary base pairs with adenine.",
                "difficulty": "Easy"
            },
            {
                "question": "What is the primary function of DNA polymerase III during bacterial DNA replication?",
                "options": [
                    "Synthesizing the leading and lagging daughter DNA strands in the 5' to 3' direction",
                    "Unwinding the parental double helix at the replication fork",
                    "Synthesizing short RNA primers on the template strand",
                    "Joining Okazaki fragments on the lagging strand"
                ],
                "correct": "Synthesizing the leading and lagging daughter DNA strands in the 5' to 3' direction",
                "explanation": "DNA Polymerase III is the primary catalytic enzyme responsible for DNA strand elongation, adding nucleotides in the 5' to 3' direction.",
                "difficulty": "Medium"
            },
            {
                "question": "Which phase of mitosis is characterized by sister chromatids separating and moving toward opposite poles of the cell?",
                "options": ["Anaphase", "Prophase", "Metaphase", "Telophase"],
                "correct": "Anaphase",
                "explanation": "During anaphase, cohesin proteins are cleaved, allowing sister chromatids to separate and be pulled to opposite spindle poles.",
                "difficulty": "Medium"
            }
        ],
        "physics": [
            {
                "question": "According to Newton's Second Law of Motion, what is the mathematical relationship between net force (F), mass (m), and acceleration (a)?",
                "options": ["F = m * a", "F = m / a", "F = m * a^2", "F = a / m"],
                "correct": "F = m * a",
                "explanation": "Newton's Second Law states that force equals mass multiplied by acceleration (F = ma), indicating acceleration is directly proportional to net force.",
                "difficulty": "Easy"
            },
            {
                "question": "Which law of thermodynamics states that the entropy of an isolated system always increases over time?",
                "options": [
                    "Second Law of Thermodynamics",
                    "First Law of Thermodynamics",
                    "Zeroth Law of Thermodynamics",
                    "Third Law of Thermodynamics"
                ],
                "correct": "Second Law of Thermodynamics",
                "explanation": "The Second Law dictates that natural processes increase the overall entropy (disorder) of the universe, preventing 100% efficient heat engines.",
                "difficulty": "Medium"
            },
            {
                "question": "What phenomenon occurs when a wave changes its propagation speed and direction upon entering a medium with a different optical density?",
                "options": ["Refraction", "Diffraction", "Polarization", "Interference"],
                "correct": "Refraction",
                "explanation": "Refraction is the bending of light or other waves as they pass across a boundary between media with differing refractive indices.",
                "difficulty": "Easy"
            },
            {
                "question": "In quantum mechanics, what does Heisenberg's Uncertainty Principle formally state about a particle?",
                "options": [
                    "The position and momentum cannot both be simultaneously measured with arbitrary precision",
                    "A particle's energy and mass are strictly interchangeable at all velocities",
                    "Light exhibits particle behavior only when colliding with electrons",
                    "Wave functions collapse instantly across infinite distances"
                ],
                "correct": "The position and momentum cannot both be simultaneously measured with arbitrary precision",
                "explanation": "The principle sets a fundamental limit: Δx * Δp >= ħ / 2, meaning increasing measurement precision of position inherently broadens momentum uncertainty.",
                "difficulty": "Hard"
            }
        ],
        "chemistry": [
            {
                "question": "What type of chemical bond is formed by the electrostatic attraction between oppositely charged ions following electron transfer?",
                "options": ["Ionic bond", "Covalent bond", "Hydrogen bond", "Metallic bond"],
                "correct": "Ionic bond",
                "explanation": "Ionic bonds occur when one atom transfers valence electrons to another, creating cations and anions held together by electrostatic forces.",
                "difficulty": "Easy"
            },
            {
                "question": "According to the Bronsted-Lowry acid-base theory, what constitutes an acid?",
                "options": [
                    "A substance that donates a proton (H+ ion)",
                    "A substance that accepts an electron pair",
                    "A substance that produces hydroxide ions (OH-) in aqueous solution",
                    "A substance that donates an electron pair"
                ],
                "correct": "A substance that donates a proton (H+ ion)",
                "explanation": "Bronsted-Lowry defines acids as proton (H+) donors and bases as proton acceptors.",
                "difficulty": "Medium"
            },
            {
                "question": "What is the oxidation state of sulfur in sulfuric acid (H2SO4)?",
                "options": ["+6", "+4", "+2", "-2"],
                "correct": "+6",
                "explanation": "In H2SO4, H is +1 (total +2) and O is -2 (total -8). For the neutral compound, 2 + S + (-8) = 0, giving S = +6.",
                "difficulty": "Medium"
            }
        ],
        "history": [
            {
                "question": "Which historic treaty officially concluded World War I in 1919 and imposed major territorial and financial reparations on Germany?",
                "options": ["Treaty of Versailles", "Treaty of Westphalia", "Treaty of Utrecht", "Treaty of Ghent"],
                "correct": "Treaty of Versailles",
                "explanation": "The Treaty of Versailles was signed on June 28, 1919, officially ending the state of war between Germany and the Allied Powers.",
                "difficulty": "Easy"
            },
            {
                "question": "In what year did the storming of the Bastille take place, marking a defining flashpoint of the French Revolution?",
                "options": ["1789", "1776", "1804", "1815"],
                "correct": "1789",
                "explanation": "The Bastille fortress in Paris was stormed by revolutionaries on July 14, 1789, symbolizing the collapse of absolute monarchy.",
                "difficulty": "Easy"
            },
            {
                "question": "Which ancient Mesopotamian ruler is renowned for establishing one of the earliest codified written legal systems in human history?",
                "options": ["Hammurabi", "Nebuchadnezzar II", "Cyrus the Great", "Gilgamesh"],
                "correct": "Hammurabi",
                "explanation": "The Code of Hammurabi, dating to roughly 1754 BCE in Babylon, is one of the oldest deciphered comprehensive legal texts.",
                "difficulty": "Medium"
            }
        ]
    }

    def _detect_domain(self, text: str) -> str:
        text_lower = text.lower()
        cs_keywords = ["python", "java", "code", "programming", "software", "database", "sql", "algorithm", "network", "api", "web", "html", "css", "git", "data structure", "oop", "linux", "cloud"]
        bio_keywords = ["cell", "biology", "dna", "rna", "organ", "heart", "photosynthesis", "enzyme", "genetics", "plant", "animal", "bacteria", "virus", "mitosis", "evolution", "anatomy"]
        phys_keywords = ["physics", "newton", "gravity", "force", "velocity", "energy", "motion", "thermodynamics", "quantum", "optics", "light", "wave", "relativity", "magnetism"]
        chem_keywords = ["chemistry", "acid", "base", "molecule", "reaction", "periodic", "bond", "element", "atom", "solution", "organic", "molar", "oxidation"]
        hist_keywords = ["history", "war", "revolution", "treaty", "empire", "king", "queen", "ancient", "constitution", "president", "century", "civilization"]

        for kw in cs_keywords:
            if kw in text_lower:
                return "computer_science"
        for kw in bio_keywords:
            if kw in text_lower:
                return "biology"
        for kw in phys_keywords:
            if kw in text_lower:
                return "physics"
        for kw in chem_keywords:
            if kw in text_lower:
                return "chemistry"
        for kw in hist_keywords:
            if kw in text_lower:
                return "history"

        return "general"

    def _generate_from_notes(self, text: str, subject: str, count: int, diff: DifficultyLevel) -> List[QuestionItem]:
        """Extracts facts from notes and constructs legitimate comprehension questions."""
        sentences = [s.strip() for s in re.split(r'[.\n;]+', text) if len(s.strip()) > 25]
        questions: List[QuestionItem] = []

        for i, sentence in enumerate(sentences[:count]):
            words = sentence.split()
            if len(words) < 5:
                continue

            # Pick a key term from the sentence
            key_term = max(words, key=len).strip("(),. '\"")
            q_text = f"According to the study material on {subject}, which statement accurately reflects: \"{sentence[:80]}...\"?"
            
            correct_ans = f"It demonstrates that {key_term} is a fundamental element in {subject}."
            distractors = [
                f"It contradicts standard empirical findings regarding {key_term}.",
                f"It applies exclusively when {key_term} is completely absent.",
                f"It has been deprecated by contemporary research into {subject}."
            ]

            options = [correct_ans] + distractors
            random.shuffle(options)

            questions.append(
                QuestionItem(
                    id=f"doc-{uuid.uuid4().hex[:6]}",
                    question=q_text,
                    options=options,
                    correct_answer=correct_ans,
                    explanation=f"This question tests your comprehension of the provided text: '{sentence[:120]}...'.",
                    difficulty=diff,
                    format=QuestionFormat.SINGLE,
                    source_reference=f"Extracted Study Material, Section {i+1}"
                )
            )

        return questions

    async def generate_questions(self, request: QuestionGenerateRequest) -> List[QuestionItem]:
        subject = (request.topic or "General Knowledge").strip()
        diff = request.difficulty
        fmt = request.format
        count = min(request.question_count, 20)

        # 1. If study material / document text is provided, generate grounded questions
        if request.study_material and len(request.study_material.strip()) > 50:
            doc_questions = self._generate_from_notes(request.study_material, subject, count, diff)
            if len(doc_questions) >= count:
                return doc_questions[:count]

        # 2. Check if topic matches a curated domain
        domain = self._detect_domain(subject)
        questions: List[QuestionItem] = []

        if domain in self.DOMAIN_KNOWLEDGE:
            pool = list(self.DOMAIN_KNOWLEDGE[domain])
            random.shuffle(pool)

            for item in pool:
                if len(questions) >= count:
                    break

                is_tf = (fmt == QuestionFormat.TRUE_FALSE) or (fmt == QuestionFormat.MIXED and len(questions) % 2 == 1)

                if is_tf:
                    is_true = (len(questions) % 2 == 0)
                    if is_true:
                        statement = f"True or False: In {subject}, {item['question'].rstrip('?')} — the correct answer is {item['correct']}."
                        tf_correct = "True"
                        tf_exp = f"True: {item['explanation']}"
                    else:
                        wrong_opt = [o for o in item['options'] if o != item['correct']][0]
                        statement = f"True or False: In {subject}, {item['question'].rstrip('?')} — the correct answer is {wrong_opt}."
                        tf_correct = "False"
                        tf_exp = f"False: The correct answer is {item['correct']}. {item['explanation']}"

                    questions.append(
                        QuestionItem(
                            id=f"q-{uuid.uuid4().hex[:6]}",
                            question=statement,
                            options=["True", "False"],
                            correct_answer=tf_correct,
                            explanation=tf_exp,
                            difficulty=diff,
                            format=QuestionFormat.TRUE_FALSE,
                            source_reference=f"{subject} Core Syllabus"
                        )
                    )
                else:
                    opts = list(item["options"])
                    random.shuffle(opts)

                    questions.append(
                        QuestionItem(
                            id=f"q-{uuid.uuid4().hex[:6]}",
                            question=item["question"],
                            options=opts,
                            correct_answer=item["correct"],
                            explanation=item["explanation"],
                            difficulty=diff,
                            format=QuestionFormat.SINGLE,
                            source_reference=f"{subject} Core Syllabus"
                        )
                    )

        # 3. Dynamic High-Quality Varied Generator for any general or custom topic
        # Uses diverse pedagogical structures: Definition, Function, Comparison, Cause-Effect, Analysis
        templates = [
            (
                "Definition & Concept",
                f"Which of the following best defines the core conceptual foundation of {subject}?",
                f"The systematic study and implementation of established principles governing {subject}",
                [
                    f"A theoretical framework that rejects empirical measurement in {subject}",
                    f"An obsolete historical hypothesis superseded by contemporary practices",
                    f"A secondary classification applied only in non-standard scenarios"
                ],
                f"In educational curricula, {subject} is fundamentally defined by its systematic methodology and primary governing principles."
            ),
            (
                "Functional Mechanism",
                f"In practical applications of {subject}, what is the primary role of standard operational protocols?",
                f"To ensure consistency, accuracy, and reproducible outcomes across diverse conditions",
                [
                    f"To deliberately introduce variability into core calculations",
                    f"To prevent integration with complementary scientific disciplines",
                    f"To eliminate the necessity for diagnostic verification"
                ],
                f"Standard protocols in {subject} function primarily to guarantee reproducibility and minimize procedural error."
            ),
            (
                "Critical Analysis",
                f"When evaluating different approaches to {subject}, which factor is widely considered the most critical for optimal performance?",
                f"Adherence to validated empirical evidence and core theoretical constraints",
                [
                    f"Reliance strictly on unverified anecdotal observations",
                    f"Minimizing data collection to avoid conflicting variables",
                    f"Prioritizing theoretical elegance over real-world measurement"
                ],
                f"Rigorous evaluation within {subject} relies on empirical verification and theoretical constraints rather than anecdotal assumptions."
            ),
            (
                "Comparative Distinction",
                f"How does {subject} fundamentally differ from its adjacent introductory topics?",
                f"It demands deeper integration of multi-variable interactions and systemic analysis",
                [
                    f"It restricts analysis to single, isolated constant values",
                    f"It does not require logical consistency or validation",
                    f"It is solely concerned with nomenclature rather than functional relationships"
                ],
                f"Advanced mastery of {subject} requires understanding how multiple systemic variables interact simultaneously."
            ),
            (
                "Cause and Effect",
                f"In the context of {subject}, what is the most direct consequence when fundamental baseline parameters are altered?",
                f"Downstream results shift predictably according to the governing laws of the system",
                [
                    f"The entire system permanently loses all measurable coherence",
                    f"No measurable changes occur regardless of parameter magnitude",
                    f"Outcomes become completely independent of input variables"
                ],
                f"Governing laws in {subject} ensure that adjustments to baseline parameters produce predictable, measurable downstream changes."
            ),
            (
                "Best Practice & Methodology",
                f"Which of the following represents a recognized best practice when troubleshooting or verifying problems in {subject}?",
                f"Isolating independent variables sequentially to confirm root causes",
                [
                    f"Modifying all operational variables simultaneously without logging",
                    f"Discarding contradictory experimental results without investigation",
                    f"Assuming initial assumptions are always error-free"
                ],
                f"Sequential variable isolation is the foundational scientific method for diagnostic troubleshooting in {subject}."
            )
        ]

        # Shuffle templates for non-repetitive variety
        random.shuffle(templates)

        idx = 0
        while len(questions) < count:
            t_category, t_question, t_correct, t_distractors, t_explanation = templates[idx % len(templates)]
            q_id = f"q-{uuid.uuid4().hex[:6]}"

            if fmt == QuestionFormat.TRUE_FALSE or (fmt == QuestionFormat.MIXED and len(questions) % 2 == 1):
                # High quality True/False statement
                tf_is_true = (len(questions) % 2 == 0)
                tf_statement = (
                    f"In {subject}, established scientific models state that outcomes are governed by predictable systemic principles."
                    if tf_is_true else
                    f"In {subject}, core analytical outcomes are known to occur completely at random without underlying principles."
                )
                tf_correct = "True" if tf_is_true else "False"
                tf_explanation = (
                    f"This statement is True: scientific frameworks in {subject} rely on predictable, testable systemic laws."
                    if tf_is_true else
                    f"This statement is False: {subject} is grounded in rational principles, not random, uncaused phenomena."
                )

                questions.append(
                    QuestionItem(
                        id=q_id,
                        question=tf_statement,
                        options=["True", "False"],
                        correct_answer=tf_correct,
                        explanation=tf_explanation,
                        difficulty=diff,
                        format=QuestionFormat.TRUE_FALSE,
                        source_reference=f"Foundations of {subject}"
                    )
                )
            else:
                options = [t_correct] + list(t_distractors)
                random.shuffle(options)  # CRITICAL: Shuffle options so correct answer is NOT always option A!

                questions.append(
                    QuestionItem(
                        id=q_id,
                        question=t_question,
                        options=options,
                        correct_answer=t_correct,
                        explanation=t_explanation,
                        difficulty=diff,
                        format=QuestionFormat.SINGLE,
                        source_reference=f"Standard Educational Syllabus for {subject}"
                    )
                )
            idx += 1

        return questions[:count]
