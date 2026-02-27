import React, { useState } from 'react';
import { Search, FileText, Upload, Plus } from 'lucide-react';
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
            <section className="ws-sidebar-section" style={{ flex: '0 0 auto', maxHeight: '40%' }}>
                <div className="ws-section-header">
                    <h3>Documents ({documents.length} / 10)</h3>
                    <button onClick={onUploadClick} className="ws-btn-ghost">
                        <Plus size={18} />
                    </button>
                </div>
                <div className="ws-scroll-area">
                    {documents.length === 0 ? (
                        <div className="ws-empty-state">
                            <FileText size={24} />
                            <p style={{ fontSize: '0.85rem' }}>No documents uploaded yet.</p>
                        </div>
                    ) : (
                        documents.map((doc, idx) => (
                            <div key={idx} className="ws-item-card">
                                <FileText size={16} className="ws-doc-icon" />
                                <span className="ws-item-label">{doc.file_name || doc.name}</span>
                            </div>
                        ))
                    )}
                    <button onClick={onUploadClick} className="ws-btn ws-btn-secondary" style={{ width: '100%', marginTop: '0.5rem' }}>
                        <Upload size={16} /> Upload
                    </button>
                </div>
            </section>

            <section className="ws-sidebar-section" style={{ flex: 1 }}>
                <div className="ws-section-header">
                    <h3>Entities</h3>
                </div>
                <div className="ws-search-wrapper">
                    <Search size={18} />
                    <input
                        type="text"
                        className="ws-search-input"
                        placeholder="Search entities..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <div className="ws-scroll-area" style={{ flex: 1 }}>
                    {filteredEntities.length === 0 ? (
                        <div className="ws-empty-state">
                            <Plus size={24} />
                            <p style={{ fontSize: '0.85rem' }}>{searchTerm ? 'No matches found.' : 'No entities extracted yet.'}</p>
                        </div>
                    ) : (
                        filteredEntities.map((entity, idx) => (
                            <div
                                key={idx}
                                className="ws-item-card"
                                onClick={() => onEntityClick(entity)}
                            >
                                <div className="ws-entity-tag">{entity.type || entity.data?.type || 'Entity'}</div>
                                <span className="ws-item-label">{entity.label || entity.data?.label}</span>
                            </div>
                        ))
                    )}
                </div>
            </section>
        </aside>
    );
};

export default Sidebar;
