# Συντακτική ανακατασκευή χρησιμοποιώντας ετικέτες POS, εξαγωγή ουσιαστικών (noun),
# string transformation με βάση κανόνες και pattern matching

import re
from typing import List, Tuple, Dict

# ============== CONSTANTS ==============

# συνδετικές λέξεις
SUBORDINATE_CONJUNCTIONS = {
    'although', 'because', 'if', 'when', 'while', 'since', 
    'unless', 'until', 'whereas', 'though', 'after', 'before', 'as'
}

# βοηθητικά ρήματα
AUXILIARY_VERBS = {
    'be', 'am', 'is', 'are', 'was', 'were', 'been', 'being',
    'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing',
    'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could'
}

'''
ΝΝ = common noun
NNS = common noun plural
NNP = proper noun, singular
NNPS = proper noun, plural

PRP = αντωνυμία personal pronoun
PRP$ = possesive pronoun πχ my

DT = determiner πχ the

JJ = adjective - επίθετο good
JJR = comparative adjective better
JJS = superlative adjective πχ best

RB = επίρρημα adverb πχ quickly
RBR = comparative adverb πχ faster
RBS = superlative adverb πχ fastest

VB* = όλα τα ρήματα πιάνονται σε αυτό
MD = modal πχ can, should, will

IN = preposition/ subordinating conjuction πχ in, on, because, if

RP = phrasal verb particles πχ up, out, pick up

'''


# ============== STEP 1: POS PATTERN DETECTION ==============

def identify_noun_phrases(pos_tags):
    # Βρες “ονοματικές φράσεις” (NP) με απλούς κανόνες POS.
    # Patterns:
    # - DT? JJ* NN(S)?  (e.g., "the big dog")
    # - PRP$ JJ* NN(S)?  (e.g., "my new car")
    # - NN(S)? alone
    # - PRP alone
    # Επιστρέφει: List[Tuple[start_idx, end_idx, tokens]]
    noun_phrases = []
    i = 0
    
    while i < len(pos_tags):
        phrase_start = i
        phrase_tokens = []
        
        # Pronouns alone (PRP)
        if pos_tags[i][1] == 'PRP':
            noun_phrases.append((i, i+1, [pos_tags[i][0]]))
            i += 1
            continue
        
        # Determiners (DT) or Possessives (PRP$)
        if pos_tags[i][1] in ['DT', 'PRP$']:
            phrase_tokens.append(pos_tags[i][0])
            i += 1
        
        # Adjectives (JJ, JJR, JJS)
        while i < len(pos_tags) and pos_tags[i][1] in ['JJ', 'JJR', 'JJS']:
            phrase_tokens.append(pos_tags[i][0])
            i += 1
        
        # Nouns (NN, NNS, NNP, NNPS)
        if i < len(pos_tags) and pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS']:
            phrase_tokens.append(pos_tags[i][0])
            i += 1
            
            # We have a noun phrase
            if len(phrase_tokens) > 0:
                noun_phrases.append((phrase_start, i, phrase_tokens))
        else:
            # Not a complete noun phrase
            if len(phrase_tokens) == 0:
                # Check if standalone noun
                if i < len(pos_tags) and pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS']:
                    noun_phrases.append((i, i+1, [pos_tags[i][0]]))
                    i += 1
                else:
                    i = phrase_start + 1
            else:
                i = phrase_start + 1
    
    return noun_phrases


def find_verb_groups(pos_tags):
    # Identify verb groups and distinguish auxiliary from main verbs.
    # Returns: List of (start_idx, end_idx, tokens, is_main_verb)
    verb_groups = []
    i = 0
    
    while i < len(pos_tags):
        phrase_start = i
        phrase_tokens = []
        
        # Check for modal or auxiliary
        if pos_tags[i][1] == 'MD' or (pos_tags[i][1].startswith('VB') and pos_tags[i][0].lower() in AUXILIARY_VERBS):
            phrase_tokens.append(pos_tags[i][0])
            i += 1
        
        # Main verb
        if i < len(pos_tags) and pos_tags[i][1].startswith('VB'):
            phrase_tokens.append(pos_tags[i][0])
            is_main = pos_tags[i][0].lower() not in AUXILIARY_VERBS
            i += 1
            
            # Particle (RP) - phrasal verb
            if i < len(pos_tags) and pos_tags[i][1] == 'RP':
                phrase_tokens.append(pos_tags[i][0])
                i += 1
            
            if len(phrase_tokens) > 0:
                verb_groups.append((phrase_start, i, phrase_tokens, is_main))
        else:
            if len(phrase_tokens) > 0:
                verb_groups.append((phrase_start, i, phrase_tokens, False))
            else:
                i += 1
    
    return verb_groups


