import re

# ============================== STEP 1: SPELLING CORRECTION ==============================
 

def apply_spelling_correction(text):
    # Apply simple spelling correction using dictionary.
    
    # METHOD: Rule-based replacement from predefined dictionary
    # NOT: Language models, context-aware correction
    
    # Δέχεται κείμενο και το επιστρέφει διορθωμένο
    
    # Dictionary of common spelling errors → correct forms
    # Only very common and certain typos (not context-dependent)
    spelling_corrections = {
        # Common typos with one correct form
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
        
        # Contractions without apostrophe
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
        
        # Specific errors
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
    """
    Apply surface-level grammar rules.
    
    METHOD: POS-based surface cleanup (using provided POS tags)
    - Remove orphan adjectives
    - Clean double determiners
    - Remove repeated tokens
    
    IMPORTANT: This module does NOT generate POS tags. It applies rules
    only if POS tags are provided from previous preprocessing stage.
    
    NOT: Deep syntax, dependency parsing, subject-verb agreement, POS generation
    
    Based on: Natural Language Processing Recipes - Chapter 4 (Grammatical Normalization)
    
    Args:
        text: Text to process
        pos_tags: POS tags from previous preprocessing [(token, tag), ...]
        
    Returns:
        str: Cleaned text
    """
    # If no POS tags, use string-level cleanup only
    if pos_tags is None or len(pos_tags) == 0:
        return apply_string_level_cleanup(text)
    
    tokens = pos_tags
    cleaned_tokens = []
    i = 0
    
    while i < len(tokens):
        word, pos = tokens[i]
        
        # Rule 1: Remove double determiners (the the, a a)
        if pos == 'DT' and i + 1 < len(tokens):
            next_word, next_pos = tokens[i + 1]
            if next_pos == 'DT' and word.lower() == next_word.lower():
                # Skip duplicate determiner
                i += 1
                continue
        
        # Rule 2: Remove orphan adjective at end
        # (adjective not followed by noun)
        if pos in ['JJ', 'JJR', 'JJS'] and i == len(tokens) - 1:
            # Last word is adjective → remove
            i += 1
            continue
        
        # Rule 3: Surface check for duplicate words
        if i + 1 < len(tokens):
            next_word, _ = tokens[i + 1]
            if word.lower() == next_word.lower():
                # Duplicate word → keep one
                cleaned_tokens.append(word)
                i += 2
                continue
        
        # Rule 4: Remove orphan determiners at end
        if pos == 'DT' and i == len(tokens) - 1:
            # Last word is determiner → remove
            i += 1
            continue
        
        # Rule 5: Remove excessive consecutive adjectives (>3)
        # (usually indicates reconstruction error)
        if pos in ['JJ', 'JJR', 'JJS']:
            adj_count = 1
            j = i + 1
            while j < len(tokens) and tokens[j][1] in ['JJ', 'JJR', 'JJS']:
                adj_count += 1
                j += 1
            
            # If >3 consecutive adjectives, keep only last 2
            if adj_count > 3:
                i += adj_count - 2
                continue
        
        cleaned_tokens.append(word)
        i += 1
    
    # Reconstruct text
    result = ' '.join(cleaned_tokens)
    
    return result


def apply_string_level_cleanup(text):
    """
    Apply string-level cleanup (without POS tags).
    
    Only very conservative rules that don't require syntactic analysis.
    
    Args:
        text: Text to clean
        
    Returns:
        str: Cleaned text
    """
    # Remove exact duplicate words (word word → word)
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    
    # Remove triple+ repetitions of modifiers
    text = re.sub(r'\b(very|really|so)\s+\1\s+\1\b', 
                  r'\1', text, flags=re.IGNORECASE)
    
    return text


# ============================== STEP 3: POST-PROCESSING ==============================

def apply_post_processing(text):
    """
    Apply basic text formatting.
    
    METHOD: Text formatting rules
    - Capitalize first letter
    - Add period at end (if missing)
    - Clean whitespace
    - Basic punctuation
    
    Args:
        text: Text to format
        
    Returns:
        str: Formatted text
    """
    if not text:
        return text
    
    # Remove excess whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Fix spacing around punctuation
    # Remove spaces before punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    # Add space after punctuation (if missing)
    text = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', text)
    
    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    # Add period if missing and no other punctuation exists
    if text and text[-1] not in '.!?':
        text += '.'
    
    # Fix multiple punctuation marks
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'!{2,}', '!', text)
    text = re.sub(r'\?{2,}', '?', text)
    
    # Clean special characters
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    
    return text



# ============================== STEP 4: PRINT FUNCTIONS ==============================


def print_correction_step(step_number, step_name, content):
    """
    Print a correction step with formatting.
    
    Args:
        step_number: Step number
        step_name: Name of the step
        content: Content to display
    """
    print(f"\n[Step {step_number}] {step_name}")
    print("-" * 80)
    
    if isinstance(content, str):
        print(content)
    elif isinstance(content, dict):
        for key, value in content.items():
            print(f"  {key}: {value}")
    else:
        print(content)


# ============================== MAIN GRAMMATICAL CORRECTION PIPELINE ==============================

def grammatical_correction_pipeline(text, pos_tags=None, verbose=True):
    """
    Complete grammatical correction pipeline.
    
    Applies in order:
    1. Spelling correction
    2. Surface grammar rules
    3. Post-processing
    
    IMPORTANT: This module does NOT generate POS tags. It applies POS-based rules
    only if tags are provided from previous preprocessing.
    
    Based on: Natural Language Processing Recipes
    
    Args:
        text: The reconstructed sentence
        pos_tags: POS tags from previous preprocessing [(token, tag), ...]
        verbose: If True, print intermediate steps
        
    Returns:
        str: Corrected and formatted sentence
    """
    if not text or not text.strip():
        return text
    
    if verbose:
        print("\n" + "="*80)
        print("GRAMMATICAL CORRECTION & SMOOTHING")
        print("="*80)
        print_correction_step(0, "Input (Reconstructed Sentence)", text)
    
    # Step 1: Spelling correction
    corrected = apply_spelling_correction(text)
    if verbose:
        changes = "Changes applied" if corrected != text else "No changes"
        print_correction_step(1, "After Spelling Correction", f"{corrected}\n({changes})")
    
    # Step 2: Surface grammar rules
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


def grammatical_correction_simple(text, pos_tags=None):
    """
    Simplified grammatical correction returning only corrected text.
    
    Args:
        text: The reconstructed sentence
        pos_tags: Optional POS tags from preprocessing
        
    Returns:
        str: Corrected sentence
    """
    return grammatical_correction_pipeline(text, pos_tags, verbose=False)