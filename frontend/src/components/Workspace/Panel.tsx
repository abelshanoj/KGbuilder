import React from 'react';
import { Edit, GitMerge, X, Info, Tag, AlignLeft, Link2 } from 'lucide-react';

interface PanelProps {
    selectedEntity: any | null;
    onClose: () => void;
    onEdit: (entity: any) => void;
    onMerge: (entity: any) => void;
}

const Panel: React.FC<PanelProps> = ({ selectedEntity, onClose, onEdit, onMerge }) => {
    if (!selectedEntity) return null;

    return (
        <div className="entity-panel visible">
            <header className="panel-header">
                <div className="header-title">
                    <Info size={18} className="header-icon" />
                    <h2>Entity Details</h2>
                </div>
                <button onClick={onClose} className="close-btn" aria-label="Close panel">
                    <X size={20} />
                </button>
            </header>

            <div className="panel-body">
                <div className="entity-card">
                    <div className="entity-main-info">
                        <div className="entity-header-row">
                            <h1 className="entity-title">{selectedEntity.label}</h1>
                            <span className={`type-badge ${selectedEntity.type?.toLowerCase()}`}>
                                <Tag size={12} />
                                {selectedEntity.type || 'Unknown'}
                            </span>
                        </div>
                    </div>

                    <div className="detail-section">
                        <div className="section-label">
                            <AlignLeft size={14} />
                            <span>Description</span>
                        </div>
                        <p className="entity-description">
                            {selectedEntity.description || "No description provided for this entity."}
                        </p>
                    </div>

                    <div className="detail-section">
                        <div className="section-label">
                            <Link2 size={14} />
                            <span>Connections</span>
                        </div>
                        <div className="connections-placeholder">
                            <p>No connections to display yet.</p>
                        </div>
                    </div>
                </div>
            </div>

            <footer className="panel-footer">
                <button onClick={() => onEdit(selectedEntity)} className="panel-btn edit">
                    <Edit size={16} />
                    <span>Edit Entity</span>
                </button>
                <button onClick={() => onMerge(selectedEntity)} className="panel-btn merge">
                    <GitMerge size={16} />
                    <span>Merge</span>
                </button>
            </footer>
        </div>
    );
};

export default Panel;
