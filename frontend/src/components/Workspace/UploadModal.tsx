import React, { useState } from 'react';
import { X, Upload, File, Loader2, AlertCircle } from 'lucide-react';
import { api } from '../../lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import './Workspace.css';

interface UploadModalProps {
    workspaceId: string;
    onClose: () => void;
    onSuccess: () => void;
}

const UploadModal: React.FC<UploadModalProps> = ({ workspaceId, onClose, onSuccess }) => {
    const [files, setFiles] = useState<File[]>([]);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const selected = Array.from(e.target.files);
            if (files.length + selected.length > 10) {
                setError("Max 10 documents allowed per workspace");
                return;
            }
            setFiles(prev => [...prev, ...selected]);
            setError(null);
        }
    };

    const removeFile = (index: number) => {
        setFiles(prev => prev.filter((_, i) => i !== index));
    };

    const handleUpload = async () => {
        setUploading(true);
        setError(null);

        try {
            for (const file of files) {
                const formData = new FormData();
                formData.append('file', file);
                await api.postFormData(`/graph/${workspaceId}/upload`, formData);
            }
            onSuccess();
            onClose();
        } catch (err: any) {
            setError(err.message || "Upload failed");
        } finally {
            setUploading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="modal-overlay"
        >
            <motion.div
                initial={{ scale: 0.95, opacity: 0, y: 20 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.95, opacity: 0, y: 20 }}
                className="modal-content"
            >
                <div className="ws-modal-header">
                    <h2>Upload Documents</h2>
                    <button onClick={onClose} className="close-btn"><X size={20} /></button>
                </div>

                <div className="ws-modal-body" style={{ padding: 0 }}>
                    <div className="upload-zone">
                        <input
                            type="file"
                            multiple
                            accept=".pdf,.txt,.json"
                            onChange={handleFileChange}
                            id="file-input"
                            hidden
                        />
                        <label htmlFor="file-input" className="drop-area">
                            <Upload size={32} />
                            <p>Select PDF, TXT or JSON</p>
                            <span>Maximum 10 documents total</span>
                        </label>
                    </div>

                    <AnimatePresence>
                        {files.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="file-preview-container"
                                style={{ marginTop: '1.5rem', maxHeight: '200px', overflowY: 'auto' }}
                            >
                                <h3 style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>
                                    Selected Files ({files.length})
                                </h3>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                    {files.map((f, i) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            className="ws-item-card compact"
                                            style={{ margin: 0, justifyContent: 'space-between' }}
                                        >
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', overflow: 'hidden' }}>
                                                <File size={14} className="ws-doc-icon" />
                                                <span className="ws-item-label">{f.name}</span>
                                            </div>
                                            <button
                                                onClick={() => removeFile(i)}
                                                className="ws-btn-ghost"
                                                style={{ padding: '0.2rem' }}
                                            >
                                                <X size={14} />
                                            </button>
                                        </motion.div>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: 5 }}
                            animate={{ opacity: 1, y: 0 }}
                            style={{ marginTop: '1rem', color: 'var(--error)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', fontWeight: 600 }}
                        >
                            <AlertCircle size={14} />
                            <span>{error}</span>
                        </motion.div>
                    )}
                </div>

                <div className="ws-modal-footer">
                    <button onClick={onClose} disabled={uploading} className="logout-btn" style={{ background: 'transparent', border: '1px solid var(--border)', padding: '0.75rem 1.25rem' }}>
                        Cancel
                    </button>
                    <button
                        onClick={handleUpload}
                        disabled={uploading || files.length === 0}
                        className="primary-btn"
                        style={{ padding: '0.75rem 1.5rem', fontSize: '0.9rem' }}
                    >
                        {uploading ? (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                                <Loader2 className="animate-spin" size={16} />
                                <span>Processing...</span>
                            </div>
                        ) : "Process Knowledge"}
                    </button>
                </div>
            </motion.div>
        </motion.div>
    );
};

export default UploadModal;