def detect_subordinate_conjunctions(pos_tags):
    # Detect subordinate conjunctions using EXPLICIT word list only.
    # Returns: List of (index, word)
    subordinate_markers = []
    
    for i, (token, pos) in enumerate(pos_tags):
        if token.lower() in SUBORDINATE_CONJUNCTIONS:
            subordinate_markers.append((i, token.lower()))
    
    return subordinate_markers

# ============== STEP 2: PROBLEMATIC PATTERN DETECTION WITH FIXES ==============

def fix_preposition_adjective_no_noun(pos_tags, problem_idx):
    # Fix: IN + JJ without NN
    # Strategy: Attach adjective to nearest following noun phrase
    # Returns: Modified pos_tags
    # Find nearest noun after the adjective
    nearest_noun_idx = None
    for i in range(problem_idx + 2, min(problem_idx + 5, len(pos_tags))):
        if pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS']:
            nearest_noun_idx = i
            break
    
    if nearest_noun_idx:
        # Move adjective next to noun
        adj_token = pos_tags[problem_idx + 1]
        # Reorder: keep preposition, move adjective+noun together
        new_tags = (
            pos_tags[:problem_idx+1] +  # Keep up to preposition
            [adj_token] +                # Adjective
            [pos_tags[nearest_noun_idx]] +  # Noun
            pos_tags[problem_idx+2:nearest_noun_idx] +  # In-between
            pos_tags[nearest_noun_idx+1:]  # Rest
        )
        return new_tags
    
    return pos_tags


def fix_verb_without_subject(pos_tags, verb_idx):
    # Fix: Verb without clear subject
    # Strategy: Find nearest NP/PRP and move before verb
    # Returns: Modified pos_tags
    # Look for subject candidates around verb (within 5 tokens)
    subject_idx = None
    
    # First, check before verb (preferred)
    for i in range(max(0, verb_idx - 5), verb_idx):
        if pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS', 'PRP']:
            subject_idx = i
    
    # If not found, check after verb
    if subject_idx is None:
        for i in range(verb_idx + 1, min(verb_idx + 5, len(pos_tags))):
            if pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS', 'PRP']:
                subject_idx = i
                break
    
    if subject_idx is not None and subject_idx != verb_idx - 1:
        # Move subject before verb
        subject_token = pos_tags[subject_idx]
        
        if subject_idx < verb_idx:
            # Subject is before but not immediately before
            new_tags = (
                pos_tags[:subject_idx] +  # Before subject
                pos_tags[subject_idx+1:verb_idx] +  # Between subject and verb
                [subject_token] +  # Subject moved here
                pos_tags[verb_idx:]  # Verb and rest
            )
        else:
            # Subject is after verb, move it before
            new_tags = (
                pos_tags[:verb_idx] +  # Before verb
                [subject_token] +  # Subject moved here
                pos_tags[verb_idx:subject_idx] +  # Verb to subject
                pos_tags[subject_idx+1:]  # After subject
            )
        
        return new_tags
    
    return pos_tags


def fix_unusual_start(pos_tags):
    # Fix: Sentence starts with adjective/adverb without structure
    # Strategy: Move to after first noun phrase or verb
    # Returns: Modified pos_tags
    if len(pos_tags) < 2:
        return pos_tags
    
    first_token = pos_tags[0]
    
    # Find first noun or verb
    target_idx = None
    for i in range(1, len(pos_tags)):
        if pos_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS', 'PRP'] or pos_tags[i][1].startswith('VB'):
            target_idx = i
            break
    
    if target_idx:
        # Move adjective/adverb after target
        new_tags = (
            pos_tags[1:target_idx+1] +  # Skip first, go to target
            [first_token] +  # Move first token here
            pos_tags[target_idx+1:]  # Rest
        )
        return new_tags
    
    return pos_tags


