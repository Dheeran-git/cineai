import React, { useState, useRef, useEffect } from 'react';
import { useProjectStore } from '../store/useProjectStore';
import {
    Play,
    Pause,
    SkipBack,
    SkipForward,
    ZoomIn,
    ZoomOut,
    Scissors,
    MousePointer2,
    Hand,
    Layers,
    Check,
    type LucideIcon
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface TimelineClip {
    id: string;
    name: string;
    start: number; // in frames
    duration: number; // in frames
    color: string;
    type: 'video' | 'audio';
    track: number;
    score: number;
    aiReasoning: string[];
}

const initialClips: TimelineClip[] = [
    {
        id: 'c1',
        name: 'S12_T04_Master',
        start: 0,
        duration: 1200,
        color: '#34d399',
        type: 'video',
        track: 0,
        score: 94,
        aiReasoning: ['Excellent lighting', 'No focus hunting', 'Perfect dialogue delivery', 'Matches script exactly']
    },
    { id: 'c2', name: 'S12_T04_Audio_Mix', start: 0, duration: 1200, color: '#60a5fa', type: 'audio', track: 1, score: 98, aiReasoning: [] },
    {
        id: 'c3',
        name: 'S12_T05_CU_B',
        start: 1200,
        duration: 800,
        color: '#34d399',
        type: 'video',
        track: 0,
        score: 82,
        aiReasoning: ['Slight motion blur at start', 'Strong emotional intensity', 'Character B eyes caught light well']
    },
    { id: 'c4', name: 'S12_T05_Audio_Mix', start: 1200, duration: 800, color: '#60a5fa', type: 'audio', track: 1, score: 92, aiReasoning: [] },
];

export const Timeline = () => {
    const { timeline, fetchTimeline } = useProjectStore();
    const [zoom, setZoom] = useState(1);
    const [playhead, setPlayhead] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [selectedClipId, setSelectedClipId] = useState<string | null>(null);
    const [tool, setTool] = useState<'select' | 'hand' | 'blade'>('select');

    const timelineRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        fetchTimeline();
    }, []);

    const clips = React.useMemo(() => {
        if (!timeline) return [];
        const typedTimeline = timeline as {
            tracks: Record<string, { type: 'video' | 'audio'; clips: Array<{ id: string; name: string; start: number; duration: number; score: number; reasoning: string }> }>
        };
        const allClips: TimelineClip[] = [];
        Object.keys(typedTimeline.tracks).forEach(trackKey => {
            typedTimeline.tracks[trackKey].clips.forEach((clip) => {
                allClips.push({
                    ...clip,
                    type: typedTimeline.tracks[trackKey].type,
                    color: typedTimeline.tracks[trackKey].type === 'video' ? '#34d399' : '#60a5fa',
                    track: 0,
                    aiReasoning: [clip.reasoning]
                });
            });
        });
        return allClips;
    }, [timeline]);

    useEffect(() => {
        let interval: number | undefined;
        if (isPlaying) {
            interval = setInterval(() => {
                setPlayhead((prev: number) => (prev + 1) % 5000);
            }, 1000 / 24);
        }
        return () => clearInterval(interval);
    }, [isPlaying]);

    const selectedClip = clips.find(c => c.id === selectedClipId);

    const formatTimecode = (frames: number) => {
        const fps = 24;
        const h = Math.floor(frames / (fps * 3600));
        const m = Math.floor((frames % (fps * 3600)) / (fps * 60));
        const s = Math.floor((frames % (fps * 60)) / fps);
        const f = frames % fps;
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}:${f.toString().padStart(2, '0')}`;
    };

    return (
        <div className="h-full flex flex-col overflow-hidden bg-editor-bg">
            {/* Top Toolbar */}
            <div className="h-12 border-b border-editor-border flex items-center justify-between px-4">
                <div className="flex items-center gap-1">
                    <ToolButton active={tool === 'select'} onClick={() => setTool('select')} icon={MousePointer2} />
                    <ToolButton active={tool === 'hand'} onClick={() => setTool('hand')} icon={Hand} />
                    <ToolButton active={tool === 'blade'} onClick={() => setTool('blade')} icon={Scissors} />
                    <div className="w-[1px] h-6 bg-editor-border mx-2" />
                    <div className="text-xs font-mono font-bold text-primary px-3 py-1 bg-primary/10 rounded">
                        {formatTimecode(playhead)}
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                        <button className="p-1.5 hover:bg-editor-track rounded text-editor-muted"><SkipBack size={18} /></button>
                        <button
                            onClick={() => setIsPlaying(!isPlaying)}
                            className="w-10 h-10 flex items-center justify-center bg-primary text-white rounded-full hover:bg-primary/80 transition-all shadow-lg active:scale-90"
                        >
                            {isPlaying ? <Pause size={20} fill="currentColor" /> : <Play size={20} className="ml-1" fill="currentColor" />}
                        </button>
                        <button className="p-1.5 hover:bg-editor-track rounded text-editor-muted"><SkipForward size={18} /></button>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button onClick={() => setZoom((z: number) => Math.max(0.1, z - 0.1))} className="p-1.5 hover:bg-editor-track rounded text-editor-muted"><ZoomOut size={18} /></button>
                    <div className="w-24 h-1.5 bg-editor-border rounded-full overflow-hidden">
                        <div className="h-full bg-editor-muted" style={{ width: `${zoom * 100}%` }} />
                    </div>
                    <button onClick={() => setZoom((z: number) => Math.min(2, z + 0.1))} className="p-1.5 hover:bg-editor-track rounded text-editor-muted"><ZoomIn size={18} /></button>
                </div>
            </div>

            <div className="flex-1 flex min-h-0 relative">
                {/* Main Timeline Area */}
                <div className="flex-1 flex flex-col min-w-0">
                    {/* Ruler */}
                    <div className="h-8 border-b border-editor-border bg-editor-track/30 relative">
                        <div
                            className="absolute top-0 bottom-0 w-[1px] bg-primary z-50 pointer-events-none"
                            style={{ left: `${playhead * zoom}px` }}
                        >
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-4 h-4 bg-primary rounded-b-sm flex items-center justify-center">
                                <div className="w-1 h-2 bg-white/50 rounded-full" />
                            </div>
                        </div>
                        {/* Time markers */}
                        <div className="flex items-end h-full px-2 gap-[100px]" style={{ transform: `scaleX(${zoom})`, transformOrigin: 'left' }}>
                            {Array.from({ length: 20 }).map((_, i) => (
                                <div key={i} className="flex flex-col items-center">
                                    <span className="text-[9px] text-editor-muted mb-1">{formatTimecode(i * 100)}</span>
                                    <div className="h-2 w-[1px] bg-editor-border" />
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Tracks */}
                    <div className="flex-1 overflow-auto relative p-4 space-y-2 select-none" ref={timelineRef}>
                        <Track label="Video 1" icon={Layers} color="text-success">
                            {clips.filter(c => c.type === 'video').map(clip => (
                                <TimelineClipItem
                                    key={clip.id}
                                    clip={clip}
                                    zoom={zoom}
                                    selected={selectedClipId === clip.id}
                                    onClick={() => setSelectedClipId(clip.id)}
                                />
                            ))}
                        </Track>
                        <Track label="Audio 1" icon={Play} color="text-primary">
                            {clips.filter(c => c.type === 'audio').map(clip => (
                                <TimelineClipItem
                                    key={clip.id}
                                    clip={clip}
                                    zoom={zoom}
                                    selected={selectedClipId === clip.id}
                                    onClick={() => setSelectedClipId(clip.id)}
                                />
                            ))}
                        </Track>
                    </div>
                </div>

                {/* Right Inspector Panel */}
                <div className="w-80 border-l border-editor-border bg-surface flex flex-col">
                    <div className="p-4 border-b border-editor-border text-xs font-bold uppercase tracking-widest text-editor-muted">
                        Clip Inspector
                    </div>

                    {selectedClip ? (
                        <div className="flex-1 overflow-y-auto p-4 space-y-6">
                            <div>
                                <div className="text-[10px] uppercase font-bold text-editor-muted mb-2">Selected Take</div>
                                <div className="text-lg font-bold text-white leading-tight">{selectedClip.name}</div>
                                <div className="flex gap-2 mt-3">
                                    <div className="bg-success text-white px-2 py-1 rounded text-[10px] font-bold">#{selectedClip.score} TAKE SCORE</div>
                                </div>
                            </div>

                            <div className="space-y-3">
                                <div className="text-[10px] uppercase font-bold text-editor-muted flex items-center justify-between">
                                    AI Assessment
                                    <span className="text-success font-mono font-bold">92% CONFIDENCE</span>
                                </div>
                                <ul className="space-y-2">
                                    {selectedClip.aiReasoning.map((reason: string, i: number) => (
                                        <li key={i} className="flex gap-2 text-xs text-editor-muted">
                                            <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1 flex-shrink-0" />
                                            {reason}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="space-y-2">
                                <div className="text-[10px] uppercase font-bold text-editor-muted">Human Override</div>
                                <div className="grid grid-cols-2 gap-2">
                                    <button className="flex items-center justify-center gap-2 py-2 bg-success/10 text-success border border-success/20 rounded-md hover:bg-success/20 transition-all font-bold text-xs uppercase">
                                        <Check size={14} /> Accept
                                    </button>
                                    <button className="flex items-center justify-center gap-2 py-2 bg-danger/10 text-danger border border-danger/20 rounded-md hover:bg-danger/20 transition-all font-bold text-xs uppercase">
                                        <Check size={14} className="rotate-45" /> Reject
                                    </button>
                                </div>
                            </div>

                            <div className="pt-6 border-t border-editor-border">
                                <div className="text-[10px] uppercase font-bold text-editor-muted mb-4 tracking-widest">Metadata</div>
                                <div className="space-y-2">
                                    <MetadataRow label="Codec" value="ProRes 422 HQ" />
                                    <MetadataRow label="Resolution" value="3840 x 2160" />
                                    <MetadataRow label="FPS" value="23.976" />
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-editor-muted">
                            <MousePointer2 size={48} className="mb-4 opacity-20" />
                            <p className="text-sm italic">Select a clip on the timeline to view AI reasoning and metadata.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

const ToolButton = ({ active, onClick, icon: Icon }: { active: boolean, onClick: () => void, icon: LucideIcon }) => (
    <button
        onClick={onClick}
        className={cn(
            "p-1.5 rounded transition-colors",
            active ? "bg-primary text-white" : "text-editor-muted hover:bg-editor-track hover:text-white"
        )}
    >
        <Icon size={18} />
    </button>
);

const Track = ({ label, icon: Icon, color, children }: { label: string, icon: LucideIcon, color: string, children: React.ReactNode }) => (
    <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2 mb-1">
            <div className={cn("w-4 h-4 flex items-center justify-center", color)}>
                <Icon size={12} />
            </div>
            <span className="text-[10px] uppercase font-bold text-editor-muted tracking-tight">{label}</span>
        </div>
        <div className="h-16 bg-black/20 rounded-md border border-editor-border/50 relative overflow-hidden group">
            <div className="absolute inset-0 grid grid-cols-[repeat(40,minmax(0,1fr))] opacity-10 pointer-events-none">
                {Array.from({ length: 40 }).map((_, i) => (
                    <div key={i} className="border-r border-white" />
                ))}
            </div>
            {children}
        </div>
    </div>
);

const TimelineClipItem = ({ clip, zoom, selected, onClick }: { clip: TimelineClip, zoom: number, selected: boolean, onClick: () => void }) => (
    <div
        onClick={(e) => { e.stopPropagation(); onClick(); }}
        className={cn(
            "absolute top-0 bottom-0 rounded-sm border-r border-background/20 cursor-pointer transition-all flex flex-col justify-between p-1 overflow-hidden",
            selected ? "ring-2 ring-primary ring-inset z-10 brightness-110" : "hover:brightness-105"
        )}
        style={{
            left: `${clip.start * zoom}px`,
            width: `${clip.duration * zoom}px`,
            backgroundColor: clip.color
        }}
    >
        <div className="text-[10px] font-bold text-black/80 truncate">{clip.name}</div>
        {clip.score && (
            <div className="flex justify-between items-end">
                <div className="text-[9px] font-mono font-bold text-black/60">T-{clip.score}</div>
                <div className="w-2 h-2 rounded-full bg-black/20" />
            </div>
        )}
    </div>
);

const MetadataRow = ({ label, value }: { label: string, value: string }) => (
    <div className="flex justify-between items-center py-1">
        <span className="text-[10px] text-editor-muted">{label}</span>
        <span className="text-xs font-mono font-semibold text-white/90">{value}</span>
    </div>
);
