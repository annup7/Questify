import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");
  const [docId, setDocId] = useState(null);
  const [summary, setSummary] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loadingUpload, setLoadingUpload] = useState(false);
  const [loadingAnswer, setLoadingAnswer] = useState(false);

  const backendURL = "http://127.0.0.1:5000";

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setUploadMessage("");
    setSummary("");
    setDocId(null);
    setAnswer("");
    setQuestion("");
  };

  const uploadFile = async () => {
    if (!file) {
      setUploadMessage("Please select a file first.");
      return;
    }
    setLoadingUpload(true);
    setUploadMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${backendURL}/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (res.ok) {
        setUploadMessage("File uploaded successfully!");
        setDocId(data.doc_id);
        fetchSummary(data.doc_id);
      } else {
        setUploadMessage(data.error || "Upload failed.");
      }
    } catch (err) {
      setUploadMessage("Error: " + err.message);
    } finally {
      setLoadingUpload(false);
    }
  };

  const fetchSummary = async (id) => {
    try {
      const res = await fetch(`${backendURL}/summary/${id}`);
      const data = await res.json();
      if (res.ok) {
        setSummary(data.summary);
      } else {
        setSummary("Failed to fetch summary.");
      }
    } catch (err) {
      setSummary("Error: " + err.message);
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) {
      setAnswer("Please enter a question.");
      return;
    }
    if (!docId) {
      setAnswer("No document loaded.");
      return;
    }
    setLoadingAnswer(true);
    setAnswer("");

    try {
      const res = await fetch(`${backendURL}/ask/${docId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, model: "bart" }),
      });
      const data = await res.json();
      if (res.ok) {
        setAnswer(data.answer);
      } else {
        setAnswer(data.error || "Failed to get answer.");
      }
    } catch (err) {
      setAnswer("Error: " + err.message);
    } finally {
      setLoadingAnswer(false);
    }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: 720 }}>
      <h2 className="text-center mb-4 fw-bold text-primary">QUESTIFY</h2>

      {/* Upload Section */}
      <div className="card shadow-sm mb-4">
        <div className="card-body">
          <h5 className="card-title">Upload Document</h5>
          <input type="file" className="form-control mb-3" onChange={handleFileChange} />
          <button
            className="btn btn-success"
            onClick={uploadFile}
            disabled={loadingUpload}
          >
            {loadingUpload && (
              <span className="spinner-border spinner-border-sm me-2" role="status" />
            )}
            {loadingUpload ? "Uploading..." : "Upload & Summarize"}
          </button>
          {uploadMessage && (
            <div
              className={`alert mt-3 ${
                uploadMessage.toLowerCase().includes("error") ||
                uploadMessage.toLowerCase().includes("fail")
                  ? "alert-danger"
                  : "alert-success"
              }`}
            >
              {uploadMessage}
            </div>
          )}
        </div>
      </div>

      {/* Summary Section */}
      {summary && (
        <div className="card shadow-sm mb-4">
          <div className="card-body">
            <h5 className="card-title">📌 Summary</h5>
            <p className="card-text" style={{ whiteSpace: "pre-wrap" }}>{summary}</p>
          </div>
        </div>
      )}

      {/* QnA Section */}
      {docId && (
        <div className="card shadow-sm">
          <div className="card-body">
            <h5 className="card-title">❓ Ask a Question</h5>
            <textarea
              className="form-control mb-3"
              rows="3"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Type your question here..."
            />
            <button
              className="btn btn-primary"
              onClick={askQuestion}
              disabled={loadingAnswer}
            >
              {loadingAnswer && (
                <span className="spinner-border spinner-border-sm me-2" role="status" />
              )}
              {loadingAnswer ? "Getting Answer..." : "Ask"}
            </button>
            {answer && (
              <div className="alert alert-info mt-3" style={{ whiteSpace: "pre-wrap" }}>
                <strong>Answer:</strong> {answer}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
