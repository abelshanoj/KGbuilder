import React, { useState } from 'react';
import { supabase } from '../lib/supabase';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, Mail, ArrowLeft } from 'lucide-react';

const SignupPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const handleSignUp = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) {
            setError(error.message);
        } else {
            alert('Signup successful! Check your email for confirmation.');
            navigate('/login');
        }
        setLoading(false);
    };

    return (
        <div className="auth-container">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="auth-card"
            >
                <h1>Create Account</h1>
                <p>Start your journey into knowledge graphs</p>
                {error && <div className="error-text" style={{ color: 'var(--error)', marginBottom: '1rem', textAlign: 'center' }}>{error}</div>}

                <form className="auth-form" onSubmit={handleSignUp}>
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
                        {loading ? 'Creating Account...' : 'Sign Up'}
                    </button>
                    <div className="auth-footer">
                        <Link to="/login" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}>
                            <ArrowLeft size={14} /> Back to Login
                        </Link>
                    </div>
                </form>
            </motion.div>
        </div>
    );
};

export default SignupPage;
