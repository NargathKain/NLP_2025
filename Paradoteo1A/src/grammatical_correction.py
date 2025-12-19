import re

# ============================== STEP 1: SPELLING CORRECTION ==============================

def apply_spelling_correction(text):
    # απλή ορθογραφική διόρθωση με χρήση dictionary.
    # αντικατάσταση από προκαθορισμένο dictionary
    
    # Dictionary με κοινά ορθογραφικά → σωστές φόρμες (έχει μόνο πολύ συνηθισμένα λάθη)
    spelling_corrections = {
        # συχνά typos
        r'\brecieve\b': 'receive',
        r'\boccured\b': 'occurred',
        r'\bseperate\b': 'separate',
        r'\bdefinately\b': 'definitely',
        r'\bwierd\b': 'weird',
        r'\bneccessary\b': 'necessary',
        r'\boccasion\b': 'occasion',
        r'\bpublically\b': 'publicly',
        r'\bthier\b': 'their',
        r'\bbeleive\b': 'believe',
        r'\bbeggining\b': 'beginning',
        r'\bcommited\b': 'committed',
        r'\bexistance\b': 'existence',
        r'\bconsious\b': 'conscious',
        r'\bfourty\b': 'forty',
        r'\buntill\b': 'until',
        
        # συντομεύσεις χωρίς απόστροφο
        r'\bcant\b': "can't",
        r'\bdont\b': "don't",
        r'\bdidnt\b': "didn't",
        r'\bisnt\b': "isn't",
        r'\barent\b': "aren't",
        r'\bwasnt\b': "wasn't",
        r'\bwerent\b': "weren't",
        r'\bhasnt\b': "hasn't",
        r'\bhavent\b': "haven't",
        r'\bhadnt\b': "hadn't",
        r'\bwont\b': "won't",
        r'\bwouldnt\b': "wouldn't",
        r'\bshouldnt\b': "shouldn't",
        r'\bcouldnt\b': "couldn't",
        
        # πιο συγκεκριμένα
        r'\balot\b': 'a lot',
        r'\btheir are\b': 'there are',
        r'\byour welcome\b': "you're welcome",
    }
    
    corrected_text = text
    for pattern, replacement in spelling_corrections.items():
        corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
    
    return corrected_text

# ============================== STEP 2: SURFACE GRAMMAR RULES ==============================

def apply_surface_grammar_rules(text, pos_tags):
    # Επιφανειακοί γραμματικοί κανόνες
    # χρήση POS tags για αφαίρεση επιθέτων, καθαρισμό διπλών προσδιοριστικών, επαναλαμβανόμενων tokens
    # Δεν δημιουργούνται νέες ετικέτες, εφαρμόζονται οι κανόνες μόνο αν POS tags παρέχονται από προηγούμενο στάδιο επεξεργασίας
    # Δεν έχουμε: Deep syntax, dependency parsing, subject-verb agreement, POS generation
    # Δέχεται κείμενο και POS tags από προηγούμενη επεξεργασία και το επιστρέφει καθαρισμένο
    # Πληροφορίες: Natural Language Processing Recipes - Chapter 4 (Grammatical Normalization)    
    
    # Αν δεν υπάρχουν POS tags, χρησιμοποίησε μόνο καθαρισμένο σε επίπεδο συμβολοσειράς
    if pos_tags is None or len(pos_tags) == 0:
        return apply_string_level_cleanup(text)
    
    tokens = pos_tags
    cleaned_tokens = []
    i = 0
    
    while i < len(tokens):
        word, pos = tokens[i]
        
        # Rule 1: αφαίρεση διπλών προσδιορισμών (the the, a a)
        if pos == 'DT' and i + 1 < len(tokens):
            next_word, next_pos = tokens[i + 1]
            if next_pos == 'DT' and word.lower() == next_word.lower():
                # παράλειψη διπλότυπου προσδιοριστή
                i += 1
                continue
        
        # Rule 2: αφαίρεση "ορφανών" επιθέτων στο τέλος (επίθετο που δεν ακολουθείται από ουσιαστικό)
        if pos in ['JJ', 'JJR', 'JJS'] and i == len(tokens) - 1:
            i += 1 # τελευταία λέξη επίθετο -> αφαίρεση
            continue
        
        # Rule 3: επιφανειακός έλεγχος για διπλότυπες λέξεις
        if i + 1 < len(tokens):
            next_word, _ = tokens[i + 1]
            if word.lower() == next_word.lower():
                cleaned_tokens.append(word) # Διπλύτυπη λέξη -> διατήρηση μιας
                i += 2
                continue
        
        # Rule 4: αφαίρεση ορφανών προσδιοριστών στο τέλος
        if pos == 'DT' and i == len(tokens) - 1:
            i += 1 # προσδιοριστική τελευταία λέξη -> αφαίρεση
            continue
        
        # Rule 5: αφαίρεση υπερβολικών διαδοχικών επιθέτων (σφάλμα ανακατασκευής)
        if pos in ['JJ', 'JJR', 'JJS']:
            adj_count = 1
            j = i + 1
            while j < len(tokens) and tokens[j][1] in ['JJ', 'JJR', 'JJS']:
                adj_count += 1
                j += 1
            
            if adj_count > 3: # If >3 διαδοχικά επίθετα, κράτα 2
                i += adj_count - 2
                continue

        # Rule 6: Remove orphan prepositions at end
        if pos == 'IN' and i == len(tokens) - 1:
            # Last word is preposition → remove
            i += 1
            continue
        
        # Rule 7: Remove consecutive prepositions (in to with → keep first)
        if pos == 'IN' and i + 1 < len(tokens):
            next_word, next_pos = tokens[i + 1]
            if next_pos == 'IN':
                # Two prepositions in a row → skip second
                cleaned_tokens.append(word)
                i += 2
                continue
        
        cleaned_tokens.append(word)
        i += 1
    
    result = ' '.join(cleaned_tokens) # Ανακατασκευή κειμένου
    
    return result


