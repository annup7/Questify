from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from utils import setup_document, answer_question

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store documents in-memory for demo: {doc_id: {summary, chunks, embeddings}}
documents = {}

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed: {ALLOWED_EXTENSIONS}'}), 400
    
    try:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # DEBUG LOG
        print(f"Saved file to: {filepath}")

        summary, chunks, embeddings = setup_document(filepath)
        
        # DEBUG LOG
        print("Summary:", summary)
        print("Chunks:", chunks[:1])  # Print only 1st chunk for brevity
        print("Embeddings:", embeddings[:1])  # Embedding debug

        if not summary:
            return jsonify({'error': 'Failed to process the document'}), 500

        doc_id = str(uuid.uuid4())
        documents[doc_id] = {
            'summary': summary,
            'chunks': chunks,
            'embeddings': embeddings
        }
        return jsonify({'message': 'File uploaded and processed.', 'doc_id': doc_id})
    
    except Exception as e:
        # NEW LOG
        print(f"Exception during file processing: {e}")
        return jsonify({'error': f'Internal server error: {e}'}), 500


@app.route('/summary/<doc_id>', methods=['GET'])
def get_summary(doc_id):
    doc = documents.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    return jsonify({'summary': doc['summary']})

@app.route('/ask/<doc_id>', methods=['POST'])
def ask_question(doc_id):
    doc = documents.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    data = request.get_json()
    question = data.get('question')
    model = data.get('model', 'bart')
    if not question:
        return jsonify({'error': 'Question not provided'}), 400
    try:
        answer = answer_question(question, doc['chunks'], doc['embeddings'], model)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': f'Error processing question: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
