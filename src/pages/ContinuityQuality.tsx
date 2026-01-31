import React, { useState } from 'react';
import {
    ShieldCheck,
    Maximize2,
    Columns,
    Box,
    Zap,
    Camera,
    type LucideIcon
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface ContinuityError {
    id: string;
    type: 'Prop' | 'Costume' | 'Lighting' | 'Focus';
    severity: 'High' | 'Medium' | 'Low';
    desc: string;
    frame: string;
    thumbnailA: string;
    thumbnailB: string;
}

const issues: ContinuityError[] = [
    {
        id: 'e1',
        type: 'Prop',
        severity: 'High',
        desc: 'Glass position shifted 15cm between Master and Close-up.',
        frame: '00:12:04:15',
        thumbnailA: 'https://via.placeholder.com/150/000000/FFFFFF?text=Master+Glass',
        thumbnailB: 'https://via.placeholder.com/150/000000/FFFFFF?text=CU+Glass'
    },
    {
        id: 'e2',
        type: 'Focus',
        severity: 'Medium',
        desc: 'Micro-hunting detected on Character B eyes.',
        frame: '00:12:08:22',
        thumbnailA: 'https://via.placeholder.com/150/000000/FFFFFF?text=In+Focus',
        thumbnailB: 'https://via.placeholder.com/150/000000/FFFFFF?text=Soft+Focus'
    },
    {
        id: 'e3',
        type: 'Lighting',
        severity: 'Low',
        desc: 'Flicker detected in background practical light.',
        frame: '00:12:15:02',
        thumbnailA: 'https://via.placeholder.com/150/000000/FFFFFF?text=Normal',
        thumbnailB: 'https://via.placeholder.com/150/000000/FFFFFF?text=Flicker'
    },
];

export const ContinuityQuality = () => {
    const [selectedIssueId, setSelectedIssueId] = useState<string | null>('e1');

    const selectedIssue = issues.find(i => i.id === selectedIssueId);

    return (
        <div className="h-full flex flex-col bg-editor-bg">
            <header className="p-6 border-b border-editor-border bg-surface flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                        <ShieldCheck className="text-success" />
                        Continuity & Technical Quality
                    </h1>
                    <p className="text-sm text-editor-muted">PROJECT: THE PERIMETER | SCANNING: SCENE 12</p>
                </div>
                <div className="flex gap-2">
                    <button className="flex items-center gap-2 px-3 py-1.5 bg-editor-track rounded text-[10px] font-bold uppercase tracking-widest text-editor-muted hover:text-white transition-colors border border-white/5">
                        <Columns size={14} /> Side-by-Side
                    </button>
                    <button className="flex items-center gap-2 px-3 py-1.5 bg-primary text-white rounded text-[10px] font-bold uppercase tracking-widest hover:bg-primary/80 transition-all shadow-lg">
                        <Zap size={14} /> Run Deep Scan
                    </button>
                </div>
            </header>

            <div className="flex-1 flex min-h-0">
                {/* Issues List */}
                <div className="w-96 border-r border-editor-border flex flex-col bg-surface/50">
                    <div className="p-4 border-b border-editor-border flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase text-editor-muted tracking-widest">Detected Variances ({issues.length})</span>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                        {issues.map(issue => (
                            <button
                                key={issue.id}
                                onClick={() => setSelectedIssueId(issue.id)}
                                className={cn(
                                    "w-full p-4 rounded-xl border text-left transition-all group",
                                    selectedIssueId === issue.id
                                        ? "bg-primary/10 border-primary/50 shadow-lg"
                                        : "bg-editor-track/40 border-white/5 hover:border-white/20"
                                )}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-2">
                                        <div className={cn(
                                            "w-2 h-2 rounded-full",
                                            issue.severity === 'High' ? "bg-danger" : issue.severity === 'Medium' ? "bg-warning" : "bg-primary"
                                        )} />
                                        <span className="text-xs font-bold text-white">{issue.type} Variance</span>
                                    </div>
                                    <span className="text-[9px] font-mono text-editor-muted">{issue.frame}</span>
                                </div>
                                <p className="text-[11px] text-editor-muted leading-relaxed line-clamp-2 mb-3">
                                    {issue.desc}
                                </p>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Visualizer Panel */}
                <div className="flex-1 flex flex-col p-8 space-y-8 overflow-y-auto">
                    {selectedIssue ? (
                        <>
                            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs uppercase font-bold text-editor-muted tracking-widest">Reference Take (Master)</span>
                                    </div>
                                    <div className="aspect-video bg-black rounded-2xl border-2 border-editor-border relative overflow-hidden group">
                                        <img src={selectedIssue.thumbnailA} alt="Ref" className="w-full h-full object-cover opacity-60" />
                                        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40">
                                            <Maximize2 size={32} className="text-white" />
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs uppercase font-bold text-editor-muted tracking-widest">Current Take (Close-up)</span>
                                    </div>
                                    <div className="aspect-video bg-black rounded-2xl border-2 border-primary/50 relative overflow-hidden group shadow-[0_0_30px_rgba(59,130,246,0.1)]">
                                        <img src={selectedIssue.thumbnailB} alt="Curr" className="w-full h-full object-cover" />
                                        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40">
                                            <Maximize2 size={32} className="text-white" />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="glass-panel p-8 rounded-2xl space-y-6">
                                <div>
                                    <h3 className="text-xl font-bold text-white mb-2">Technical Analysis Result</h3>
                                    <p className="text-sm text-editor-muted max-w-2xl leading-relaxed">
                                        Computer vision model identified a geometric variance.
                                    </p>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                                    <QualityMetric icon={Camera} label="Focus Score" value="98.2%" status="Optimal" />
                                    <QualityMetric icon={Zap} label="Lighting Drift" value="0.4 EV" status="Stable" />
                                    <QualityMetric icon={Box} label="Geometric Fit" value="62.5%" status="Warning" />
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-center p-20 opacity-40">
                            <ShieldCheck size={80} className="mb-6" />
                            <h3 className="text-2xl font-bold text-white mb-2">No Issue Selected</h3>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

const QualityMetric = ({ icon: Icon, label, value, status }: { icon: LucideIcon, label: string, value: string, status: 'Optimal' | 'Warning' | 'Stable' }) => (
    <div className="space-y-2">
        <div className="flex items-center gap-2 text-editor-muted">
            <Icon size={14} />
            <span className="text-[10px] font-bold uppercase tracking-widest">{label}</span>
        </div>
        <div className="flex items-end gap-3">
            <span className="text-2xl font-mono font-bold text-white">{value}</span>
            <span className={cn(
                "text-[10px] font-bold px-1.5 py-0.5 rounded-full mb-1",
                status === 'Optimal' || status === 'Stable' ? "bg-success/20 text-success" : "bg-warning/20 text-warning"
            )}>{status}</span>
        </div>
    </div>
);
