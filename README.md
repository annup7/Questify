# QUESTIFY: Document-based Question Answering System

Questify is a full-stack web application that allows users to upload documents (PDF, TXT, DOCX), summarize their content, and ask questions based on that content. It uses state-of-the-art Transformer models for Natural Language Processing (NLP) to generate intelligent responses.

---

## 🚀 Tech Stack

### 🔧 Frontend
- React.js (Vite)
- Bootstrap
- Axios

### 🧠 Backend
- Python (Flask)
- Transformers (from Hugging Face)
- MySQL (for data storage)
- Libraries: PyMuPDF, python-docx, PDFMiner, etc.

---

## 🤖 NLP Models Used

| Model  | Usage | Description |
|--------|-------|-------------|
| **BERT** | Question Answering | Extractive QA model that finds answers in text |
| **T5 (Text-To-Text Transfer Transformer)** | Summarization | Converts long documents into concise summaries |
| **BART** | *(optional/extendable)* | Powerful for summarization and QnA (not used yet but can replace T5/BERT) |
| **GPT-2** | *(optional/extendable)* | Generative model suitable for free-form answers (not currently integrated) |

---

## ✨ Features

- Upload documents (`.pdf`, `.txt`, `.docx`)
- Text summarization using **T5**
- Ask natural language questions
- Answer generation using **BERT**
- Real-time interaction through React UI
- Backend powered by Flask + MySQL

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

git clone https://github.com/annup7/Questify.git
cd Questify

### 2. Backend Setup

cd backend
python -m venv venv
venv\Scripts\activate     # On Windows
pip install -r requirements.txt
python app.py

### 3. Frontend Setup

cd frontend/doc-qna-frontend
npm install
npm run dev

---

## 🧪 Usage

1. Visit the frontend in browser (default: http://localhost:5173)
2. Upload a document
3. Click Summarize
4. Ask any question related to the content
5. View instant AI-generated answers

---

## 👤 Author
Anup Nalawade
anupnalawadee@gmail.com

---

## 📄 License

MIT License – feel free to use and modify.

