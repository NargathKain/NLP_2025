"""
NLTK Data Setup Script
Run this once before using the preprocessing pipeline.
"""

import nltk
import ssl

def download_nltk_data():
    """
    Download all required NLTK data packages.
    """
    print("\n" + "="*60)
    print("NLTK DATA SETUP")
    print("="*60 + "\n")
    
    # Fix SSL certificate issue
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    # Required packages
    packages = [
        ('punkt', 'Tokenization'),
        ('wordnet', 'Lemmatization'),
        ('averaged_perceptron_tagger', 'POS Tagging'),
        ('omw-1.4', 'Open Multilingual Wordnet'),
    ]
    
    print("Downloading required NLTK packages...\n")
    
    for package, description in packages:
        print(f"📦 {description} ({package})...", end=" ")
        try:
            nltk.download(package, quiet=True)
            print("✓")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✓ NLTK setup complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    download_nltk_data()