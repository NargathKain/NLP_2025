# NLP 2025 
# Η συνάρτηση main καλεί όλα τα υπόλοιπα αρχεία και 
# φορτώνει τις προτάσεις με αρχείο, καλεί τις συναρτήσεις
# παρουσιάζει τα αποτελέσματα 

import os
import sys
from src.preprocessing import preprocess_pipeline
from src.syntactic_analysis import syntactic_analysis_pipeline

# Paths
BASE_DIR = "data"
RAW_DIR = os.path.join(BASE_DIR, "raw")
PREPROCESSED_DIR = os.path.join(BASE_DIR, "preprocessed")

# Input files
SENTENCE1_FILE = os.path.join(RAW_DIR, "sentence1.txt")
SENTENCE2_FILE = os.path.join(RAW_DIR, "sentence2.txt")

# ============================== FILE I/O FUNCTIONS ==============================

def load_sentence_from_file(filepath):
    # Φόρτωση προτάσεων από αρχείο
    # Args: filepath (str): Path του αρχείου
    # Επιστρέφει string με το κείμενο - FileNotFoundError: αν το αρχείο δεν υπάρχιε
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"File not found: {filepath}\n"
            f"Please create the file with your sentence."
        )
    with open(filepath, 'r', encoding='utf-8') as f:
        sentence = f.read().strip()
    return sentence

# ============================== MAIN EXECUTION FUNCTION ==============================

def run_deliverable_1a():    
    print("\n" + "█"*80)
    print("NLP ASSIGNMENT 2025 - DELIVERABLE 1A")
    print("Custom Pipeline")
    print("█"*80 + "\n")
    
    # Create directories if they don't exist
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PREPROCESSED_DIR, exist_ok=True)
    
    try:
        # ===== LOAD SENTENCES =====
        sentence1 = load_sentence_from_file(SENTENCE1_FILE)
        sentence2 = load_sentence_from_file(SENTENCE2_FILE)
        print(f"Loaded Sentence 1 from: {SENTENCE1_FILE}")
        print(f"Loaded Sentence 2 from: {SENTENCE2_FILE}")
        
        # ===== PROCESS SENTENCE 1 =====
        #Preprocessing for Sentence 1
        print("\n" + "▼"*80)
        print("Sentence 1: Preprocessing \n")
        
        preprocess_results1 = preprocess_pipeline(sentence1, verbose=True)
        
        print("\n" + "="*80)
        print(f"✓ Sentence 1 preprocessing complete: "
              f"{len(preprocess_results1['lemmatized_tokens'])} tokens")
        print("="*80)

        # Syntactic Analysis for Sentence 1
        print("\n" + "▼"*80)
        print("Sentence 1: Syntactic Reconstruction \n")
        
        syntax_results1 = syntactic_analysis_pipeline(preprocess_results1['pos_tags'], verbose=True)
        
        print("\n" + "="*80)
        print("✓ Sentence 1 syntactic reconstruction complete")
        print("="*80)

        
        
        # ===== PROCESS SENTENCE 2 =====
        #Preprocessing for Sentence 2
        print("\n" + "▼"*80)
        print("Sentence 2: Preprocessing \n")
        
        preprocess_results2  = preprocess_pipeline(sentence2, verbose=True)

        print("\n" + "="*80)
        print(f"✓ Sentence 2 preprocessing complete: "
              f"{len(preprocess_results2['lemmatized_tokens'])} tokens")
        print("="*80)

        #Syntactic Analysis for Sentence 2
        print("\n" + "="*80)
        print("Sentence 2: Syntactic Reconstruction \n")
        
        syntax_results2 = syntactic_analysis_pipeline(preprocess_results2['pos_tags'], verbose=True)
        
        print("\n" + "="*80)
        print("✓ Sentence 2 syntactic reconstruction complete")
        print("="*80)

        
        # ===== Summary =====
        print("\n" + "█"*35 + " SUMMARY  " + "█"*35)
        
        print("\n SENTENCE 1:")
        print(f"  Original:      {syntax_results1['original']}")
        print(f"  Reconstructed: {syntax_results1['reconstructed']}")
        
        print("\n SENTENCE 2:")
        print(f"  Original:      {syntax_results2['original']}")
        print(f"  Reconstructed: {syntax_results2['reconstructed']}")
        
        print("\n" + "█"*30 + " Process  Completed " + "█"*30)
        
        # results1, results2
        return {
            'sentence1': {
                'preprocessing': preprocess_results1,
                'syntactic': syntax_results1
            },
            'sentence2': {
                'preprocessing': preprocess_results2,
                'syntactic': syntax_results2
            }
        }
        
    except FileNotFoundError as e:
        print(f"\n ======= Error: {e} =======")
        print("\nPlease create the following files:")
        print(f"  1. {SENTENCE1_FILE}")
        print(f"  2. {SENTENCE2_FILE}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n ======= Unexpected error: {e} =======")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# ============================== ENTRY POINT ==============================
if __name__ == "__main__":
    # Run preprocessing for Deliverable 1A
    results = run_deliverable_1a()
    
    # Optional: Save results for next steps
    # You can access:
    # - results1['lemmatized_tokens']
    # - results2['lemmatized_tokens']
    # And pass them to syntactic analysis module

# ```
# I didn't see that part final yet, or maybe I missed, I apologize if so.