import React, { useState } from 'react';
import { Search, FileText, Upload, Plus, Database, Inbox } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './Workspace.css';

interface SidebarProps {
    onUploadClick: () => void;
    documents: any[];
    entities: any[];
    onEntityClick: (entity: any) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onUploadClick, documents, entities, onEntityClick }) => {
    const [searchTerm, setSearchTerm] = useState('');

    const filteredEntities = entities.filter(e => {
        const label = e.label || e.data?.label || '';
        return label.toLowerCase().includes(searchTerm.toLowerCase());
    });

    return (
        <aside className="ws-sidebar">
            {/* Documents Section */}
            <section className="ws-sidebar-section">
                <div className="ws-section-header">
                    <div className="ws-section-title">
                        <FileText size={16} />
                        <h3>Documents</h3>
                    </div>
                    <span className="ws-badge">{documents.length}/10</span>
                </div>

                <div className="ws-upload-card" onClick={onUploadClick}>
                    <div className="ws-upload-icon-wrapper">
                        <Upload size={20} />
                    </div>
                    <div className="ws-upload-text">
                        <p className="ws-upload-main">Upload Documents</p>
                        <p className="ws-upload-sub">PDF, TXT, or JSON</p>
                    </div>
                    <Plus size={16} className="ws-upload-plus" />
                </div>

                <div className="ws-scroll-area" style={{ maxHeight: '180px' }}>
                    <AnimatePresence>
                        {documents.length > 0 && documents.map((doc, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="ws-item-card compact"
                            >
                                <FileText size={14} className="ws-doc-icon" />
                                <span className="ws-item-label">{doc.file_name || doc.name}</span>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            </section>

            {/* Entities Section */}
            <section className="ws-sidebar-section entities">
                <div className="ws-section-header">
                    <div className="ws-section-title">
                        <Database size={16} />
                        <h3>Knowledge Base</h3>
                    </div>
                </div>

                <div className="ws-search-wrapper">
                    <Search size={16} />
                    <input
                        type="text"
                        className="ws-search-input"
                        placeholder="Filter entities..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <div className="ws-scroll-area">
                    {filteredEntities.length === 0 ? (
                        <div className="ws-empty-state-compact">
                            <Inbox size={32} />
                            <p>{searchTerm ? 'No results found' : 'No entities extracted'}</p>
                        </div>
                    ) : (
                        <div className="ws-entity-list">
                            {filteredEntities.map((entity, idx) => (
                                <div
                                    key={idx}
                                    className="ws-entity-item"
                                    onClick={() => onEntityClick(entity)}
                                >
                                    <div className={`ws-entity-marker ${entity.type?.toLowerCase() || 'default'}`} />
                                    <div className="ws-entity-info">
                                        <span className="ws-entity-name">{entity.label || entity.data?.label}</span>
                                        <span className="ws-entity-type-text">{entity.type || 'Entity'}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </section>
        </aside>
    );
};

export default Sidebar;
