import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ChatInterface from '../components/Chat/ChatInterface';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import { ArrowLeft, Loader2 } from 'lucide-react';

interface Workspace {
    id: string;
    name: string;
}

const WorkspaceChatPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { isInitialized, user } = useAuth();
    
    const [workspace, setWorkspace] = useState<Workspace | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isInitialized && user && id) {
            fetchWorkspace();
        }
    }, [isInitialized, user, id]);

    const fetchWorkspace = async () => {
        try {
            const ws = await api.get(`/workspaces/${id}`);
            setWorkspace(ws);
        } catch (err) {
            console.error("Failed to fetch workspace:", err);
            // Optionally redirect if critical
        } finally {
            setLoading(false);
        }
    };

    if (!isInitialized || !user || loading) {
        return (
            <div className="ws-page-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Loader2 size={48} className="animate-spin" color="var(--primary)" />
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="ws-page-container"
            style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}
        >
            <Navbar workspaceName={workspace?.name} />
            
            <div className="chat-page-header" style={{
                display: 'flex',
                alignItems: 'center',
                padding: '1rem 2rem',
                borderBottom: '1px solid var(--border)',
                background: 'var(--bg-surface)'
            }}>
                <button 
                    onClick={() => navigate(`/workspace/${id}`)}
                    className="back-btn"
                    style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        fontSize: '0.9rem',
                        fontWeight: 600
                    }}
                >
                    <ArrowLeft size={18} />
                    Back to Knowledge Graph
                </button>
            </div>

            <main className="chat-page-main" style={{ flex: 1, overflow: 'hidden', display: 'flex', justifyContent: 'center', background: '#010409' }}>
                {id && <ChatInterface workspaceId={id} />}
            </main>
        </motion.div>
    );
};

export default WorkspaceChatPage;
