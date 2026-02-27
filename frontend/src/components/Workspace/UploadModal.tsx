import React, { useState } from 'react';
import { X, Upload, File, Loader } from 'lucide-react';
import { api } from '../../lib/api';
import { motion } from 'framer-motion';
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
        }
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
            className="ws-modal-overlay"
        >
            <motion.div
                initial={{ scale: 0.95, opacity: 0, y: 20 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.95, opacity: 0, y: 20 }}
                className="ws-modal-content"
            >
                <div className="ws-modal-header">
                    <h2>Upload Documents</h2>
                    <button onClick={onClose} className="ws-btn-ghost"><X size={20} /></button>
                </div>

                <div className="ws-modal-body">
                    <div className="upload-zone">
                        <input
                            type="file"
                            multiple
                            accept=".pdf,.txt"
                            onChange={handleFileChange}
                            id="file-input"
                            hidden
                        />
                        <label htmlFor="file-input" className="drop-area">
                            <Upload size={32} />
                            <p>Click to select PDF or TXT files</p>
                            <span>Maximum 10 documents total</span>
                        </label>
                    </div>

                    {files.length > 0 && (
                        <div className="file-preview" style={{ marginTop: '1.5rem', maxHeight: '200px', overflowY: 'auto' }}>
                            <h3 style={{ fontSize: '0.9rem', marginBottom: '0.5rem', color: 'var(--text-dim)' }}>Files Selected ({files.length}):</h3>
                            <ul style={{ listStyle: 'none', padding: 0 }}>
                                {files.map((f, i) => (
                                    <li key={i} className="ws-item-card" style={{ cursor: 'default' }}>
                                        <File size={16} className="ws-doc-icon" />
                                        <span className="ws-item-label">{f.name}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {error && <div className="error-text" style={{ marginTop: '1rem', color: 'var(--error)' }}>{error}</div>}
                </div>

                <div className="ws-modal-footer">
                    <button onClick={onClose} disabled={uploading} className="ws-btn ws-btn-secondary">Cancel</button>
                    <button onClick={handleUpload} disabled={uploading || files.length === 0} className="ws-btn ws-btn-primary">
                        {uploading ? <><Loader className="animate-spin" size={16} /> Processing...</> : "Process Documents"}
                    </button>
                </div>
            </motion.div>
        </motion.div>
    );
};

export default UploadModal;
