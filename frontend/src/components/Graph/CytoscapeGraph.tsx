import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';

interface GraphProps {
    data: {
        nodes: any[];
        edges: any[];
    };
    onNodeClick: (node: any) => void;
}

const CytoscapeGraph: React.FC<GraphProps> = ({ data, onNodeClick }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const cyRef = useRef<any>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const cy = cytoscape({
            container: containerRef.current,
            elements: [
                ...data.nodes.map(n => ({
                    data: {
                        id: n.id,
                        label: n.id, // Use ID as label
                        type: n.type,
                        description: n.description
                    }
                })),
                ...data.edges.map((e, idx) => ({
                    data: {
                        id: `e${idx}`,
                        source: e.source,
                        target: e.target,
                        label: e.label
                    }
                }))
            ],
            style: [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'background-color': '#6366f1',
                        'color': '#fff',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-family': 'Outfit, sans-serif',
                        'font-size': '10px',
                        'font-weight': 'bold',
                        'width': '50px',
                        'height': '50px',
                        'border-width': '3px',
                        'border-color': 'rgba(255,255,255,0.2)',
                        'overlay-padding': '6px',
                        'z-index': 10
                    }
                },
                {
                    selector: 'node:selected',
                    style: {
                        'border-width': '4px',
                        'border-color': '#fff',
                        'background-color': '#4f46e5'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': 'rgba(148, 163, 184, 0.3)',
                        'target-arrow-color': 'rgba(148, 163, 184, 0.3)',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '8px',
                        'color': '#94a3b8',
                        'text-rotation': 'autorotate',
                        'text-margin-y': -10,
                        'arrow-scale': 1.2,
                        'ghost': 'yes',
                        'ghost-offset-x': 1,
                        'ghost-offset-y': 1,
                        'ghost-opacity': 0.1
                    }
                },
                {
                    selector: 'node[type="Company"]',
                    style: {
                        'background-color': '#10b981',
                        'shape': 'round-rectangle'
                    }
                },
                {
                    selector: 'node[type="Person"]',
                    style: {
                        'background-color': '#f59e0b',
                        'shape': 'ellipse'
                    }
                },
                {
                    selector: 'node[type="Feature"]',
                    style: {
                        'background-color': '#8b5cf6',
                        'shape': 'diamond'
                    }
                },
                {
                    selector: 'node[type="Date"]',
                    style: {
                        'background-color': '#ef4444',
                        'shape': 'tag'
                    }
                }
            ],
            layout: {
                name: 'cose',
                idealEdgeLength: 100,
                nodeOverlap: 20,
                refresh: 20,
                fit: true,
                padding: 50,
                randomize: false,
                componentSpacing: 100,
                nodeRepulsion: 400000,
                edgeElasticity: 100,
                nestingFactor: 5,
                gravity: 80,
                numIter: 1000,
                initialTemp: 200,
                coolingFactor: 0.95,
                minTemp: 1.0
            }
        });

        cy.on('tap', 'node', (evt: any) => {
            onNodeClick(evt.target.data());
        });

        // Add interactivity
        cy.on('mouseover', 'node', (e: any) => {
            e.target.animate({
                style: { 'width': '60px', 'height': '60px' }
            }, { duration: 200 });
        });

        cy.on('mouseout', 'node', (e: any) => {
            e.target.animate({
                style: { 'width': '50px', 'height': '50px' }
            }, { duration: 200 });
        });

        cyRef.current = cy;

        return () => cy.destroy();
    }, [data]);

    return <div ref={containerRef} className="cy-container" />;
};

export default CytoscapeGraph;
