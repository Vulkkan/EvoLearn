import spacy
import random
import pdfplumber
from collections import Counter
import os
import nltk
from nltk.corpus import wordnet

from typing import List, Tuple
# nltk.download('wordnet')


def extract_pdf_text(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonym = lemma.name().replace('_', ' ')
            if synonym != word:
                synonyms.add(synonym)
    return list(synonyms)



def generate_mcqs(text: str, num_questions: int = 20) -> List[Tuple[str, List[str], str]]:
    """
    Generate multiple-choice questions (MCQs) from a given text.

    Parameters:
    -----------
    text : str
        The input text from which to generate questions.
    num_questions : int, optional
        The number of MCQs to generate. Default is 20.

    Returns:
    --------
    List[Tuple[str, List[str], str]]
        A list of tuples, each containing:
        - question_stem (str): The sentence with a blank in place of a noun.
        - answer_choices (List[str]): A list of four choices including the correct noun.
        - correct_answer (str): The letter (A, B, C, or D) corresponding to the correct answer.
    """
    
    if text is None:
        return []

    # Load spaCy English model
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    # Filter sentences: must be long enough and not contain digits
    sentences = [
        sent.text.strip() for sent in doc.sents
        if len(sent.text.strip()) > 15 and not any(char.isdigit() for char in sent.text.strip())
    ]

    generated_questions = set()
    mcqs = []

    while len(mcqs) < num_questions:
        sentence = random.choice(sentences)

        # Skip very long sentences
        if len(sentence) > 200:
            continue

        sent_doc = nlp(sentence)

        # Extract nouns and proper nouns as possible answer candidates
        nouns = [token.text for token in sent_doc if token.pos_ in ["NOUN", "PROPN"]]

        if len(nouns) < 1:
            continue

        subject = random.choice(nouns)
        question_stem = sentence.replace(subject, "_______", 1)

        # Avoid generating duplicate questions
        if (question_stem, subject) in generated_questions:
            continue

        answer_choices = [subject]

        # Generate distractors from synonyms and similar words
        synonyms = get_synonyms(subject)
        similar_words = [
            token.text for token in nlp.vocab
            if token.is_alpha and token.has_vector and token.is_lower
            and token.similarity(nlp(subject)) > 0.5
        ][:3]

        distractors = list(set(synonyms + similar_words))
        distractors = [d for d in distractors if d.lower() != subject.lower()]

        # Add fallback distractors from the text if needed
        while len(distractors) < 3:
            candidates = [
                token.text for token in nlp(text)
                if token.pos_ in ["NOUN", "PROPN"]
                and token.text.lower() != subject.lower()
                and token.text.lower() not in [d.lower() for d in distractors]
            ]
            if not candidates:
                break
            new_distractor = random.choice(candidates)
            distractors.append(new_distractor)

        # Add 3 distractors to the answer choices
        if len(distractors) < 3:
            continue

        answer_choices.extend(random.sample(distractors, 3))
        random.shuffle(answer_choices)

        # Discard trivial answers (e.g., single letters)
        if all(len(option) <= 1 for option in answer_choices):
            continue

        # Discard if choices are too similar (identical)
        if len(set(choice.lower() for choice in answer_choices)) < 4:
            continue

        # Identify correct answer letter (A, B, C, or D)
        correct_answer = chr(65 + answer_choices.index(subject))  # A=65

        mcqs.append((question_stem, answer_choices, correct_answer))
        generated_questions.add((question_stem, subject))

    return mcqs
