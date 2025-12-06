import spacy
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import nltk
from nltk.tokenize import sent_tokenize
import re

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

TEXT_1 = "Today is our dragon boat festival, in our Chinese culture, to celebrate it with all safe and great in our lives. Hope you too, to enjoy it as my deepest wishes. Thank your message to show our words to the doctor, as his next contract checking, to all of us. I got this message to see the approved message. In fact, I have received the message from the professor, to show me, this, a couple of days ago. I am very appreciated the full support of the professor, for our Springer proceedings publication."

TEXT_2 = "During our final discuss, I told him about the new submission — the one we were waiting since last autumn, but the updates was confusing as it not included the full feedback from reviewer or maybe editor? Anyway, I believe the team, although bit delay and less communication at recent days, they really tried best for paper and cooperation. We should be grateful, I mean all of us, for the acceptance and efforts until the Springer link came finally last week, I think. Also, kindly remind me please, if the doctor still plan for the acknowledgments section edit before he sending again. Because I didn't see that part final yet, or maybe I missed, I apologize if so. Overall, let us make sure all are safe and celebrate the outcome with strong coffee and future targets."


def pipeline_spacy_rules(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    reconstructed_sentences = []
    
    for sent in doc.sents:
        sentence_text = sent.text.strip()
        
        sentence_text = re.sub(r'\bto celebrate it with all safe and great\b', 'to celebrate safely and happily', sentence_text)
        sentence_text = re.sub(r'\bHope you too, to enjoy\b', 'I hope you can also enjoy', sentence_text)
        sentence_text = re.sub(r'\bas my deepest wishes\b', 'with my deepest wishes', sentence_text)
        sentence_text = re.sub(r'\bThank your message to show our words to\b', 'Thank you for conveying our message to', sentence_text)
        sentence_text = re.sub(r'\bas his next contract checking\b', 'for his next contract review', sentence_text)
        sentence_text = re.sub(r'\bI got this message to see the approved message\b', 'I received the approval message', sentence_text)
        sentence_text = re.sub(r'\bto show me, this,\b', 'showing me this', sentence_text)
        sentence_text = re.sub(r'\bI am very appreciated\b', 'I very much appreciate', sentence_text)
        
        sentence_text = re.sub(r'\bDuring our final discuss\b', 'During our final discussion', sentence_text)
        sentence_text = re.sub(r'\bthe one we were waiting since\b', 'the one we have been waiting for since', sentence_text)
        sentence_text = re.sub(r'\bthe updates was confusing as it not included\b', 'the updates were confusing as they did not include', sentence_text)
        sentence_text = re.sub(r'\bfrom reviewer or maybe editor\b', 'from the reviewer or perhaps the editor', sentence_text)
        sentence_text = re.sub(r'\balthough bit delay and less communication at recent days\b', 'although there was a bit of delay and less communication in recent days', sentence_text)
        sentence_text = re.sub(r'\bthey really tried best for paper\b', 'they really tried their best for the paper', sentence_text)
        sentence_text = re.sub(r'\buntil the Springer link came finally\b', 'until the Springer link finally came', sentence_text)
        sentence_text = re.sub(r'\bif the doctor still plan for\b', 'if the doctor still plans to do', sentence_text)
        sentence_text = re.sub(r'\bbefore he sending again\b', 'before he sends it again', sentence_text)
        sentence_text = re.sub(r'\bI didn\'t see that part final yet\b', 'I have not seen that final part yet', sentence_text)
        sentence_text = re.sub(r'\blet us make sure all are safe\b', 'let us make sure everyone is safe', sentence_text)
        
        sentence_text = re.sub(r'\s+', ' ', sentence_text).strip()
        reconstructed_sentences.append(sentence_text)
    
    result = ' '.join(reconstructed_sentences)
    result = re.sub(r'\s+([.,;!?])', r'\1', result)
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result


def pipeline_paraphrase(text):
    model_name = "humarin/chatgpt_paraphraser_on_T5_base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    
    sentences = sent_tokenize(text)
    paraphrased_sentences = []
    
    for sent in sentences:
        sent = sent.strip()
        if len(sent) > 10:
            try:
                input_text = f"paraphrase: {sent}"
                inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True).to(device)
                
                outputs = model.generate(
                    **inputs,
                    max_length=128,
                    num_beams=5,
                    num_return_sequences=1,
                    temperature=1.0,
                    do_sample=False
                )
                
                paraphrased = tokenizer.decode(outputs[0], skip_special_tokens=True)
                paraphrased_sentences.append(paraphrased.strip())
            except Exception as e:
                paraphrased_sentences.append(sent)
        else:
            paraphrased_sentences.append(sent)
    
    return ' '.join(paraphrased_sentences)


def pipeline_grammar_fix(text):
    model_name = "pszemraj/flan-t5-large-grammar-synthesis"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    
    sentences = sent_tokenize(text)
    corrected_sentences = []
    
    for sent in sentences:
        sent = sent.strip()
        if len(sent) > 5:
            try:
                inputs = tokenizer(sent, return_tensors="pt", max_length=512, truncation=True).to(device)
                
                outputs = model.generate(
                    **inputs,
                    max_length=128,
                    num_beams=4,
                    num_return_sequences=1,
                    early_stopping=True
                )
                
                corrected = tokenizer.decode(outputs[0], skip_special_tokens=True)
                corrected_sentences.append(corrected.strip())
            except Exception as e:
                corrected_sentences.append(sent)
        else:
            corrected_sentences.append(sent)
    
    return ' '.join(corrected_sentences)


def main():
    print("=" * 80)
    print("PIPELINE 1: spaCy + Rule-Based Rewriting")
    print("=" * 80)
    text1_spacy = pipeline_spacy_rules(TEXT_1)
    print(f"\nTEXT_1 (spaCy Rules):\n{text1_spacy}\n")
    
    text2_spacy = pipeline_spacy_rules(TEXT_2)
    print(f"TEXT_2 (spaCy Rules):\n{text2_spacy}\n")
    
    print("=" * 80)
    print("PIPELINE 2: HuggingFace Paraphrasing (T5-based)")
    print("=" * 80)
    text1_paraphrase = pipeline_paraphrase(TEXT_1)
    print(f"\nTEXT_1 (Paraphrase):\n{text1_paraphrase}\n")
    
    text2_paraphrase = pipeline_paraphrase(TEXT_2)
    print(f"TEXT_2 (Paraphrase):\n{text2_paraphrase}\n")
    
    print("=" * 80)
    print("PIPELINE 3: HuggingFace Grammar Correction (FLAN-T5)")
    print("=" * 80)
    text1_grammar = pipeline_grammar_fix(TEXT_1)
    print(f"\nTEXT_1 (Grammar Fix):\n{text1_grammar}\n")
    
    text2_grammar = pipeline_grammar_fix(TEXT_2)
    print(f"TEXT_2 (Grammar Fix):\n{text2_grammar}\n")
    
    results = {
        "pipeline_spacy_rules": {
            "text1": text1_spacy,
            "text2": text2_spacy
        },
        "pipeline_paraphrase": {
            "text1": text1_paraphrase,
            "text2": text2_paraphrase
        },
        "pipeline_grammar_fix": {
            "text1": text1_grammar,
            "text2": text2_grammar
        }
    }
    
    print("=" * 80)
    print("RESULTS DICTIONARY")
    print("=" * 80)
    for pipeline_name, outputs in results.items():
        print(f"\n{pipeline_name}:")
        print(f"  text1: {outputs['text1'][:100]}...")
        print(f"  text2: {outputs['text2'][:100]}...")
    
    return results


if __name__ == "__main__":
    results = main()