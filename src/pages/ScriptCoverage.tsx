import React, { useState, useMemo } from 'react';
import {
    FileText,
    CheckCircle2,
    AlertCircle,
    Eye,
    MoreVertical,
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface ScriptLine {
    id: string;
    char: string;
    line: string;
    status: 'covered' | 'partial' | 'missing';
    takes: string[];
    adLib?: string;
}

const scriptData: ScriptLine[] = [
    { id: 'l1', char: 'KALE', line: "I told you we shouldn't have come here, Marcus. The perimeter is compromised.", status: 'covered', takes: ['S12_T01', 'S12_T02', 'S12_T04'] },
    { id: 'l2', char: 'MARCUS', line: "Since when do you care about perimeters? You just want to get back to the city.", status: 'covered', takes: ['S12_T04', 'S12_T05'] },
    { id: 'l3', char: 'KALE', line: "I care about staying alive. Look at this tech. This isn't local. This is Sector 7 gear.", status: 'partial', takes: ['S12_T02'], adLib: "Sector 7? More like Sector Suicide." },
    { id: 'l4', char: 'MARCUS', line: "Sector 7 is a myth. Put the tracker down.", status: 'missing', takes: [] },
    { id: 'l5', char: 'KALE', line: "(Beat) It's no myth. I've seen the markings before.", status: 'covered', takes: ['S12_T01', 'S12_T05'] },
];

export const ScriptCoverage = () => {
    const [selectedLineId, setSelectedLineId] = useState<string | null>('l1');

    return (
        <div className="h-full flex flex-col bg-editor-bg overflow-hidden">
            <header className="p-6 border-b border-editor-border flex justify-between items-center bg-surface">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                        <FileText className="text-primary" />
                        Script & Coverage
                    </h1>
                    <p className="text-sm text-editor-muted">EPISODE 104 - "THE PERIMETER" | SCENE 12</p>
                </div>
                <div className="flex gap-4">
                    <div className="flex items-center gap-6 px-4 py-2 bg-editor-track rounded-md text-xs font-bold uppercase tracking-tight">
                        <div className="flex items-center gap-1.5 text-success">
                            <CheckCircle2 size={14} /> 82% COVERED
                        </div>
                        <div className="flex items-center gap-1.5 text-warning">
                            <AlertCircle size={14} /> 12% PARTIAL
                        </div>
                        <div className="flex items-center gap-1.5 text-danger">
                            <X size={14} /> 6% MISSING
                        </div>
                    </div>
                </div>
            </header>

            <div className="flex-1 flex min-h-0">
                {/* Script Panel */}
                <div className="flex-1 overflow-y-auto border-r border-editor-border p-12 bg-editor-bg/50">
                    <div className="max-w-2xl mx-auto space-y-12 font-mono text-sm">
                        <div className="text-center italic text-editor-muted mb-16">
                            INT. ABANDONED OUTPOST - NIGHT
                        </div>

                        {scriptData.map((item) => (
                            <div
                                key={item.id}
                                onClick={() => setSelectedLineId(item.id)}
                                className={cn(
                                    "relative group cursor-pointer transition-all border-l-2 pl-8 py-4 -ml-8 rounded-r-lg",
                                    selectedLineId === item.id ? "bg-primary/5 border-primary" : "border-transparent hover:bg-white/5"
                                )}
                            >
                                <div className="absolute left-0 top-1/2 -translate-y-1/2 flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <div className={cn(
                                        "w-3 h-3 rounded-full",
                                        item.status === 'covered' ? "bg-success" : item.status === 'partial' ? "bg-warning" : "bg-danger"
                                    )} title={item.status} />
                                </div>

                                <div className="font-bold text-white mb-2 tracking-widest text-center">{item.char}</div>
                                <div className="text-editor-text leading-loose whitespace-pre-wrap max-w-lg mx-auto">
                                    {item.line}
                                </div>

                                {item.adLib && (
                                    <div className="mt-4 p-3 bg-accent/10 border border-accent/20 rounded text-[11px] text-accent font-sans italic">
                                        <span className="font-bold uppercase not-italic mr-2">Ad-lib Detected:</span>
                                        "{item.adLib}"
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Coverage Panel */}
                <div className="w-96 flex flex-col bg-surface shadow-xl relative z-10">
                    <div className="p-4 border-b border-editor-border font-bold text-xs uppercase tracking-widest text-editor-muted flex items-center justify-between">
                        Takes Covering Line
                        {selectedLineId && (
                            <span className="bg-primary/20 text-primary px-2 py-0.5 rounded">
                                Line {selectedLineId.replace('l', '')}
                            </span>
                        )}
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {selectedLineId ? (
                            <>
                                {scriptData.find(l => l.id === selectedLineId)?.takes.length === 0 ? (
                                    <div className="p-8 text-center space-y-4">
                                        <div className="w-16 h-16 rounded-full bg-danger/10 text-danger flex items-center justify-center mx-auto mb-4">
                                            <AlertCircle size={32} />
                                        </div>
                                        <div className="font-bold text-white">No Coverage Detected</div>
                                        <p className="text-xs text-editor-muted leading-relaxed">
                                            AI scan of current project footage has not found this line in any processed take.
                                        </p>
                                        <button className="btn-primary w-full text-xs">Request Reshoot Risk Analysis</button>
                                    </div>
                                ) : (
                                    scriptData.find(l => l.id === selectedLineId)?.takes.map((takeId) => (
                                        <TakeCard key={takeId} id={takeId} />
                                    ))
                                )}
                            </>
                        ) : (
                            <div className="h-full flex items-center justify-center italic text-editor-muted text-sm text-center p-8">
                                Select a line in the script to view available take coverage.
                            </div>
                        )}
                    </div>

                    <div className="p-4 bg-editor-track/50 border-t border-editor-border">
                        <div className="text-[10px] uppercase font-bold text-editor-muted mb-4">Scene Coverage Matrix</div>
                        <div className="grid grid-cols-5 gap-2">
                            {Array.from({ length: 15 }).map((_, i) => (
                                <div
                                    key={i}
                                    className={cn(
                                        "aspect-square rounded shadow-inner border border-white/5 transition-all flex items-center justify-center font-mono text-[9px] font-bold",
                                        i < 8 ? "bg-success/40 text-success border-success/30 hover:bg-success/60" :
                                            i < 12 ? "bg-warning/40 text-warning border-warning/30 hover:bg-warning/60" :
                                                "bg-danger/40 text-danger border-danger/30 hover:bg-danger/60"
                                    )}
                                >
                                    L-{i + 1}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const TakeCard = ({ id }: { id: string }) => {
    const randomSeconds = useMemo(() => {
        const hash = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        return (hash % 60).toString().padStart(2, '0');
    }, [id]);

    return (
        <div className="glass-panel p-3 rounded-lg flex gap-3 hover:bg-white/5 cursor-pointer transition-colors border border-white/5">
            <div className="w-20 aspect-video bg-black rounded relative overflow-hidden flex-shrink-0">
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <div className="absolute bottom-1 right-1 text-[8px] font-bold text-white">00:12:{randomSeconds}</div>
            </div>
            <div className="flex-1 min-w-0">
                <div className="text-xs font-bold text-white truncate mb-1">{id}</div>
                <div className="flex gap-2">
                    <span className="text-[9px] px-1 bg-editor-border rounded text-editor-muted">CAM-A</span>
                    <span className="text-[9px] px-1 bg-primary/10 rounded text-primary font-bold">94% MATCH</span>
                </div>
                <div className="mt-2 flex gap-1">
                    <button className="p-1 hover:text-white text-editor-muted transition-colors"><Eye size={12} /></button>
                    <button className="p-1 hover:text-white text-editor-muted transition-colors"><MoreVertical size={12} /></button>
                </div>
            </div>
        </div>
    );
};

const X = ({ className, size }: { className?: string, size?: number }) => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={className}
    >
        <path d="M18 6 6 18" /><path d="m6 6 12 12" />
    </svg>
);
