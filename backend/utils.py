import os
import torch
import fitz  # PyMuPDF
import docx2txt
from transformers import (
    BartForConditionalGeneration, BartTokenizer,
    GPT2LMHeadModel, GPT2Tokenizer,
    BertTokenizer, BertModel
)
from sentence_transformers import SentenceTransformer, util

# Load models globally only once
bart_tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
bart_model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
gpt2_model = GPT2LMHeadModel.from_pretrained('gpt2')
gpt2_tokenizer.pad_token = gpt2_tokenizer.eos_token

bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')

sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')  # Load once globally

def read_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".pdf":
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".docx":
            return docx2txt.process(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return ""

def chunk_text(text, chunk_size=300):
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def summarize_text(text):
    inputs = bart_tokenizer([text], max_length=1024, return_tensors='pt', truncation=True)
    summary_ids = bart_model.generate(inputs['input_ids'], max_length=150, min_length=40, length_penalty=2.0)
    summary = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def embed_text(text):
    inputs = bert_tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = bert_model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]  # CLS token
    return embeddings

def generate_answer_with_bart(context, question):
    input_text = f"question: {question} context: {context}"
    inputs = bart_tokenizer([input_text], return_tensors='pt', truncation=True)
    summary_ids = bart_model.generate(inputs['input_ids'], max_length=100, num_beams=4, early_stopping=True)
    return bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def generate_answer_with_gpt2(context, question):
    input_text = f"Context: {context}\nQuestion: {question}\nAnswer:"
    input_ids = gpt2_tokenizer.encode(input_text, return_tensors="pt", truncation=True)
    outputs = gpt2_model.generate(input_ids, max_length=200, pad_token_id=gpt2_tokenizer.eos_token_id)
    return gpt2_tokenizer.decode(outputs[0], skip_special_tokens=True)

def get_most_relevant_sentence_with_bert(context, question):
    sentences = context.split('. ')
    question_embedding = sentence_transformer_model.encode(question, convert_to_tensor=True)
    sentence_embeddings = sentence_transformer_model.encode(sentences, convert_to_tensor=True)
    cos_scores = util.cos_sim(question_embedding, sentence_embeddings)[0]
    best_idx = torch.argmax(cos_scores).item()
    return sentences[best_idx]

def setup_document(file_path):
    text = read_file(file_path)
    if not text:
        return "", [], []
    chunks = chunk_text(text)
    embeddings = [embed_text(chunk) for chunk in chunks]
    summary = summarize_text(text)
    return summary, chunks, embeddings

def answer_question(question, stored_chunks, stored_embeddings, model_name="bart"):
    if not stored_chunks or not stored_embeddings:
        return "No document uploaded."
    
    question_embedding = embed_text(question)
    similarities = [util.pytorch_cos_sim(question_embedding, emb)[0][0].item() for emb in stored_embeddings]
    best_idx = similarities.index(max(similarities))
    context = stored_chunks[best_idx]

    if model_name.lower() == "gpt2":
        return generate_answer_with_gpt2(context, question)
    elif model_name.lower() == "bert":
        return get_most_relevant_sentence_with_bert(context, question)
    else:  # Default BART
        return generate_answer_with_bart(context, question)
