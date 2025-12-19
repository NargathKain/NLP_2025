# NLP assignment - paradoteo1b
import os
import sys
import subprocess
from src.pipeline_textblob_1.pipeline_1 import pipeline_textblob_1_main
from src.pipeline_embeddings_2.pipeline_2 import pipeline_embeddings_2_main
from src.pipeline_transformer_3.pipeline_3 import pipeline_transformer_3_main

# ============================== FILE PATHS ==============================
# Directories
BASE_DIR = "data"
RAW_DIR = os.path.join(BASE_DIR, "raw")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Input Files
TEXT1_FILE = os.path.join(RAW_DIR, "text1.txt")
TEXT2_FILE = os.path.join(RAW_DIR, "text2.txt")

# Output / Result directories
PIPELINE1_DIR = os.path.join(RESULTS_DIR, "pipeline_1_data")
PIPELINE2_DIR = os.path.join(RESULTS_DIR, "pipeline_2_data")
PIPELINE3_DIR = os.path.join(RESULTS_DIR, "pipeline_3_data")

# ============================== FILE I/O FUNCTIONS ==============================
def load_text_from_file(filepath): # Φόρτωση κειμένου από αρχείο 
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}") 
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    return text

def save_result(result_text, output_path): # Αποθήκευση κειμένου σε αρχείο
    with open(output_path, 'w', encoding='utf-8') as f: 
        f.write(result_text)

# προαιρετική συνάρτηση για εμφάνιση νέας κονσόλας - δεν δουλεύει
# def run_pipeline_in_new_console(script_path, text_file):
#     # Ανοίγει νέα κονσόλα και εκτελεί pipeline
#     if sys.platform == "win32":# Windows
#         subprocess.Popen(['start', 'cmd', '/k', 'python', script_path, text_file], shell=True)
#     elif sys.platform == "darwin":# macOS
#         subprocess.Popen(['open', '-a', 'Terminal', 'python', script_path, text_file])
#     else: # Linux
#         subprocess.Popen(['gnome-terminal', '--', 'python3', script_path, text_file])


# ============================== MAIN FUNCTION ==============================
def run_deliverable_1b():

    print("\n" + "="*82)
    print("                        NLP ASSIGNMENT 2025 - DELIVERABLE 1B                      ")
    print("="*82 + "\n")

    # Δημιουργία φακέλων
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PIPELINE1_DIR, exist_ok=True)
    os.makedirs(PIPELINE2_DIR, exist_ok=True)
    os.makedirs(PIPELINE3_DIR, exist_ok=True)
    
    try:
        # ΦΟΡΤΩΣΗ ΚΕΙΜΕΝΩΝ 
        text1 = load_text_from_file(TEXT1_FILE)
        text2 = load_text_from_file(TEXT2_FILE)
        print("[ Step 1 ] Load input texts")
        
        # PIPELINE 1: TextBlob --------       
        print("[ Step 2 ] Running Pipeline 1 (TextBlob)...")
        result1_text1 = pipeline_textblob_1_main(text1)
        save_result(result1_text1, os.path.join(PIPELINE1_DIR, "pipeline1_result_text1.txt"))
        
        result1_text2 = pipeline_textblob_1_main(text2)
        save_result(result1_text2, os.path.join(PIPELINE1_DIR, "pipeline1_result_text2.txt"))
        input("Press Enter to continue...")
        # εμφάνιση νέας κονσόλας 
        # run_pipeline_in_new_console('src/pipeline_textblob_1/filename.py', TEXT1_FILE)

        
        # PIPELINE 2: Embeddings --------        
        print("[ Step 3 ] Running Pipeline 2 (Embeddings)...")
        result2_text1 = pipeline_embeddings_2_main(text1)
        save_result(result2_text1, os.path.join(PIPELINE2_DIR, "pipeline2_result_text1.txt"))
        
        result2_text2 = pipeline_embeddings_2_main(text2)
        save_result(result2_text2, os.path.join(PIPELINE2_DIR, "pipeline2_result_text2.txt"))
        
        input("Press Enter to continue...")
        # εμφάνιση νέας κονσόλας
        # run_pipeline_in_new_console('src/pipeline_embeddings_2/filename.py', TEXT1_FILE)

        
        # PIPELINE 3: Transformer         
        print("[ Step 4 ] Running Pipeline 3 (Transformer)...")
        result3_text1 = pipeline_transformer_3_main(text1)
        save_result(result3_text1, os.path.join(PIPELINE3_DIR, "pipeline3_result_text1.txt"))
        
        result3_text2 = pipeline_transformer_3_main(text2)
        save_result(result3_text2, os.path.join(PIPELINE3_DIR, "pipeline3_result_text2.txt"))
        
        input("Press Enter to continue...")
        # εμφάνιση νέας κονσόλας
        # run_pipeline_in_new_console('src/pipeline_transformer_3/filename.py', TEXT1_FILE)

        
        # ΤΕΛΟΣ 
        print("="*82)
        print("✓ All pipelines completed successfully!")
        print(f"✓ Results saved in: {RESULTS_DIR}/")
        print("="*82 + "\n")

    except FileNotFoundError as e:
        print(f"\n =======     Error: {e}       =======")
        print("\nPlease create the following files:")
        print(f"  1. {TEXT1_FILE}")
        print(f"  2. {TEXT2_FILE}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n ======= Unexpected error: {e} =======")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_deliverable_1b()

