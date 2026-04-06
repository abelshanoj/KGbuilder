import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, AlertCircle } from 'lucide-react';
import { api } from '../../lib/api';
import './Chat.css';

interface Source {
    content: string;
    document_name: string;
}

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    sources?: Source[];
    createdAt: string;
}

interface ChatInterfaceProps {
    workspaceId: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ workspaceId }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, streamingMessageId]);

    const simulateStreaming = async (messageId: string, fullContent: string, sources: Source[]) => {
        setStreamingMessageId(messageId);
        
        // Simulating character by character stream
        let currentContent = '';
        const chars = fullContent.split('');
        
        for (let i = 0; i < chars.length; i++) {
            currentContent += chars[i];
            
            // Chunk updates to avoid re-rendering every single char if too slow
            // But we can do short micro-delays
            await new Promise(r => setTimeout(r, 10)); // 10ms per char
            
            setMessages(prev => prev.map(m => 
                m.id === messageId ? { ...m, content: currentContent } : m
            ));
        }
        
        // At the end, attach the sources
        setMessages(prev => prev.map(m => 
            m.id === messageId ? { ...m, content: fullContent, sources } : m
        ));
        
        setStreamingMessageId(null);
    };

    const handleSend = async () => {
        const query = input.trim();
        if (!query || loading) return;

        setInput('');
        setError(null);

        const userMsgId = Date.now().toString();
        const assistantMsgId = (Date.now() + 1).toString();

        const newUserMessage: Message = {
            id: userMsgId,
            role: 'user',
            content: query,
            createdAt: new Date().toISOString()
        };

        const placeholderAssistantMessage: Message = {
            id: assistantMsgId,
            role: 'assistant',
            content: '', // will be streamed into
            createdAt: new Date().toISOString()
        };

        setMessages(prev => [...prev, newUserMessage]);
        setLoading(true);

        try {
            // API Call matching correct contract
            const response = await api.post('/query', {
                workspace_id: workspaceId,
                query: query
            });

            // Add placeholder before streaming starts
            setMessages(prev => [...prev, placeholderAssistantMessage]);

            const finalAnswer = response.answer || "No response received.";
            const finalSources = response.sources || [];
            
            await simulateStreaming(assistantMsgId, finalAnswer, finalSources);
        } catch (err: any) {
            console.error("Chat error:", err);
            setError("Failed to fetch answer. Please try again.");
            // If failed, we should probably remove the placeholder msg if it was added
            setMessages(prev => prev.filter(m => m.id !== assistantMsgId));
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="chat-container">
            {messages.length === 0 ? (
                <div className="chat-empty-state">
                    <FileText size={48} opacity={0.5} />
                    <p>Ask something about your documents...</p>
                </div>
            ) : (
                <div className="chat-messages-area">
                    {messages.map(msg => (
                        <div key={msg.id} className={`chat-message ${msg.role}`}>
                            <div className="chat-bubble">
                                {msg.content}
                                {streamingMessageId === msg.id && <span className="typing-cursor">|</span>}
                            </div>
                            {msg.sources && msg.sources.length > 0 && (
                                <div className="chat-sources">
                                    <div className="chat-sources-title">Sources used:</div>
                                    {msg.sources.map((src, idx) => (
                                        <div key={idx} className="chat-source-item">
                                            <div className="chat-source-header">
                                                <FileText size={14} /> {src.document_name}
                                            </div>
                                            <div className="chat-source-content">
                                                "{src.content}"
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                    
                    {loading && !streamingMessageId && (
                        <div className="typing-indicator">
                            <div className="typing-dot"></div>
                            <div className="typing-dot"></div>
                            <div className="typing-dot"></div>
                        </div>
                    )}

                    {error && (
                        <div className="chat-error-inline">
                            <AlertCircle size={18} />
                            <span>{error}</span>
                            <button className="reply-btn" onClick={handleSend}>Retry</button>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            )}

            <div className="chat-input-area">
                <div className="chat-input-wrapper">
                    <textarea
                        className="chat-input"
                        placeholder="Type a message... (Press Enter to send)"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={loading}
                        rows={1}
                    />
                    <button 
                        className="chat-send-btn" 
                        onClick={handleSend}
                        disabled={!input.trim() || loading}
                    >
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
