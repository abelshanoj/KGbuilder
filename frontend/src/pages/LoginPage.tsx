import React, { useState } from 'react';
import { supabase } from '../lib/supabase';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, Mail, ArrowRight } from 'lucide-react';

const LoginPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const handleSignIn = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) setError(error.message);
        else navigate('/');
        setLoading(false);
    };

    return (
        <div className="auth-container">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="auth-card"
            >
                <h1>Welcome Back</h1>
                <p>Sign in to continue to your Knowledge Graph</p>
                {error && <div className="error-text" style={{ color: 'var(--error)', marginBottom: '1rem', textAlign: 'center' }}>{error}</div>}

                <form className="auth-form" onSubmit={handleSignIn}>
                    <div style={{ position: 'relative' }}>
                        <Mail size={18} style={{ position: 'absolute', left: '1rem', top: '1.1rem', color: 'var(--text-muted)' }} />
                        <input
                            type="email"
                            placeholder="Email Address"
                            value={email}
                            required
                            style={{ paddingLeft: '3rem', width: '100%' }}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    <div style={{ position: 'relative' }}>
                        <Lock size={18} style={{ position: 'absolute', left: '1rem', top: '1.1rem', color: 'var(--text-muted)' }} />
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            required
                            style={{ paddingLeft: '3rem', width: '100%' }}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <button type="submit" disabled={loading} className="primary-btn">
                        {loading ? 'Authenticating...' : 'Sign In'}
                    </button>
                    <div className="auth-footer">
                        New here? <Link to="/signup">Create an account <ArrowRight size={14} style={{ display: 'inline', marginLeft: '4px' }} /></Link>
                    </div>
                </form>
            </motion.div>
        </div>
    );
};

export default LoginPage;
