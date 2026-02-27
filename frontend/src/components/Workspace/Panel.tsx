import React from 'react';
import { Edit, GitMerge, X } from 'lucide-react';

interface PanelProps {
    selectedEntity: any | null;
    onClose: () => void;
    onEdit: (entity: any) => void;
    onMerge: (entity: any) => void;
}

const Panel: React.FC<PanelProps> = ({ selectedEntity, onClose, onEdit, onMerge }) => {
    if (!selectedEntity) return null;

    return (
        <div className="entity-panel">
            <header className="panel-header">
                <h2>Entity Details</h2>
                <button onClick={onClose} className="close-btn"><X size={20} /></button>
            </header>

            <div className="panel-body">
                <div className="detail-item">
                    <label>Name</label>
                    <p>{selectedEntity.label}</p>
                </div>
                <div className="detail-item">
                    <label>Type</label>
                    <span className="type-badge">{selectedEntity.type}</span>
                </div>
                <div className="detail-item">
                    <label>Description</label>
                    <p>{selectedEntity.description || "No description available."}</p>
                </div>

                <div className="connected-nodes">
                    <h3>Connected Entities</h3>
                    {/* List connected nodes here if available in selectedEntity */}
                </div>

                <div className="source-snippets">
                    <h3>Source Snippets</h3>
                    {/* List snippets here */}
                </div>
            </div>

            <footer className="panel-footer">
                <button onClick={() => onEdit(selectedEntity)} className="edit-btn">
                    <Edit size={16} /> Edit
                </button>
                <button onClick={() => onMerge(selectedEntity)} className="merge-btn">
                    <GitMerge size={16} /> Merge
                </button>
            </footer>
        </div>
    );
};

export default Panel;
