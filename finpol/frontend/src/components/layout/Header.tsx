import React from 'react';
import { Bell, Search, User } from 'lucide-react';

export const Header: React.FC = () => {
    return (
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 sticky top-0 z-10">
            <div className="flex items-center bg-slate-100 rounded-lg px-3 py-2 w-96 focus-within:ring-2 focus-within:ring-blue-500/50 transition-all">
                <Search className="w-4 h-4 text-slate-400 mr-2" />
                <input
                    type="text"
                    placeholder="Search transactions, users, or risks..."
                    className="bg-transparent border-none outline-none text-sm text-slate-700 w-full placeholder:text-slate-400"
                />
            </div>

            <div className="flex items-center space-x-4">
                <button className="relative p-2 text-slate-400 hover:bg-slate-100 rounded-full transition-colors">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"></span>
                </button>

                <div className="h-8 w-px bg-slate-200"></div>

                <button className="flex items-center space-x-3 hover:bg-slate-50 p-1.5 rounded-lg transition-colors">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700">
                        <User className="w-4 h-4" />
                    </div>
                    <div className="text-sm text-left hidden sm:block">
                        <div className="font-medium text-slate-700">Admin User</div>
                        <div className="text-xs text-slate-500">Compliance Officer</div>
                    </div>
                </button>
            </div>
        </header>
    );
};
