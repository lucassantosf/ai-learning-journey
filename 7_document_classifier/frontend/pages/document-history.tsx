import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { apiService, DocumentHistoryItem } from '../services/api';
import styles from '../styles/pages/document-history.module.css';
import Header from '../components/Header';
import BackHomeButton from "../components/BackHomeButton";

const documentCategories = [
  'contracts', 
  'invoices', 
  'resumes', 
  'ocr_tests', 
  'other'
];

const DocumentHistoryPage: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retrainingStatus, setRetrainingStatus] = useState<'idle' | 'training' | 'success' | 'error'>('idle');
  const [confirmationModal, setConfirmationModal] = useState<{
    show: boolean;
    documentId?: string;
    currentCategory?: string;
    newCategory?: string;
    notes?: string;
  }>({ show: false });

  useEffect(() => {
    fetchDocumentHistory();
  }, []);

  const fetchDocumentHistory = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const historyData = await apiService.getDocumentHistory();
      setDocuments(historyData);
      setIsLoading(false);
    } catch (err) {
      setError('Failed to fetch document history. Please try again later.');
      setIsLoading(false);
    }
  };

  const handleCategoryChangeRequest = (documentId: string, newCategory: string) => {
    // Open confirmation modal
    setConfirmationModal({
      show: true,
      documentId,
      currentCategory: documents.find(doc => doc.id === documentId)?.current_category,
      newCategory,
      notes: '' // Initialize notes as empty string
    });
  };

  const handleCategoryChange = async () => {
    if (!confirmationModal.documentId || !confirmationModal.newCategory) return;

    // Validate notes have at least 5 characters
    if (!confirmationModal.notes || confirmationModal.notes.trim().length < 5) {
      setError('Justification must be at least 5 characters long');
      return;
    }

    try {
      await apiService.sendDocumentFeedback(
        confirmationModal.documentId, 
        confirmationModal.newCategory,
        confirmationModal.notes
      );
      // Refresh the document history after updating
      fetchDocumentHistory();
      // Close the modal
      setConfirmationModal({ show: false });
    } catch (err) {
      setError('Failed to update document category');
      setConfirmationModal({ show: false });
    }
  };

  const closeConfirmationModal = () => {
    setConfirmationModal({ show: false });
  };

  const handleNotesChange = (notes: string) => {
    setConfirmationModal(prev => ({
      ...prev,
      notes
    }));
  };

  const handleRetrain = async () => {
    try {
      setRetrainingStatus('training');
      await apiService.retrainModel();
      setRetrainingStatus('success');
      setTimeout(() => setRetrainingStatus('idle'), 3000);
    } catch (err) {
      setRetrainingStatus('error');
      setError('Failed to retrain the model');
      setTimeout(() => setRetrainingStatus('idle'), 3000);
    }
  };

  const renderRetrainingButton = () => {
    switch (retrainingStatus) {
      case 'training':
        return <button className={styles.retrainingButton} disabled>Retraining...</button>;
      case 'success':
        return <button className={styles.retrainedSuccessButton} disabled>Retrained Successfully!</button>;
      case 'error':
        return <button className={styles.retrainErrorButton} disabled>Retrain Failed</button>;
      default:
        return (
          <button 
            onClick={handleRetrain} 
            className={styles.retrainButton}
          >
            Retrain Model
          </button>
        );
    }
  };

  if (isLoading) return <div className={styles.loadingContainer}>Loading...</div>;

  return (
    <div className={styles.container}>
      <Head>
        <title>Document History | Document Classifier</title>
        <meta name="description" content="View and manage your document classification history" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Header 
        title="Document Classifier" 
        pageTitle="Document History" 
        description="View and manage uploaded documents"
      />
      
      <main className={styles.main}>
        {error && <div className={styles.errorBanner}>{error}</div>}

        <div className={styles.retrainingContainer}>
          {renderRetrainingButton()}
        </div>

        <BackHomeButton />

        {documents.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No documents have been uploaded yet.</p>
          </div>
        ) : (
          <div className={styles.documentList}>
            {documents.map((doc) => (
              <div key={doc.id} className={styles.documentItem}>
                <div className={styles.documentInfo}>
                  <span className={styles.filename}>{doc.filename}</span>
                  <span className={styles.uploadDate}>
                    Uploaded: {new Date(doc.upload_date).toLocaleString()}
                  </span>
                </div>
                <div className={styles.documentActions}>
                  <select 
                    value={doc.current_category} 
                    onChange={(e) => handleCategoryChangeRequest(doc.id, e.target.value)}
                    className={styles.categorySelect}
                  >
                    {documentCategories.map((category) => (
                      <option key={category} value={category}>
                        {category}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Confirmation Modal */}
        {confirmationModal.show && (
          <div className={styles.modalOverlay}>
            <div className={styles.modalContent}>
              <h2>Confirm Category Change</h2>
              <p>
                Are you sure you want to change the category of this document 
                from <strong>{confirmationModal.currentCategory}</strong> 
                to <strong>{confirmationModal.newCategory}</strong>?
              </p>
              <textarea 
                id="justification"
                className={styles.modalNotesTextarea}
                value={confirmationModal.notes || ''}
                onChange={(e) => handleNotesChange(e.target.value)}
                placeholder="Provide justification for changing the category (Required)"
                required
              />
              <div className={styles.modalButtons}>
                <button 
                  onClick={handleCategoryChange} 
                  className={`${styles.confirmButton} ${confirmationModal.notes && confirmationModal.notes.trim().length >= 5 ? styles.enabled : ''}`}
                  disabled={!confirmationModal.notes || confirmationModal.notes.trim().length < 5}
                >
                  {confirmationModal.notes && confirmationModal.notes.trim().length >= 5 ? '✓ Confirm' : 'Confirm'}
                </button>
                <button 
                  onClick={closeConfirmationModal} 
                  className={styles.cancelButton}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default DocumentHistoryPage;
