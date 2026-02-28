import React, { useState } from 'react';
import { X, Save, Tag, AlignLeft, User, Loader2, AlertCircle } from 'lucide-react';
import { api } from '../../lib/api';
import { motion } from 'framer-motion';

interface EditEntityModalProps {
    workspaceId: string;
    entity: any;
    onClose: () => void;
    onSuccess: () => void;
}

const EditEntityModal: React.FC<EditEntityModalProps> = ({ workspaceId, entity, onClose, onSuccess }) => {
    const [name, setName] = useState(entity.label || entity.id);
    const [type, setType] = useState(entity.type || '');
    const [description, setDescription] = useState(entity.description || '');
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim() || !type.trim()) {
            setError("Name and Type are required");
            return;
        }

        setSaving(true);
        setError(null);

        try {
            // Backend expects: old_name, new_name, new_type, new_desc
            await api.put(`/graph/${workspaceId}/entity?old_name=${encodeURIComponent(entity.id)}&new_name=${encodeURIComponent(name.trim())}&new_type=${encodeURIComponent(type.trim())}&new_desc=${encodeURIComponent(description.trim())}`, {});
            onSuccess();
            onClose();
        } catch (err: any) {
            setError(err.message || "Failed to save changes");
        } finally {
            setSaving(false);
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
                style={{ maxWidth: '500px' }}
            >
                <div className="ws-modal-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{ background: 'var(--primary-glow)', padding: '0.5rem', borderRadius: '0.5rem', color: 'var(--primary)' }}>
                            <Tag size={20} />
                        </div>
                        <h2>Edit Entity</h2>
                    </div>
                    <button onClick={onClose} className="close-btn" disabled={saving}>
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSave} className="ws-modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', padding: '0 0 1.5rem 0' }}>
                    <div className="input-group" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <label style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                            Entity Name
                        </label>
                        <div style={{ position: 'relative' }}>
                            <User size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Enter entity name..."
                                style={{ width: '100%', paddingLeft: '2.75rem' }}
                                required
                            />
                        </div>
                    </div>

                    <div className="input-group" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <label style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                            Entity Type
                        </label>
                        <div style={{ position: 'relative' }}>
                            <Tag size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="text"
                                value={type}
                                onChange={(e) => setType(e.target.value)}
                                placeholder="Person, Company, Concept, etc."
                                style={{ width: '100%', paddingLeft: '2.75rem' }}
                                required
                            />
                        </div>
                    </div>

                    <div className="input-group" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <label style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                            Description
                        </label>
                        <div style={{ position: 'relative' }}>
                            <AlignLeft size={16} style={{ position: 'absolute', left: '1rem', top: '1rem', color: 'var(--text-muted)' }} />
                            <textarea
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder="Brief summary of this entity..."
                                rows={4}
                                style={{
                                    width: '100%',
                                    padding: '0.9rem 1.25rem 0.9rem 2.75rem',
                                    background: 'rgba(2, 6, 23, 0.6)',
                                    border: '1px solid var(--border)',
                                    borderRadius: 'var(--radius-lg)',
                                    color: 'white',
                                    outline: 'none',
                                    resize: 'none',
                                    fontSize: '0.95rem'
                                }}
                            />
                        </div>
                    </div>

                    {error && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--error)', fontSize: '0.85rem', fontWeight: 600, background: 'rgba(239, 68, 68, 0.1)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
                            <AlertCircle size={16} />
                            <span>{error}</span>
                        </div>
                    )}

                    <div className="ws-modal-footer" style={{ marginTop: '0.5rem', padding: 0 }}>
                        <button type="button" onClick={onClose} className="logout-btn" disabled={saving} style={{ padding: '0.75rem 1.5rem' }}>
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={saving}
                            className="primary-btn"
                            style={{ padding: '0.75rem 1.75rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}
                        >
                            {saving ? (
                                <Loader2 size={18} className="animate-spin" />
                            ) : (
                                <Save size={18} />
                            )}
                            <span>{saving ? 'Saving...' : 'Save Changes'}</span>
                        </button>
                    </div>
                </form>
            </motion.div>
        </motion.div>
    );
};

export default EditEntityModal;
