import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, LayoutDashboard, Database, ChevronRight } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const Navbar: React.FC<{ workspaceName?: string }> = ({ workspaceName }) => {
    const { user, signOut } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await signOut();
        navigate('/login');
    };

    return (
        <motion.nav
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="navbar"
        >
            <div className="nav-left" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <Link to="/" className="logo">
                    <div style={{ background: 'var(--primary)', color: 'white', padding: '0.4rem', borderRadius: '0.6rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Database size={18} />
                    </div>
                    <span>KG Builder</span>
                </Link>

                {workspaceName && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--text-muted)' }}>
                        <ChevronRight size={16} />
                        <span style={{ color: 'var(--text-main)', fontWeight: 600, fontSize: '0.9rem' }}>{workspaceName}</span>
                    </div>
                )}
            </div>

            <div className="nav-right">
                {user && (
                    <>
                        <Link to="/" className="nav-link">
                            <LayoutDashboard size={16} />
                            <span>Dashboard</span>
                        </Link>

                        <div style={{ height: '24px', width: '1px', background: 'var(--border)', margin: '0 0.25rem' }} />

                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 500 }}>{user.email}</span>
                            <button onClick={handleLogout} className="logout-btn" title="Logout">
                                <LogOut size={16} />
                            </button>
                        </div>
                    </>
                )}
            </div>
        </motion.nav>
    );
};

export default Navbar;
