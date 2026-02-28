import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Workspace/Sidebar';
import Panel from '../components/Workspace/Panel';
import CytoscapeGraph from '../components/Graph/CytoscapeGraph';
import UploadModal from '../components/Workspace/UploadModal';
import { api, ApiError } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, AlertCircle, RefreshCcw } from 'lucide-react';
import '../components/Workspace/Workspace.css';

import EditEntityModal from '../components/Workspace/EditEntityModal';
import MergeEntityModal from '../components/Workspace/MergeEntityModal';

const WorkspacePage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { isInitialized, user } = useAuth();

    const [workspace, setWorkspace] = useState<any>(null);
    const [graphData, setGraphData] = useState<{ nodes: any[], edges: any[] }>({ nodes: [], edges: [] });
    const [selectedEntity, setSelectedEntity] = useState<any | null>(null);
    const [showUpload, setShowUpload] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showMergeModal, setShowMergeModal] = useState(false);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<{ status?: number; message: string } | null>(null);

    const fetchWorkspaceData = useCallback(async (isRetry = false) => {
        if (!id) return;

        setLoading(true);
        if (isRetry) setError(null);

        try {
            // Fetch workspace details and graph in parallel for performance
            // Use timestamp to bypass any caching for the graph data
            const [ws, graph] = await Promise.all([
                api.get(`/workspaces/${id}`),
                api.get(`/workspaces/${id}/graph?t=${Date.now()}`)
            ]);

            setWorkspace(ws);
            setGraphData(graph || { nodes: [], edges: [] });
            setError(null);
        } catch (err: any) {
            console.error("Workspace fetch failed:", err);

            if (err instanceof ApiError) {
                // Redirect ONLY on definitive auth/existence failures
                if (err.status === 401 || err.status === 403 || err.status === 404) {
                    navigate('/', { replace: true });
                    return;
                }
                setError({ status: err.status, message: "Server encountered an error while loading workspace." });
            } else {
                setError({ message: "Failed to connect to the server. Please check your connection." });
            }
        } finally {
            setLoading(false);
        }
    }, [id, navigate]);

    // Added helper to clear selection before refresh as requested
    const handleRefreshWithClear = useCallback(async () => {
        setSelectedEntity(null);
        await fetchWorkspaceData();
    }, [fetchWorkspaceData]);

    useEffect(() => {
        // Wait for auth to be definitively resolved before fetching
        if (isInitialized && user && id) {
            fetchWorkspaceData();
        }
    }, [isInitialized, user, id, fetchWorkspaceData]);

    const handleNodeClick = (node: any) => setSelectedEntity(node);
    const handlePanelClose = () => setSelectedEntity(null);

    // If auth is not ready or user is missing, the ProtectedRoute in App.tsx handles the major layout.
    // However, if we reach here while auth is still hydrating, we show a clean local loader.
    if (!isInitialized || !user) {
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
        >
            <Navbar workspaceName={workspace?.name} />

            <div className="ws-main-layout">
                <motion.div
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    style={{ height: '100%', display: 'flex' }}
                >
                    <Sidebar
                        onUploadClick={() => setShowUpload(true)}
                        documents={[]}
                        entities={graphData.nodes}
                        onEntityClick={handleNodeClick}
                    />
                </motion.div>

                <main className="ws-graph-container">
                    <AnimatePresence mode="wait">
                        {loading ? (
                            <motion.div
                                key="loader"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="loading-overlay"
                                style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '1rem' }}
                            >
                                <Loader2 size={48} className="animate-spin" color="var(--primary)" />
                                <p style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Building Knowledge Graph...</p>
                            </motion.div>
                        ) : error ? (
                            <motion.div
                                key="error"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="error-state-ui"
                                style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '1.5rem', textAlign: 'center', padding: '2rem' }}
                            >
                                <div className="error-icon-wrapper" style={{ background: 'var(--bg-card)', padding: '1.5rem', borderRadius: '50%', border: '1px solid var(--border)' }}>
                                    <AlertCircle size={48} color="var(--error)" />
                                </div>
                                <div>
                                    <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Failed to Load Workspace</h2>
                                    <p style={{ color: 'var(--text-muted)', maxWidth: '400px' }}>{error.message}</p>
                                </div>
                                <button
                                    onClick={() => fetchWorkspaceData(true)}
                                    className="primary-btn"
                                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                                >
                                    <RefreshCcw size={18} /> Retry Connection
                                </button>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="graph"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="ws-graph-wrapper"
                            >
                                <CytoscapeGraph data={graphData} onNodeClick={handleNodeClick} />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </main>

                <AnimatePresence>
                    {selectedEntity && (
                        <motion.div
                            initial={{ x: 300, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            exit={{ x: 300, opacity: 0 }}
                            className="ws-panel-container"
                            style={{ height: '100%', width: '380px', borderLeft: '1px solid var(--border)', background: 'var(--bg-card)' }}
                        >
                            <Panel
                                selectedEntity={selectedEntity}
                                onClose={handlePanelClose}
                                onEdit={() => setShowEditModal(true)}
                                onMerge={() => setShowMergeModal(true)}
                            />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <AnimatePresence>
                {showUpload && (
                    <UploadModal
                        workspaceId={id!}
                        onClose={() => setShowUpload(false)}
                        onSuccess={fetchWorkspaceData}
                    />
                )}
                {showEditModal && selectedEntity && (
                    <EditEntityModal
                        workspaceId={id!}
                        entity={selectedEntity}
                        onClose={() => setShowEditModal(false)}
                        onSuccess={handleRefreshWithClear}
                    />
                )}
                {showMergeModal && selectedEntity && (
                    <MergeEntityModal
                        workspaceId={id!}
                        sourceEntity={selectedEntity}
                        allEntities={graphData.nodes}
                        onClose={() => setShowMergeModal(false)}
                        onSuccess={handleRefreshWithClear}
                    />
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default WorkspacePage;
