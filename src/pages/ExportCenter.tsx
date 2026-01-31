import React, { useState } from 'react';
import { api } from '../lib/api';
import {
    Download,
    FileCode,
    Settings,
    CheckCircle2,
    FileJson,
    FileText,
    Share2,
    Lock,
    ChevronRight,
    type LucideIcon
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface ExportFormat {
    id: string;
    name: string;
    icon: LucideIcon;
    ext: string;
    desc: string;
    recommended: boolean;
}

const formats: ExportFormat[] = [
    { id: 'xml', name: 'Final Cut Pro XML', icon: FileCode, ext: '.xml', desc: 'Standard XML for FCP7, FCPX and Premiere Pro exchange.', recommended: true },
    { id: 'edl', name: 'CMX 3600 EDL', icon: FileText, ext: '.edl', desc: 'Legacy edit decision list for high-end finishing.', recommended: false },
    { id: 'aaf', name: 'Avid AAF', icon: FileJson, ext: '.aaf', desc: 'Exchange format for Media Composer and ProTools audio.', recommended: false },
    { id: 'otio', name: 'OpenTimelineIO', icon: Settings, ext: '.otio', desc: 'Modern open-source interchange for VFX pipelines.', recommended: true },
];

export const ExportCenter = () => {
    const [selectedFormat, setSelectedFormat] = useState('xml');
    const [includeAI, setIncludeAI] = useState(true);
    const [exporting, setExporting] = useState(false);

    const handleExport = async () => {
        setExporting(true);
        try {
            const response = await api.export.download(selectedFormat);
            // In a real app, this would be a blob download
            console.log("Export triggered for", selectedFormat, response.data);
            alert(`Export generated successfully: project_export.${selectedFormat}`);
        } catch (err) {
            console.error("Export failed", err);
            alert("Export failed. Please check the backend connection.");
        } finally {
            setExporting(false);
        }
    };

    return (
        <div className="p-8 space-y-8 max-w-5xl mx-auto">
            <header>
                <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                    <Download className="text-primary" />
                    Export Center
                </h1>
                <p className="text-editor-muted">Finalize your edit and generate interchange files for post-production finishing.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {formats.map(format => (
                            <button
                                key={format.id}
                                onClick={() => setSelectedFormat(format.id)}
                                className={cn(
                                    "p-6 rounded-2xl border text-left transition-all relative overflow-hidden group",
                                    selectedFormat === format.id
                                        ? "bg-primary/10 border-primary shadow-lg"
                                        : "bg-surface border-white/5 hover:border-white/20"
                                )}
                            >
                                {format.recommended && (
                                    <div className="absolute top-0 right-0 bg-primary/20 text-primary px-3 py-1 rounded-bl-xl text-[9px] font-bold uppercase tracking-widest">Recommended</div>
                                )}
                                <format.icon className={cn("mb-4 transition-colors", selectedFormat === format.id ? "text-primary" : "text-editor-muted group-hover:text-white")} size={32} />
                                <h3 className="font-bold text-white mb-1">{format.name}</h3>
                                <div className="text-[10px] font-mono font-bold text-editor-muted mb-3">{format.ext}</div>
                                <p className="text-xs text-editor-muted leading-relaxed line-clamp-2">{format.desc}</p>
                            </button>
                        ))}
                    </div>

                    <div className="glass-panel p-8 rounded-2xl space-y-6">
                        <h3 className="text-lg font-bold text-white">Export Configuration</h3>
                        <div className="space-y-4">
                            <ToggleItem
                                label="Include AI Metadata & Markers"
                                desc="Embeds take scores, continuity notes, and script sync markers into the XML/EDL."
                                active={includeAI}
                                onChange={setIncludeAI}
                            />
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="glass-panel p-6 rounded-2xl border-t-2 border-primary">
                        <h3 className="text-sm font-bold uppercase tracking-widest text-editor-muted mb-6">Manifest Summary</h3>
                        <div className="space-y-4 mb-8">
                            <div className="flex justify-between">
                                <span className="text-xs text-editor-muted">Total Clips</span>
                                <span className="text-xs font-mono font-bold text-white">42</span>
                            </div>
                        </div>

                        <div className="p-4 bg-editor-track/50 rounded-xl mb-6">
                            <div className="flex items-center gap-2 mb-2">
                                <CheckCircle2 size={14} className="text-success" />
                                <span className="text-[10px] font-bold text-white uppercase tracking-widest">Validation Passed</span>
                            </div>
                        </div>

                        <button
                            disabled={exporting}
                            onClick={handleExport}
                            className={cn(
                                "w-full py-4 bg-primary text-white rounded-xl font-bold uppercase tracking-widest text-sm shadow-[0_0_40px_rgba(59,130,246,0.3)] hover:scale-[1.02] transition-all active:scale-95 flex items-center justify-center gap-3",
                                exporting && "opacity-50 cursor-not-allowed"
                            )}
                        >
                            <Download size={20} className={cn(exporting && "animate-bounce")} />
                            {exporting ? 'Generating...' : 'Generate Export'}
                        </button>
                    </div>

                    <div className="glass-panel p-6 rounded-xl flex items-center justify-between group cursor-pointer hover:bg-white/5 transition-colors">
                        <div className="flex items-center gap-3">
                            <Share2 className="text-accent" size={20} />
                            <span className="text-xs font-bold text-white">Publish to Review</span>
                        </div>
                        <ChevronRight size={16} className="text-editor-muted group-hover:text-white" />
                    </div>

                    <div className="p-6 text-center">
                        <div className="flex items-center justify-center gap-2 text-editor-muted mb-2">
                            <Lock size={12} />
                            <span className="text-[10px] font-bold uppercase tracking-widest">End-to-End Encrypted</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const ToggleItem = ({ label, desc, active, onChange }: { label: string, desc: string, active: boolean, onChange: (val: boolean) => void }) => (
    <div className="flex items-start justify-between p-4 bg-surface/50 rounded-xl border border-white/5">
        <div className="flex-1 pr-4">
            <div className="text-sm font-bold text-white mb-1">{label}</div>
            <p className="text-[11px] text-editor-muted leading-relaxed">{desc}</p>
        </div>
        <button
            onClick={() => onChange(!active)}
            className={cn(
                "w-12 h-6 rounded-full transition-all relative flex items-center px-1",
                active ? "bg-primary" : "bg-editor-track"
            )}
        >
            <div className={cn("w-4 h-4 bg-white rounded-full transition-all", active ? "ml-6" : "ml-0")} />
        </button>
    </div>
);
