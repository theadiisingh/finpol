import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Receipt, ShieldCheck, FileText } from 'lucide-react';
import { clsx } from 'clsx';

export const Sidebar: React.FC = () => {
    const navItems = [
        { to: '/', label: 'Dashboard', icon: LayoutDashboard },
        { to: '/transactions', label: 'Transactions', icon: Receipt },
        { to: '/compliance', label: 'Compliance', icon: ShieldCheck },
        { to: '/bulk-reports', label: 'Bulk Reports', icon: FileText },
    ];

    return (
        <aside className="w-64 bg-[#0f172a] text-slate-300 flex flex-col h-full border-r border-slate-800 hidden md:flex">
            <div className="p-6 flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                    <ShieldCheck className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-white tracking-wide">FinPol</span>
            </div>

            <nav className="flex-1 px-4 space-y-2 mt-4">
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) =>
                            clsx(
                                'flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors',
                                isActive
                                    ? 'bg-blue-600/10 text-blue-500 font-medium'
                                    : 'hover:bg-slate-800/50 hover:text-white'
                            )
                        }
                    >
                        <item.icon className="w-5 h-5" />
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="p-4 border-t border-slate-800">
                <div className="text-xs text-slate-500 text-center">
                    FinPol Compliance v1.0
                </div>
            </div>
        </aside>
    );
};
