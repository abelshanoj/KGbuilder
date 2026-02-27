import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, Home, User as UserIcon } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar: React.FC<{ workspaceName?: string }> = ({ workspaceName }) => {
    const { user, signOut } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await signOut();
        navigate('/login');
    };

    return (
        <nav className="navbar">
            <div className="nav-left">
                <Link to="/" className="logo">KG Builder</Link>
                {workspaceName && (
                    <div className="breadcrumb">
                        <span>/</span>
                        <span className="workspace-title">{workspaceName}</span>
                    </div>
                )}
            </div>
            <div className="nav-right">
                {user && (
                    <>
                        <Link to="/" className="nav-link"><Home size={20} /> Dashboard</Link>
                        <div className="profile-badge">
                            <UserIcon size={20} />
                            <span>{user.email}</span>
                        </div>
                        <button onClick={handleLogout} className="logout-btn">
                            <LogOut size={20} /> Logout
                        </button>
                    </>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
