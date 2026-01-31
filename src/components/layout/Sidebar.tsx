import React, { useState } from 'react';
import {
    LayoutDashboard,
    Upload,
    Activity,
    Film,
    FileText,
    Smile,
    ShieldCheck,
    BrainCircuit,
    Search,
    AlertTriangle,
    GraduationCap,
    Download,
    Settings,
    ChevronLeft,
    ChevronRight
} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: Upload, label: 'Media Upload', path: '/upload' },
    { icon: Activity, label: 'AI Monitor', path: '/monitor' },
    { icon: Film, label: 'Timeline', path: '/timeline' },
    { icon: FileText, label: 'Script & Coverage', path: '/script' },
    { icon: Smile, label: 'Emotion', path: '/emotion' },
    { icon: ShieldCheck, label: 'Continuity', path: '/continuity' },
    { icon: BrainCircuit, label: 'Intelligence', path: '/intelligence' },
    { icon: Search, label: 'Semantic Search', path: '/search', highlight: true },
    { icon: AlertTriangle, label: 'Reshoot Risk', path: '/risk', badge: '3' },
    { icon: GraduationCap, label: 'Training', path: '/training' },
    { icon: Download, label: 'Export', path: '/export' },
    { icon: Settings, label: 'Settings', path: '/settings' },
];

export const Sidebar = () => {
    const [collapsed, setCollapsed] = useState(false);
    const location = useLocation();

    return (
        <div
            className={cn(
                "h-screen bg-surface border-r border-editor-border transition-all duration-300 flex flex-col",
                collapsed ? "w-16" : "w-64"
            )}
        >
            <div className="p-4 flex items-center justify-between border-b border-editor-border">
                {!collapsed && <span className="font-bold text-xl tracking-tight text-primary">SmartCut AI</span>}
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="p-1 hover:bg-editor-track rounded-md transition-colors"
                >
                    {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                </button>
            </div>

            <nav className="flex-1 overflow-y-auto py-4">
                {navItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={cn(
                                "flex items-center px-4 py-3 transition-colors group relative",
                                isActive ? "text-primary bg-primary/10" : "text-editor-muted hover:text-white hover:bg-editor-track"
                            )}
                        >
                            <item.icon size={20} className={cn(isActive ? "text-primary" : "text-editor-muted group-hover:text-white")} />
                            {!collapsed && (
                                <span className="ml-3 font-medium text-sm">{item.label}</span>
                            )}
                            {item.badge && !collapsed && (
                                <span className="ml-auto bg-danger text-white text-[10px] px-1.5 py-0.5 rounded-full font-bold">
                                    {item.badge}
                                </span>
                            )}
                            {collapsed && item.badge && (
                                <div className="absolute top-2 right-2 w-2 h-2 bg-danger rounded-full border border-surface" />
                            )}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-editor-border">
                <div className={cn("flex items-center", collapsed ? "justify-center" : "gap-3")}>
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center font-bold text-xs">
                        JD
                    </div>
                    {!collapsed && (
                        <div className="flex flex-col">
                            <span className="text-xs font-semibold">Jane Doe</span>
                            <span className="text-[10px] text-editor-muted">Senior Editor</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
