import React from 'react';
import { Cpu, Cpu as Gpu, Server, CheckCircle2 } from 'lucide-react';

export const StatusBar = () => {
    return (
        <div className="h-8 bg-editor-bg border-t border-editor-border flex items-center justify-between px-4 text-[10px] uppercase tracking-wider font-semibold text-editor-muted">
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
                    <span>System Ready</span>
                </div>
                <div className="h-4 w-[1px] bg-editor-border" />
                <div className="flex items-center gap-1.5">
                    <Server size={12} />
                    <span>Local Engine: 1.2.4-stable</span>
                </div>
            </div>

            <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                    <Cpu size={12} />
                    <span>CPU: 24%</span>
                    <div className="w-16 h-1.5 bg-editor-track rounded-full overflow-hidden">
                        <div className="h-full bg-primary w-[24%]" />
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <Gpu size={12} />
                    <span>GPU: 68%</span>
                    <div className="w-16 h-1.5 bg-editor-track rounded-full overflow-hidden">
                        <div className="h-full bg-accent w-[68%]" />
                    </div>
                </div>
                <div className="h-4 w-[1px] bg-editor-border" />
                <div className="flex items-center gap-1.5 text-success">
                    <CheckCircle2 size={12} />
                    <span>Cloud Sync Active</span>
                </div>
            </div>
        </div>
    );
};
