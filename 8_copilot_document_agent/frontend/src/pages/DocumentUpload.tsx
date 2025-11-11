import React, { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { uploadDocument } from '../services/api';

const DocumentUpload: React.FC = () => {
  const [documents, setDocuments] = useState<File[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const newFiles = Array.from(event.target.files);
      setDocuments(prevDocuments => [...prevDocuments, ...newFiles]);
    }
  };

  const processUpload = async () => {
    if (documents.length === 0) {
      toast.error('Selecione pelo menos um documento');
      return;
    }

    setUploading(true);
    let successCount = 0;
    let errorCount = 0;

    try {
      for (const file of documents) {
        try {
          const result = await uploadDocument(file);
          
          if (result.success) {
            toast.success(`Documento ${file.name} enviado com sucesso`, {
              autoClose: 3000, // Keep toast visible for 3 seconds
              onClose: () => {
                if (successCount === documents.length && errorCount === 0) {
                  navigate('/');
                }
              }
            });
            successCount++;
          } else {
            toast.error(`Erro ao enviar ${file.name}: ${result.error}`);
            errorCount++;
          }
        } catch (fileError) {
          console.error(`Erro específico no upload do arquivo ${file.name}:`, fileError);
          toast.error(`Erro crítico ao enviar ${file.name}`);
          errorCount++;
        }
      }
      
      // Provide summary of upload results
      if (successCount > 0 && errorCount === 0) {
        // If all uploads are successful, the navigation will happen in the toast onClose
        setDocuments([]);
      } else if (successCount > 0 && errorCount > 0) {
        toast.warn(`${successCount} documentos enviados, ${errorCount} falharam`, {
          autoClose: 3000
        });
      } else {
        toast.error('Nenhum documento foi enviado com sucesso');
      }
    } catch (error) {
      console.error('Erro global no processamento dos documentos:', error);
      toast.error('Erro crítico no processamento dos documentos');
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDrop = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    event.stopPropagation();
    
    if (event.dataTransfer.files) {
      const droppedFiles = Array.from(event.dataTransfer.files);
      setDocuments(prevDocuments => [...prevDocuments, ...droppedFiles]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const removeDocument = (indexToRemove: number) => {
    setDocuments(prevDocuments => 
      prevDocuments.filter((_, index) => index !== indexToRemove)
    );
  };

  return (
    <div className="document-upload">
      <Link to="/" className="back-button">
        <span className="back-button-icon">←</span>
        Back to Home
      </Link>

      <div className="upload-container">
        <div className="upload-header">
          <h2>Document Upload</h2>
          <p>Upload PDF and DOCX files for intelligent analysis</p>
        </div>

        <input 
          type="file" 
          ref={fileInputRef}
          className="file-upload-input"
          accept=".pdf,.docx"
          multiple 
          onChange={handleFileUpload} 
        />

        <label 
          className="file-upload-label"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={triggerFileInput}
        >
          <div className="file-upload-label-icon">📤</div>
          <p>Drag and drop files here, or click to select</p>
          <p style={{fontSize: '0.8rem', color: '#6c757d'}}>
            Supported formats: PDF, DOCX
          </p>
        </label>
        
        {documents.length > 0 && (
          <div className="document-list">
            <h3>Uploaded Documents</h3>
            <ul>
              {documents.map((doc, index) => (
                <li key={index}>
                  <span>{doc.name}</span>
                  <div>
                    <span className="status">Pending Indexing</span>
                    <button 
                      onClick={() => removeDocument(index)}
                      style={{
                        marginLeft: '10px', 
                        background: 'none', 
                        border: 'none', 
                        color: '#e74c3c',
                        cursor: 'pointer'
                      }}
                    >
                      🗑️
                    </button>
                  </div>
                </li>
              ))}
            </ul>
            <button 
              onClick={processUpload}
              disabled={uploading}
              className="upload-button"
            >
              {uploading ? 'Enviando...' : 'Enviar Documentos'}
            </button>
          </div>
        )}
        <ToastContainer />
      </div>
    </div>
  );
};

export default DocumentUpload;
