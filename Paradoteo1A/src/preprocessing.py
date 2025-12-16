# NLP 2025 - Preprocessing 
# Module που παρέχει τις συναρτήσεις για το preprocessing 
# Όλες οι συναρτήσεις έχουν σχεδιαστεί ώστε το αρχείο να γίνει imported στη main.py

import re
import string
import contractions
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# HELPER FUNCTIONS
# βοηθητικές συναρτήσεις / βήματα του preprocessing

def expand_contractions(text):
    # Ανάπτυξη των συντομευμένων λέξεων στην πλήρη μορφή τους με τη χρήση της contractions library
    # Επιστρέφει string με το κείμενο - Παράδειγμα "I didn't see it" -> "I did not see it"
    return contractions.fix(text)


def apply_lowercasing(text):
    # Μετατροπή κειμένου σε πεζά 
    return text.lower()


def remove_punctuation_and_special_chars(text):
    # Αφαίρεση σημείων στίξης - Επιστρέφει το κείμενο χωρίς σημεία στίξης και ειδικούς χαρακτήρες
    
    # Special characters to remove
    special_chars = '—…''""'
    
    # Remove standard punctuation
    for char in string.punctuation:
        text = text.replace(char, ' ')
    
    # Remove special characters
    for char in special_chars:
        text = text.replace(char, ' ')
    
    return text


def clean_whitespace(text):
    # Αφαίρεση επιπλέων κενών που προέκυψαν από remove_punctuation
    # Επιστρέφει κείμενο με κανονικοποιημένα κενά / αντικαθιστά τα διπλά με ένα
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def tokenize_text(text):
    # Tokenization με NLTK - Επιστρέφει λίστα με tokens
    tokens = word_tokenize(text)
    return tokens


def get_wordnet_pos(treebank_tag):
    # Μετατροπή Treebank POS tag σε WordNet POS tag
    # δέχεται: treebank_tag (str): POS tag from NLTK's pos_tag
    # επιστρέφει: str: WordNet POS tag
    
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def apply_pos_tagging(tokens):
    # Apply Part-of-Speech tagging to tokens.
    # Args: tokens (list): List of tokens
    # Returns: list: List of (token, pos_tag) tuples
    pos_tags = pos_tag(tokens)
    return pos_tags


def apply_lemmatization(pos_tags):
    # Apply lemmatization to tokens using POS tags.
    # Args: pos_tags (list): List of (token, pos_tag) tuples
    # Returns: list: List of lemmatized tokens
    lemmatizer = WordNetLemmatizer()
    
    lemmatized_tokens = [
        lemmatizer.lemmatize(word, get_wordnet_pos(tag))
        for word, tag in pos_tags
    ]
    
    return lemmatized_tokens

# PRINT STEPS 

def print_step(step_number, step_name, content):
    # Print a preprocessing step with formatting.
    # Args:
    #     step_number (int): Step number
    #     step_name (str): Name of the step
    #     content: Content to display (str or list)
    #     max_length (int): Maximum line length for display
    print(f"\n[Step {step_number}] {step_name}")
    print("-" * 80)
    
    if isinstance(content, str):
        print(content) #εμφάνιση ολόκληρου string
    elif isinstance(content, list):
        # Display list with length info
        print(f"Tokens ({len(content)}): {content}")
    else:
        print(content)


# MAIN PREPROCESSING PIPELINE

def preprocess_pipeline(text, verbose=True):
    """
    Complete preprocessing pipeline.
    Returns intermediate results for debugging/visualization.
    
    Args:
        text (str): Input text
        verbose (bool): If True, print each step
        
    Returns:
        dict: Dictionary containing:
            - 'original': Original text
            - 'after_contractions': After expanding contractions
            - 'after_lowercasing': After lowercasing
            - 'after_punctuation': After removing punctuation
            - 'after_whitespace': After cleaning whitespace
            - 'tokens': After tokenization
            - 'pos_tags': After POS tagging
            - 'lemmatized_tokens': Final lemmatized tokens
    """
    results = {}
    
    # Store original
    results['original'] = text
    if verbose: print_step(0, "Original Text", text)
    
    # Step 1: Expand contractions
    text = expand_contractions(text)
    results['after_contractions'] = text
    if verbose: print_step(1, "After Expanding Contractions", text)
    
    # Step 2: Lowercasing
    text = apply_lowercasing(text)
    results['after_lowercasing'] = text
    if verbose: print_step(2, "After Lowercasing", text)
    
    # Step 3: Remove punctuation and special characters
    text = remove_punctuation_and_special_chars(text)
    results['after_punctuation'] = text
    if verbose: print_step(3, "After Removing Punctuation", text)
    
    # Step 4: Clean whitespace
    text = clean_whitespace(text)
    results['after_whitespace'] = text
    if verbose: print_step(4, "After Cleaning Whitespace", text)
    
    # Step 5: Tokenization
    tokens = tokenize_text(text)
    results['tokens'] = tokens
    if verbose: print_step(5, "After Tokenization", tokens)
    
    # Step 6: POS tagging
    pos_tags = apply_pos_tagging(tokens)
    results['pos_tags'] = pos_tags
    if verbose:
        print_step(6, "After POS Tagging", pos_tags[:10])
        if len(pos_tags) > 10:
            print(f"... and {len(pos_tags) - 10} more")
    
    # Step 7: Lemmatization
    lemmatized_tokens = apply_lemmatization(pos_tags)
    results['lemmatized_tokens'] = lemmatized_tokens
    if verbose: print_step(7, "After Lemmatization (FINAL)", lemmatized_tokens)
    
    return results


def preprocess_simple(text):
    # Simplified preprocessing that returns only final tokens.
    # Args: text (str): Input text
    # Returns: list: Final lemmatized tokens
    return preprocess_pipeline(text)['lemmatized_tokens']