def detect_and_fix_problems(pos_tags):
    # Detect problematic patterns and apply fixes.
    # Returns: (fixed_pos_tags, problems_found)
    problems = []
    fixed_tags = list(pos_tags)
    
    # Problem 1: IN + JJ without NN
    i = 0
    while i < len(fixed_tags) - 1:
        if fixed_tags[i][1] == 'IN' and fixed_tags[i+1][1] in ['JJ', 'JJR', 'JJS']:
            # Check if followed by noun
            has_noun = False
            if i+2 < len(fixed_tags) and fixed_tags[i+2][1] in ['NN', 'NNS', 'NNP', 'NNPS']:
                has_noun = True
            
            if not has_noun:
                problems.append({
                    'type': 'preposition_adjective_no_noun',
                    'position': i,
                    'original': [fixed_tags[i][0], fixed_tags[i+1][0]]
                })
                # Apply fix
                fixed_tags = fix_preposition_adjective_no_noun(fixed_tags, i)
        i += 1
    
    # Problem 2: Verb without subject (check main verbs only)
    verb_groups = find_verb_groups(fixed_tags)
    for start, end, tokens, is_main in verb_groups:
        if is_main:
            # Check for subject before verb
            has_subject = False
            for i in range(max(0, start - 3), start):
                if fixed_tags[i][1] in ['NN', 'NNS', 'NNP', 'NNPS', 'PRP']:
                    has_subject = True
                    break
            
            if not has_subject and start > 0:
                problems.append({
                    'type': 'verb_without_subject',
                    'position': start,
                    'original': tokens
                })
                # Apply fix
                fixed_tags = fix_verb_without_subject(fixed_tags, start)
    
    # Problem 3: Unusual start
    if len(fixed_tags) > 0 and fixed_tags[0][1] in ['JJ', 'RB', 'RBR', 'RBS']:
        if len(fixed_tags) < 3 or fixed_tags[1][1] not in ['NN', 'NNS', 'NNP', 'NNPS', 'PRP']:
            problems.append({
                'type': 'unusual_start',
                'position': 0,
                'original': [fixed_tags[0][0]]
            })
            # Apply fix
            fixed_tags = fix_unusual_start(fixed_tags)
    
    return fixed_tags, problems

# ============== STEP 3: IMPROVED S-V-O EXTRACTION ==============

def extract_svo_components(pos_tags):
    # Extract Subject-Verb-Object with improved logic.
    # Subject = NP before main verb (not auxiliary)
    # Verb = Main verb (not auxiliary)
    # Object = NP after main verb
    # Returns: dict with 'subject', 'verb', 'object', 'other'
    components = {
        'subject': [],
        'verb': [],
        'object': [],
        'other': []
    }
    
    noun_phrases = identify_noun_phrases(pos_tags)
    verb_groups = find_verb_groups(pos_tags)
    
    # Find main verb (first non-auxiliary verb)
    main_verb_idx = None
    main_verb_tokens = []
    
    for start, end, tokens, is_main in verb_groups:
        if is_main:
            main_verb_idx = start
            main_verb_tokens = tokens
            components['verb'] = tokens
            break
    
    # If no main verb found, use first verb group
    if main_verb_idx is None and len(verb_groups) > 0:
        main_verb_idx = verb_groups[0][0]
        main_verb_tokens = verb_groups[0][2]
        components['verb'] = main_verb_tokens
    
    # Extract subject: NP before main verb
    if main_verb_idx is not None:
        for start, end, tokens in noun_phrases:
            if end <= main_verb_idx:
                # Take the closest NP before verb as subject
                components['subject'] = tokens
    
    # Extract object: NP after main verb
    if main_verb_idx is not None:
        verb_end = main_verb_idx + len(main_verb_tokens)
        for start, end, tokens in noun_phrases:
            if start >= verb_end:
                components['object'] = tokens
                break
    
    # Collect remaining tokens
    used_indices = set()
    
    # Mark subject
    for start, end, tokens in noun_phrases:
        if tokens == components['subject']:
            used_indices.update(range(start, end))
            break
    
    # Mark verb
    if main_verb_idx is not None:
        used_indices.update(range(main_verb_idx, main_verb_idx + len(main_verb_tokens)))
    
    # Mark object
    if main_verb_idx is not None:
        verb_end = main_verb_idx + len(main_verb_tokens)
        for start, end, tokens in noun_phrases:
            if start >= verb_end and tokens == components['object']:
                used_indices.update(range(start, end))
                break
    
    # Collect other tokens
    for i, (token, pos) in enumerate(pos_tags):
        if i not in used_indices and token not in [',', '.', '!', '?']:
            components['other'].append(token)
    
    return components

