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
    const cyRef = useRef<cytoscape.Core | null>(null);
    const resizeObserverRef = useRef<ResizeObserver | null>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const cy = cytoscape({
            container: containerRef.current,
            elements: [
                ...data.nodes.map(n => ({
                    data: {
                        id: n.id,
                        label: n.label || n.id,
                        type: n.type,
                        description: n.description
                    }
                })),
                ...data.edges.map((e, idx) => ({
                    data: {
                        id: e.id || `e${idx}`,
                        source: e.source,
                        target: e.target,
                        label: e.label
                    }
                }))
            ],
            style: [
                // ────────────────────────────────────────────────
                // Your original node/edge styles (unchanged)
                // ────────────────────────────────────────────────
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'background-color': '#6366f1',
                        'color': '#ffffff',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'text-wrap': 'wrap',
                        'text-max-width': '80px',
                        'font-family': 'Inter, sans-serif',
                        'font-size': '12px',
                        'font-weight': 600,
                        'width': 70,
                        'height': 70,
                        'border-width': 0,
                        'overlay-padding': 6,
                        'z-index': 10,
                        'shape': 'round-rectangle',
                        'shadow-blur': 12,
                        'shadow-color': 'rgba(0,0,0,0.25)',
                        'shadow-offset-x': 0,
                        'shadow-offset-y': 4,
                        'shadow-opacity': 0.3,
                        'transition-property': 'background-color, width, height, shadow-blur',
                        'transition-duration': 200
                    } as any
                },
                {
                    selector: 'node:selected',
                    style: { 'border-width': 3, 'border-color': '#ffffff', 'background-color': '#4f46e5' } as any
                },
                {
                    selector: 'node.hover',
                    style: { 'width': 80, 'height': 80, 'shadow-blur': 20 } as any
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': 'rgba(148, 163, 184, 0.35)',
                        'target-arrow-color': 'rgba(148, 163, 184, 0.6)',
                        'target-arrow-shape': 'vee',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': 10,
                        'color': '#94a3b8',
                        'text-rotation': 'autorotate',
                        'text-margin-y': -8,
                        'text-background-color': '#ffffff',
                        'text-background-opacity': 0.8,
                        'text-background-padding': 2,
                        'arrow-scale': 0.9,
                        'opacity': 0.9
                    } as any
                },
                // Type-based colors (unchanged)
                { selector: 'node[type="Company"]', style: { 'background-color': '#10b981' } as any },
                { selector: 'node[type="Person"]', style: { 'background-color': '#f59e0b', 'shape': 'ellipse' } as any },
                { selector: 'node[type="Feature"]', style: { 'background-color': '#8b5cf6' } as any },
                { selector: 'node[type="Date"]', style: { 'background-color': '#ef4444', 'shape': 'tag' } as any },
            ],
            layout: {
                name: 'cose',
                idealEdgeLength: 140,
                nodeOverlap: 10,
                componentSpacing: 150,
                nodeRepulsion: 450000,
                edgeElasticity: 120,
                gravity: 80,
                numIter: 1000,
                initialTemp: 200,
                coolingFactor: 0.95,
                minTemp: 1.0,
                fit: true,
                padding: 60,
                randomize: false,
                animate: true,
                animationDuration: 500
            } as any
        });

        cyRef.current = cy;

        // ────────────────────────────────────────────────
        // Event listeners
        // ────────────────────────────────────────────────
        cy.on('tap', 'node', evt => {
            onNodeClick(evt.target.data());
        });

        cy.on('mouseover', 'node', e => {
            e.target.addClass('hover');
            if (containerRef.current) containerRef.current.style.cursor = 'pointer';
        });

        cy.on('mouseout', 'node', e => {
            e.target.removeClass('hover');
            if (containerRef.current) containerRef.current.style.cursor = 'default';
        });

        // ────────────────────────────────────────────────
        // Reliable initial sizing & fitting
        // ────────────────────────────────────────────────
        const forceUpdate = () => {
            const cy = cyRef.current;
            const container = containerRef.current;
            if (!cy || !container || container.offsetWidth === 0) return;

            cy.resize();
            (cy as any).invalidateSize?.(); // Some versions/plugins might need this, or just trigger resize again
            cy.fit(undefined, 50); // 50px padding
            cy.center();
        };

        // Aggressive polling for the first 2 seconds to catch all layout stabilization
        const timers: any[] = [
            setTimeout(forceUpdate, 100),
            setTimeout(forceUpdate, 400),
            setTimeout(forceUpdate, 800),
            setTimeout(forceUpdate, 1500),
            setTimeout(forceUpdate, 2500),
        ];

        // ────────────────────────────────────────────────
        // Resize handling
        // ────────────────────────────────────────────────
        const handleResize = () => requestAnimationFrame(forceUpdate);

        if (typeof ResizeObserver !== 'undefined' && containerRef.current) {
            resizeObserverRef.current = new ResizeObserver(handleResize);
            resizeObserverRef.current.observe(containerRef.current);
        }

        window.addEventListener('resize', handleResize);

        // ────────────────────────────────────────────────
        // Cleanup
        // ────────────────────────────────────────────────
        return () => {
            timers.forEach(clearTimeout);
            window.removeEventListener('resize', handleResize);
            resizeObserverRef.current?.disconnect();
            cy.destroy();
        };
    }, [data, onNodeClick]);

    return (
        <div
            ref={containerRef}
            className="cy-container"
            style={{
                width: '100%',
                height: '100%',
                position: 'absolute',
                top: 0,
                left: 0,
                // For debugging – remove later
                // border: '1px dashed lime',
            }}
        />
    );
};

export default CytoscapeGraph;