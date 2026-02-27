import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import { Plus, Clock, FileText, Share2, ArrowRight, Layers } from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

interface Workspace {
    id: string;
    name: string;
    created_at: string;
    doc_count: number;
    entity_count: number;
}

const DashboardPage: React.FC = () => {
    const { user } = useAuth();
    const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
    const [showModal, setShowModal] = useState(false);
    const [newWorkspaceName, setNewWorkspaceName] = useState('');

    useEffect(() => {
        if (user) fetchWorkspaces();
    }, [user]);

    const fetchWorkspaces = async () => {
        try {
            const data = await api.get('/workspaces');
            if (data) setWorkspaces(data);
        } catch (error) {
            console.error('Failed to fetch workspaces:', error);
        }
    };

    const createWorkspace = async () => {
        if (!newWorkspaceName.trim()) return;
        try {
            const data = await api.post('/workspaces', { name: newWorkspaceName });
            if (data) {
                setWorkspaces([data, ...workspaces.slice(0, 4)]);
                setShowModal(false);
                setNewWorkspaceName('');
            }
        } catch (error) {
            console.error('Failed to create workspace:', error);
        }
    };

    return (
        <div className="dashboard-container">
            <Navbar />
            <motion.main
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="dashboard-content"
            >
                <header className="dashboard-header">
                    <div>
                        <h1>Dashboard</h1>
                        <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>Manage your knowledge workspaces</p>
                    </div>
                    <button onClick={() => setShowModal(true)} className="create-btn">
                        <Plus size={20} strokeWidth={3} /> New Workspace
                    </button>
                </header>

                <section className="workspaces-grid">
                    {workspaces.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="empty-state"
                            style={{ gridColumn: '1/-1', textAlign: 'center', padding: '10rem 0' }}
                        >
                            <Layers size={64} color="var(--border)" style={{ marginBottom: '2rem' }} />
                            <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>No Workspaces Yet</h2>
                            <p style={{ color: 'var(--text-muted)' }}>Create your first workspace to start building a knowledge graph.</p>
                        </motion.div>
                    ) : (
                        workspaces.map((ws, index) => (
                            <motion.div
                                key={ws.id}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ duration: 0.4, delay: index * 0.1 }}
                                className="workspace-card"
                            >
                                <h3>{ws.name}</h3>
                                <div className="ws-meta">
                                    <div className="meta-item">
                                        <Clock size={16} />
                                        <span>{new Date(ws.created_at).toLocaleDateString()}</span>
                                    </div>
                                    <div className="meta-item">
                                        <FileText size={16} />
                                        <span>{ws.doc_count || 0} Docs</span>
                                    </div>
                                    <div className="meta-item" style={{ gridColumn: 'span 2' }}>
                                        <Share2 size={16} />
                                        <span>{ws.entity_count || 0} Entities Extracted</span>
                                    </div>
                                </div>
                                <Link to={`/workspace/${ws.id}`} className="open-btn">
                                    Open Workspace <ArrowRight size={18} style={{ marginLeft: 'auto' }} />
                                </Link>
                            </motion.div>
                        ))
                    )}
                </section>
            </motion.main>

            <AnimatePresence>
                {showModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="modal-overlay"
                    >
                        <motion.div
                            initial={{ scale: 0.9, y: 20 }}
                            animate={{ scale: 1, y: 0 }}
                            exit={{ scale: 0.9, y: 20 }}
                            className="modal-content"
                        >
                            <h2>New Workspace</h2>
                            <div className="auth-form" style={{ marginTop: 0 }}>
                                <input
                                    type="text"
                                    placeholder="Enter a name for your workspace..."
                                    value={newWorkspaceName}
                                    autoFocus
                                    onChange={(e) => setNewWorkspaceName(e.target.value)}
                                />
                                <div className="modal-actions" style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                                    <button onClick={() => setShowModal(false)} className="secondary-btn" style={{ flex: 1 }}>Cancel</button>
                                    <button onClick={createWorkspace} className="primary-btn" style={{ flex: 1 }}>Create Workspace</button>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default DashboardPage;