# ============== STEP 4: CLAUSE IDENTIFICATION AND REORDERING ==============

def identify_clauses(pos_tags):
    # Split sentence into main and dependent clauses using explicit conjunctions.
    # Returns: dict with 'main', 'dependent', 'subordinate_positions'
    clauses = {
        'main': [],
        'dependent': [],
        'subordinate_positions': []
    }
    
    # Find explicit subordinate conjunctions
    sub_positions = detect_subordinate_conjunctions(pos_tags)
    
    if len(sub_positions) == 0:
        # No dependent clause, all is main
        clauses['main'] = list(range(len(pos_tags)))
        return clauses
    
    clauses['subordinate_positions'] = [pos for pos, word in sub_positions]
    
    # If subordinate conjunction at start (first 3 positions)
    if sub_positions[0][0] < 3:
        # Dependent clause comes first
        # Find boundary (comma or halfway point)
        boundary = len(pos_tags) // 2
        for i in range(sub_positions[0][0] + 1, len(pos_tags)):
            if pos_tags[i][0] == ',':
                boundary = i
                break
        
        clauses['dependent'] = list(range(sub_positions[0][0], boundary + 1))
        clauses['main'] = list(range(boundary + 1, len(pos_tags)))
    else:
        # Main clause first
        clauses['main'] = list(range(0, sub_positions[0][0]))
        clauses['dependent'] = list(range(sub_positions[0][0], len(pos_tags)))
    
    return clauses


def reorder_clause(pos_tags):
    # Reorder a single clause to S-V-O structure.
    # Returns: str
    if len(pos_tags) == 0:
        return ""
    
    components = extract_svo_components(pos_tags)
    
    # Build sentence: Subject + Verb + Object + Other
    parts = []
    if components['subject']:
        parts.append(' '.join(components['subject']))
    if components['verb']:
        parts.append(' '.join(components['verb']))
    if components['object']:
        parts.append(' '.join(components['object']))
    if components['other']:
        parts.append(' '.join(components['other']))
    
    result = ' '.join(parts)
    
    return result


def handle_clauses(pos_tags):
    # Handle dependent and main clauses with reordering within each clause.
    # Strategy:
    # 1. Identify clauses
    # 2. Reorder WITHIN each clause
    # 3. Combine: Main clause + comma + dependent clause
    # Returns: str
    clause_info = identify_clauses(pos_tags)
    
    # If no dependent clause, reorder as single sentence
    if len(clause_info['dependent']) == 0:
        return reorder_clause(pos_tags)
    
    # Extract tokens for each clause
    main_tokens = [pos_tags[i] for i in clause_info['main']]
    dependent_tokens = [pos_tags[i] for i in clause_info['dependent']]
    
    # Reorder within main clause
    main_reconstructed = ""
    if len(main_tokens) > 0:
        main_reconstructed = reorder_clause(main_tokens)
    
    # Reorder within dependent clause (but keep conjunction at start)
    dependent_reconstructed = ""
    if len(dependent_tokens) > 0:
        # Keep conjunction, reorder rest
        conjunction = dependent_tokens[0][0]
        rest_tokens = dependent_tokens[1:]
        
        if len(rest_tokens) > 0:
            rest_reconstructed = reorder_clause(rest_tokens)
            dependent_reconstructed = f"{conjunction} {rest_reconstructed}".strip()
        else:
            dependent_reconstructed = conjunction
    
    # Combine: Main + comma + Dependent
    if main_reconstructed and dependent_reconstructed:
        result = f"{main_reconstructed}, {dependent_reconstructed}"
    elif main_reconstructed:
        result = main_reconstructed
    else:
        result = dependent_reconstructed
    
    return result

# ============== STEP 5: PRINT FUNCTIONS ==============

