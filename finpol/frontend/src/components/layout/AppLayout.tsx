import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const AppLayout: React.FC = () => {
    return (
        <div className="flex h-screen w-full bg-[#f8fafc] overflow-hidden font-sans">
            <Sidebar />
            <div className="flex flex-col flex-1 h-full min-w-0">
                <Header />
                <main className="flex-1 overflow-auto p-6 md:p-8">
                    <div className="max-w-7xl mx-auto h-full">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
};
