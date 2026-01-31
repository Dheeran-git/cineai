import React from 'react';
import { Sidebar } from './Sidebar';
import { StatusBar } from './StatusBar';
import { Outlet } from 'react-router-dom';

export const MainLayout = () => {
    return (
        <div className="flex h-screen w-screen overflow-hidden bg-background text-editor-text">
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0">
                <main className="flex-1 relative overflow-auto">
                    <Outlet />
                </main>
                <StatusBar />
            </div>
        </div>
    );
};
