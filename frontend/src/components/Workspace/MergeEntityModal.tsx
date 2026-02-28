import React, { useState } from 'react';
import { X, GitMerge, AlertTriangle, Check, Loader2, AlertCircle, Search } from 'lucide-react';
import { api } from '../../lib/api';
import { motion, AnimatePresence } from 'framer-motion';

interface MergeEntityModalProps {
    workspaceId: string;
    sourceEntity: any;
    allEntities: any[];
    onClose: () => void;
    onSuccess: () => void;
}

const MergeEntityModal: React.FC<MergeEntityModalProps> = ({ workspaceId, sourceEntity, allEntities, onClose, onSuccess }) => {
    const [targetEntityName, setTargetEntityName] = useState<string>('');
    const [merging, setMerging] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    const otherEntities = allEntities.filter(e => (e.label || e.id) !== (sourceEntity.label || sourceEntity.id));
    const filteredEntities = otherEntities.filter(e =>
        (e.label || e.id).toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleMerge = async () => {
        if (!targetEntityName) {
            setError("Please select a target entity to merge into");
            return;
        }

        setMerging(true);
        setError(null);

        try {
            await api.post(`/graph/${workspaceId}/merge?keep=${encodeURIComponent(targetEntityName)}&delete=${encodeURIComponent(sourceEntity.id || sourceEntity.label)}`, {});
            onSuccess();
            onClose();
        } catch (err: any) {
            setError(err.message || "Merge failed");
        } finally {
            setMerging(false);
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
                        <div style={{ background: 'rgba(245, 158, 11, 0.15)', padding: '0.5rem', borderRadius: '0.5rem', color: '#f59e0b' }}>
                            <GitMerge size={20} />
                        </div>
                        <h2>Merge Entities</h2>
                    </div>
                    <button onClick={onClose} className="close-btn" disabled={merging}>
                        <X size={20} />
                    </button>
                </div>

                <div className="ws-modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', padding: '0 0 1.5rem 0' }}>
                    <div style={{ background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.2)', padding: '1rem', borderRadius: 'var(--radius-lg)', display: 'flex', gap: '1rem' }}>
                        <AlertTriangle size={24} style={{ color: '#f59e0b', flexShrink: 0 }} />
                        <div style={{ fontSize: '0.85rem' }}>
                            <p style={{ fontWeight: 700, color: 'white', marginBottom: '0.25rem' }}>Review the Merge</p>
                            <p style={{ color: 'var(--text-dim)' }}>
                                You are merging <strong>{sourceEntity.label || sourceEntity.id}</strong> into another entity.
                                This entity will be deleted, and all its relationships will move to the target. <strong>This cannot be undone.</strong>
                            </p>
                        </div>
                    </div>

                    <div className="input-group" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <label style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                            Select Target Entity (Keep)
                        </label>
                        <div style={{ position: 'relative' }}>
                            <Search size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="text"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                placeholder="Search target entity..."
                                style={{ width: '100%', paddingLeft: '2.75rem' }}
                            />
                        </div>

                        <div style={{
                            maxHeight: '200px',
                            overflowY: 'auto',
                            background: 'rgba(2, 6, 23, 0.4)',
                            border: '1px solid var(--border)',
                            borderRadius: 'var(--radius-lg)',
                            marginTop: '0.5rem'
                        }}>
                            <AnimatePresence>
                                {filteredEntities.length === 0 ? (
                                    <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                                        No matching entities found
                                    </div>
                                ) : (
                                    filteredEntities.map((e, idx) => (
                                        <div
                                            key={idx}
                                            onClick={() => setTargetEntityName(e.label || e.id)}
                                            style={{
                                                padding: '0.75rem 1rem',
                                                cursor: 'pointer',
                                                display: 'flex',
                                                justifyContent: 'space-between',
                                                alignItems: 'center',
                                                background: targetEntityName === (e.label || e.id) ? 'var(--primary-glow)' : 'transparent',
                                                borderBottom: '1px solid var(--border)',
                                                transition: 'all 0.2s ease'
                                            }}
                                            className="merge-target-item"
                                        >
                                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                                <span style={{ fontWeight: 600, fontSize: '0.9rem', color: targetEntityName === (e.label || e.id) ? 'var(--primary)' : 'white' }}>
                                                    {e.label || e.id}
                                                </span>
                                                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>{e.type}</span>
                                            </div>
                                            {targetEntityName === (e.label || e.id) && <Check size={16} color="var(--primary)" />}
                                        </div>
                                    ))
                                )}
                            </AnimatePresence>
                        </div>
                    </div>

                    {error && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--error)', fontSize: '0.85rem', fontWeight: 600, background: 'rgba(239, 68, 68, 0.1)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
                            <AlertCircle size={16} />
                            <span>{error}</span>
                        </div>
                    )}
                </div>

                <div className="ws-modal-footer" style={{ marginTop: '0.5rem', padding: 0 }}>
                    <button onClick={onClose} className="logout-btn" disabled={merging} style={{ padding: '0.75rem 1.5rem' }}>
                        Cancel
                    </button>
                    <button
                        onClick={handleMerge}
                        disabled={merging || !targetEntityName}
                        className="primary-btn"
                        style={{
                            padding: '0.75rem 1.75rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.6rem',
                            background: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
                            boxShadow: '0 8px 16px -4px rgba(245, 158, 11, 0.3)'
                        }}
                    >
                        {merging ? (
                            <Loader2 size={18} className="animate-spin" />
                        ) : (
                            <GitMerge size={18} />
                        )}
                        <span>{merging ? 'Merging...' : 'Confirm Merge'}</span>
                    </button>
                </div>
            </motion.div>
        </motion.div>
    );
};

export default MergeEntityModal;