def print_analysis_step(step_number, step_name, content):
    # Print an analysis step with formatting.
    print(f"\n[Step {step_number}] {step_name}")
    print("-" * 80)
    
    if isinstance(content, str):
        print(content)
    elif isinstance(content, list):
        if len(content) > 0:
            if isinstance(content[0], tuple):
                print(f"Found {len(content)} items:")
                for item in content[:5]:
                    print(f"  {item}")
                if len(content) > 5:
                    print(f"  ... and {len(content) - 5} more")
            else:
                print(content)
        else:
            print("None found")
    elif isinstance(content, dict):
        for key, value in content.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: {value}")
    else:
        print(content)

# ============== MAIN SYNTACTIC ANALYSIS PIPELINE ==============

def syntactic_analysis_pipeline(pos_tags, verbose=True):
    # Complete rule-based syntactic reconstruction pipeline.
    # Process:
    # 1. Detect and fix problematic patterns
    # 2. Identify noun phrases and verb groups
    # 3. Extract S-V-O components with improved logic
    # 4. Identify and reorder clauses
    # 5. Reconstruct sentence
    # Args:
    #     pos_tags: List of (token, POS_tag) tuples from preprocessing
    #     verbose: If True, print intermediate steps
    # Returns: dict: Contains original, reconstructed, and analysis details
    if len(pos_tags) == 0:
        return {
            'original': '',
            'reconstructed': '',
            'noun_phrases': [],
            'verb_groups': [],
            'problems_fixed': [],
            'clauses': {},
            'svo_components': {}
        }
    
    # Original sentence
    original = ' '.join([token for token, _ in pos_tags])
    
    if verbose:
        print("\n" + "="*80)
        print("SYNTACTIC ANALYSIS & RECONSTRUCTION")
        print("="*80)
        print_analysis_step(0, "Original Sentence", original)
    
    # Step 1: Detect and fix problems
    fixed_pos_tags, problems = detect_and_fix_problems(pos_tags)
    
    if verbose:
        if len(problems) > 0:
            print_analysis_step(1, "Problems Detected & Fixed", problems)
        else:
            print_analysis_step(1, "Problems Detected & Fixed", "No problems detected")
    
    # Step 2: Identify noun phrases
    noun_phrases = identify_noun_phrases(fixed_pos_tags)
    if verbose:
        print_analysis_step(2, "Noun Phrases Identified", noun_phrases)
    
    # Step 3: Identify verb groups (with main verb detection)
    verb_groups = find_verb_groups(fixed_pos_tags)
    if verbose:
        formatted_verbs = [(start, end, tokens, "MAIN" if is_main else "AUX") 
                          for start, end, tokens, is_main in verb_groups]
        print_analysis_step(3, "Verb Groups Identified", formatted_verbs)
    
    # Step 4: Identify clauses
    clauses = identify_clauses(fixed_pos_tags)
    if verbose:
        print_analysis_step(4, "Clause Structure", clauses)
    
    # Step 5: Extract S-V-O components
    svo_components = extract_svo_components(fixed_pos_tags)
    if verbose:
        print_analysis_step(5, "S-V-O Components Extracted", svo_components)
    
    # Step 6: Reconstruct with clause handling
    reconstructed = handle_clauses(fixed_pos_tags)
    
    # Step 7: Clean up
    reconstructed = re.sub(r'\s+([.,!?])', r'\1', reconstructed)
    reconstructed = re.sub(r'\s+', ' ', reconstructed).strip()
    
    # Capitalize first letter
    if reconstructed:
        reconstructed = reconstructed[0].upper() + reconstructed[1:]
    
    # Add period if missing
    if reconstructed and reconstructed[-1] not in '.!?':
        reconstructed += '.'
    
    if verbose:
        print_analysis_step(6, "Reconstructed Sentence (FINAL)", reconstructed)
        print("\n" + "="*80)
        print("✓ Syntactic reconstruction complete")
        print("="*80)
    
    # Prepare result
    result = {
        'original': original,
        'reconstructed': reconstructed,
        'noun_phrases': noun_phrases,
        'verb_groups': verb_groups,
        'problems_fixed': problems,
        'clauses': clauses,
        'svo_components': svo_components
    }
    
    return result


def syntactic_analysis_simple(pos_tags):
    # Simplified version returning only reconstructed sentence.
    # Args: pos_tags: List of (token, POS_tag) tuples    
    # Returns: str: Reconstructed sentence
    return syntactic_analysis_pipeline(pos_tags, verbose=False)['reconstructed']