def apply_string_level_cleanup(text):
    # Εφαρμογή καθαρισμού στην συμβολοσειρά, χωρίς POS tags    
    # Συντηρητικοί κανόνες που δεν απαιτούν συντακτική ανάλυση
    
    # Αφαίρεση διπ΄λότυπων (λέξη λέξη -> λέξη)
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    
    # αφαίρεση τριπλών + επαναλαμβανόμενων τροποποιητών
    text = re.sub(r'\b(very|really|so)\s+\1\s+\1\b', 
                  r'\1', text, flags=re.IGNORECASE)
    
    return text
    
# ============================== STEP 3: POST-PROCESSING ==============================

def apply_post_processing(text):    
    # Εφαρμογή βασικής μορφοποίησης κειμένου 
    # χρήση κανόνων μορφοποίησης κειμένου: Πρώτο γράμμα κεφαλαίο, προσθήκη τελείας στο τέλος, 
    # καθαρισμός κενών και βασική στίξη  
    
    if not text:
        return text
    
    text = re.sub(r'\s+', ' ', text.strip()) # αφαίρεση επιπλέων κενών (αν και ήδη έχει γίνει 3 φο΄ρες)
    
    # Διόρθωση κενών γύρω από τα σημεία στίξης και αφαίρεση τους πριν 
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    # προσθήκη κενού μετά τα σημεία στίξης αν λείπει
    text = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', text)
    
    # Πρώτο γράμμα κεφαλαίο
    if text: text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    # πρόσθεσε τελεία αν λείπει και δενμ υπάρχει άλλο σημείο στίξης
    if text and text[-1] not in '.!?': text += '.'
    
    # Διόρθωση πολλαπλών σημείων στίξης
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'!{2,}', '!', text)
    text = re.sub(r'\?{2,}', '?', text)
    
    # Καθαρισμός ειδικών χαρακτήρων
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    
    return text

# ============================== STEP 4: PRINT FUNCTIONS ==============================

def print_correction_step(step_number, step_name, content):
    # εκτύπωση βήματος με μορφοποίηση
    # δέχεται step_number, όνομα βήματος, περιεχόμενο προς εμφάνιση
    print(f"\n[Step {step_number}] {step_name}")
    print("-" * 80)
    
    if isinstance(content, str):
        print(content)
    elif isinstance(content, dict):
        for key, value in content.items():
            print(f"  {key}: {value}")
    else:
        print(content)

# =========== STEP 0.5: Επιπλέον προσθήκη POS tags στο reconstructed text ================
def retag_reconstructed_text(reconstructed_text):
    # Προσθήκη ετικετών POS στο νέο string η συνατκτική ανακατασκεύη αναδιατάσσει το κείμενο άρα οι ετικέτες του pre-processing δεν ταιριάζουν εδώ
    # δέχεται reconstructed_text(string) -> επιστρέφει New POS tags [(token, tag), ...]
    from nltk.tokenize import word_tokenize
    from nltk import pos_tag
    
    # Tokenize and tag the reconstructed text
    tokens = word_tokenize(reconstructed_text)
    new_pos_tags = pos_tag(tokens)
    
    return new_pos_tags

# ============================== MAIN GRAMMATICAL CORRECTION PIPELINE ==============================

def grammatical_correction_pipeline(text, verbose):
    # Διαδικασία γραμματικής διόρθωσης. Κάνει σε σειρά τα εξής:
    # 1. Διόρθωση ορθογραφίας
    # 2. εφαρμογή επιφανειακών γραμματικών κανόνων
    # 3. post-processing 
    # Δέχεται κείμενο, ετικέτες και το οκευ για να τυπώσει τα βήματα

    # Based on: Natural Language Processing Recipes

    if not text or not text.strip(): return text
    
    if verbose:
        print("\n" + "="*80)
        print("GRAMMATICAL CORRECTION & SMOOTHING")
        print("="*80)
        print_correction_step(0, "Input (Reconstructed Sentence)", text)

    # Step 0.5: προσθήκη νέων ετικετών στο reconstructed
    pos_tags = retag_reconstructed_text(text)
    if verbose: print_correction_step(0.5,"Re-tagged for Grammar Rules", f"{len(pos_tags)} POS tags: {pos_tags[:5]}..." )

    # Step 1: διόρθωση ορθογραφικών
    corrected = apply_spelling_correction(text)
    if verbose:
        changes = "Changes applied" if corrected != text else "No changes"
        print_correction_step(1, "After Spelling Correction", f"{corrected}\n({changes})")
    
    # Step 2: επιφανειακοί γραμματικοί κανόνες
    before_grammar = corrected
    corrected = apply_surface_grammar_rules(corrected, pos_tags)
    if verbose:
        changes = "Changes applied" if corrected != before_grammar else "No changes"
        print_correction_step(2, "After Surface Grammar Rules", f"{corrected}\n({changes})")
    
    # Step 3: Post-processing
    before_post = corrected
    corrected = apply_post_processing(corrected)
    if verbose:
        changes = "Changes applied" if corrected != before_post else "No changes"
        print_correction_step(3, "After Post-processing (FINAL)", f"{corrected}\n({changes})")
    
    if verbose:
        print("\n" + "="*80)
        print("✓ Grammatical correction complete")
        print("="*80)
    
    return corrected

def grammatical_correction_simple(text, pos_tags): # απλοποιημένη γραμματική διόρθωση
    return grammatical_correction_pipeline(text, pos_tags, verbose=False)