import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import AuroraBackground from './AuroraBackground';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
export default function MainApp() {
  const navigate = useNavigate();
  const [docA, setDocA] = useState(null);
  const [docB, setDocB] = useState(null);
  const [uploadingA, setUploadingA] = useState(false);
  const [uploadingB, setUploadingB] = useState(false);
  const [uploadedA, setUploadedA] = useState(false);
  const [uploadedB, setUploadedB] = useState(false);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (docId, file) => {
    if (file && file.type === 'application/pdf') {
      if (docId === 'doc_A') {
        setDocA(file);
        setUploadedA(false);
      } else {
        setDocB(file);
        setUploadedB(false);
      }
      setError('');
    } else {
      setError('Please select a valid PDF file');
    }
  };

  const handleUpload = async (docId) => {
    const file = docId === 'doc_A' ? docA : docB;
    const setUploading = docId === 'doc_A' ? setUploadingA : setUploadingB;
    const setUploaded = docId === 'doc_A' ? setUploadedA : setUploadedB;

    if (!file) {
      setError(`Please select a PDF for Document ${docId === 'doc_A' ? 'A' : 'B'}`);
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_id', docId);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setUploaded(true);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to upload Document ${docId === 'doc_A' ? 'A' : 'B'}`);
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    
    if (!uploadedA || !uploadedB) {
      setError('Please upload both documents first');
      return;
    }

    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError('');
    setAnswer('');

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        question: question.trim()
      });
      
      setAnswer(response.data.answer);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get answer');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050a14] text-white">
      <AuroraBackground />
      
      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-white/10 backdrop-blur-sm">
          <div className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between">
            <motion.button
              onClick={() => navigate('/')}
              whileHover={{ x: -5 }}
              className="text-gray-400 hover:text-white transition-colors text-sm"
            >
              ← Back
            </motion.button>
            <h1 className="text-xl font-semibold">RAG Document Comparator</h1>
            <div className="w-16"></div>
          </div>
        </header>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto px-6 py-16">
          {/* Error Display */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="mb-8 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-200 text-sm"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Upload Section */}
          <div className="grid md:grid-cols-2 gap-8 mb-16">
            {/* Document A */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <h2 className="text-sm font-medium text-gray-400 mb-4">Document A</h2>
              
              <div className="relative">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => handleFileChange('doc_A', e.target.files[0])}
                  className="hidden"
                  id="file-a"
                />
                <label
                  htmlFor="file-a"
                  className="block w-full p-6 border border-white/10 rounded-lg text-center cursor-pointer hover:border-white/30 transition-colors bg-white/5 backdrop-blur-sm"
                >
                  {docA ? (
                    <span className="text-white text-sm">{docA.name}</span>
                  ) : (
                    <span className="text-gray-500 text-sm">Click to select PDF</span>
                  )}
                </label>
              </div>

              <button
                onClick={() => handleUpload('doc_A')}
                disabled={!docA || uploadingA || uploadedA}
                className={`w-full py-3 rounded-lg font-medium text-sm transition-all ${
                  uploadedA
                    ? 'bg-green-500/20 border border-green-500/50 text-green-400'
                    : uploadingA
                    ? 'bg-white/5 text-gray-500'
                    : docA
                    ? 'bg-white text-black hover:bg-gray-100'
                    : 'bg-white/5 text-gray-600 cursor-not-allowed'
                }`}
              >
                {uploadingA ? 'Uploading...' : uploadedA ? '✓ Uploaded' : 'Upload'}
              </button>
            </motion.div>

            {/* Document B */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="space-y-4"
            >
              <h2 className="text-sm font-medium text-gray-400 mb-4">Document B</h2>
              
              <div className="relative">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => handleFileChange('doc_B', e.target.files[0])}
                  className="hidden"
                  id="file-b"
                />
                <label
                  htmlFor="file-b"
                  className="block w-full p-6 border border-white/10 rounded-lg text-center cursor-pointer hover:border-white/30 transition-colors bg-white/5 backdrop-blur-sm"
                >
                  {docB ? (
                    <span className="text-white text-sm">{docB.name}</span>
                  ) : (
                    <span className="text-gray-500 text-sm">Click to select PDF</span>
                  )}
                </label>
              </div>

              <button
                onClick={() => handleUpload('doc_B')}
                disabled={!docB || uploadingB || uploadedB}
                className={`w-full py-3 rounded-lg font-medium text-sm transition-all ${
                  uploadedB
                    ? 'bg-green-500/20 border border-green-500/50 text-green-400'
                    : uploadingB
                    ? 'bg-white/5 text-gray-500'
                    : docB
                    ? 'bg-white text-black hover:bg-gray-100'
                    : 'bg-white/5 text-gray-600 cursor-not-allowed'
                }`}
              >
                {uploadingB ? 'Uploading...' : uploadedB ? '✓ Uploaded' : 'Upload'}
              </button>
            </motion.div>
          </div>

          {/* Query Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-16"
          >
            <h2 className="text-sm font-medium text-gray-400 mb-4">Ask a Question</h2>
            
            <form onSubmit={handleQuery} className="space-y-4">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="What are the main differences between these documents?"
                className="w-full p-4 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-white/30 transition-colors resize-none backdrop-blur-sm"
                rows="4"
              />
              
              <button
                type="submit"
                disabled={!uploadedA || !uploadedB || loading || !question.trim()}
                className={`w-full py-4 rounded-lg font-medium transition-all ${
                  loading
                    ? 'bg-white/5 text-gray-500'
                    : uploadedA && uploadedB && question.trim()
                    ? 'bg-white text-black hover:bg-gray-100'
                    : 'bg-white/5 text-gray-600 cursor-not-allowed'
                }`}
              >
                {loading ? 'Thinking...' : 'Get Answer'}
              </button>
            </form>
          </motion.div>

          {/* Answer Section */}
          <AnimatePresence>
            {answer && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="p-8 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg"
              >
                <h2 className="text-sm font-medium text-gray-400 mb-4">Answer</h2>
                <div className="text-gray-300 leading-relaxed whitespace-pre-wrap text-sm">
                  {answer}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}