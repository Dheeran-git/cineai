import React, { useState, useEffect, useMemo } from 'react';
import {
    Smile,
    Play,
    Clock,
    ChevronRight,
    Sparkles,
    Mic2,
    BrainCircuit,
    LayoutGrid,
    Search
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { api, API_BASE_URL } from '../lib/api';

// Shared utility for class names
function cn(...inputs: any[]) {
    return inputs.filter(Boolean).join(' ');
}

interface Take {
    id: number;
    file_name: string;
    number: number;
    ai_metadata?: any;
    confidence_score?: number;
}

interface CategorizedTakes {
    [category: string]: Take[];
}

export const EmotionPerformance: React.FC = () => {
    const navigate = useNavigate();
    const [takes, setTakes] = useState<Take[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchTakes = async () => {
            try {
                const response = await api.media.listTakes();
                setTakes(response.data);
            } catch (err) {
                console.error("Failed to fetch takes", err);
            } finally {
                setIsLoading(false);
            }
        };
        fetchTakes();
    }, []);

    const categorizedResults = useMemo(() => {
        const categories: CategorizedTakes = {
            'Hesitation & Pauses': [],
            'Laughter & Humor': [],
            'Emotional Peaks': [],
            'Analytical & Technical': [],
            'Standard Dialogue': []
        };

        takes.forEach(take => {
            const meta = take.ai_metadata || {};
            const audio = meta.audio || {};
            const behaviors = audio.behavioral_markers || {};
            const pause = behaviors.hesitation_duration || 0;
            const laughter = behaviors.laughter_detected || false;
            const emotion = meta.emotion || 'neutral';

            if (pause > 1.0) {
                categories['Hesitation & Pauses'].push(take);
            }
            if (laughter) {
                categories['Laughter & Humor'].push(take);
            }
            if (emotion === 'analytical') {
                categories['Analytical & Technical'].push(take);
            }
            if (emotion !== 'neutral' && emotion !== 'unknown' && emotion !== 'analytical') {
                categories['Emotional Peaks'].push(take);
            }
            if (!laughter && pause <= 1.0 && (emotion === 'neutral' || emotion === 'unknown' || emotion === 'analytical')) {
                // We show analytical in its own section AND Standard if it matches? 
                // No, let's keep sections distinct.
                if (emotion !== 'analytical') {
                    categories['Standard Dialogue'].push(take);
                }
            }
        });

        return categories;
    }, [takes]);

    if (isLoading) {
        return (
            <div className="h-full flex items-center justify-center bg-editor-darker">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
                    <span className="text-editor-muted font-mono text-xs uppercase tracking-widest">Aggregating Behavioral Data...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="h-full bg-editor-darker overflow-y-auto custom-scrollbar">
            <div className="p-8 space-y-12 max-w-7xl mx-auto">
                <header className="flex justify-between items-start">
                    <div>
                        <h1 className="text-4xl font-black text-white mb-2 flex items-center gap-3 tracking-tight">
                            <Smile className="text-accent" size={36} />
                            Behavioral Gallery
                        </h1>
                        <p className="text-editor-muted text-lg">
                            Neural analysis of performance cues across all existing footage
                        </p>
                    </div>
                    <button
                        onClick={() => navigate('/search')}
                        className="px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-white font-bold text-sm tracking-widest uppercase transition-all flex items-center gap-2"
                    >
                        <Search size={16} /> Advanced Search
                    </button>
                </header>

                <div className="space-y-16 pb-12">
                    {Object.entries(categorizedResults).map(([category, items], sectionIndex) => (
                        items.length > 0 && (
                            <motion.section
                                key={category}
                                initial={{ opacity: 0, y: 30 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: sectionIndex * 0.1 }}
                            >
                                <div className="flex items-center gap-4 mb-8">
                                    <h2 className="text-2xl font-bold text-white/90">{category}</h2>
                                    <div className="h-[1px] flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                                    <span className="text-xs font-mono text-editor-muted uppercase tracking-widest">{items.length} Clips Found</span>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                    {items.map((take) => (
                                        <TakeCard
                                            key={take.id}
                                            take={take}
                                            onClick={() => navigate(`/monitor?takeId=${take.id}`)}
                                        />
                                    ))}
                                </div>
                            </motion.section>
                        )
                    ))}
                </div>

                {takes.length === 0 && (
                    <div className="text-center py-24 opacity-30 mt-12">
                        <LayoutGrid size={64} className="mx-auto mb-4" />
                        <p className="text-xl">No behavioral data found. Head to AI Monitor to begin analysis.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

const TakeCard = ({ take, onClick }: { take: Take, onClick: () => void }) => {
    const videoBase = API_BASE_URL.replace('/api/v1', '');
    const meta = take.ai_metadata || {};
    const audio = meta.audio || {};
    const emotion = meta.emotion || 'neutral';
    const transcript = audio.transcript || "";
    const behaviors = audio.behavioral_markers || {};
    const pause = behaviors.hesitation_duration || 0;
    const laughter = behaviors.laughter_detected || false;

    return (
        <motion.div
            whileHover={{ scale: 1.02 }}
            className="group bg-editor-dark/60 backdrop-blur-xl border border-white/5 rounded-2xl overflow-hidden hover:border-primary/50 transition-all cursor-pointer shadow-2xl relative"
            onClick={onClick}
        >
            {/* Video Preview */}
            <div className="aspect-video bg-black relative overflow-hidden flex items-center justify-center border-b border-white/5">
                <video
                    src={`${videoBase}/media_files/${take.file_name}`}
                    className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500"
                    onMouseEnter={(e) => {
                        const video = e.currentTarget;
                        video.play().catch(() => { });
                    }}
                    onMouseLeave={(e) => {
                        const video = e.currentTarget;
                        video.pause();
                        video.currentTime = 0;
                    }}
                    muted
                    playsInline
                />

                {/* Overlay Metadata */}
                <div className="absolute top-3 left-3 flex flex-col gap-2 z-20">
                    <span className={cn(
                        "px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest border backdrop-blur-md self-start transition-colors",
                        emotion === 'tense' ? "bg-red-500/20 text-red-400 border-red-500/30" :
                            emotion === 'happy' ? "bg-green-500/20 text-green-400 border-green-500/30" :
                                emotion === 'sad' ? "bg-blue-500/20 text-blue-400 border-blue-500/30" :
                                    emotion === 'awkward' ? "bg-purple-500/20 text-purple-400 border-purple-500/30" :
                                        "bg-black/60 text-white/70 border-white/10"
                    )}>
                        {emotion}
                    </span>
                    {pause > 1.0 && (
                        <span className="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 rounded text-[9px] font-black uppercase tracking-widest backdrop-blur-md self-start shadow-xl">
                            <Clock size={10} className="inline mr-1 mb-0.5" /> {pause.toFixed(1)}s Hesitation
                        </span>
                    )}
                    {laughter && (
                        <span className="px-2 py-0.5 bg-pink-500/20 text-pink-400 border border-pink-500/30 rounded text-[9px] font-black uppercase tracking-widest backdrop-blur-md self-start shadow-xl">
                            <Sparkles size={10} className="inline mr-1 mb-0.5" /> Laughter Detected
                        </span>
                    )}
                </div>

                <div className="absolute inset-0 bg-gradient-to-t from-editor-darker via-transparent to-transparent opacity-80 group-hover:opacity-40 transition-opacity" />

                <div className="absolute bottom-3 left-3 right-3 flex justify-between items-center z-20">
                    <div className="flex -space-x-2">
                        {meta.cv?.objects?.slice(0, 3).map((obj: string, i: number) => (
                            <div key={i} className="w-5 h-5 rounded-full bg-editor-track border border-white/10 flex items-center justify-center shadow-lg" title={obj}>
                                <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                            </div>
                        ))}
                    </div>
                    <span className="text-[10px] font-bold text-white flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all translate-y-2 group-hover:translate-y-0">
                        <Play size={10} fill="currentColor" /> Preview
                    </span>
                </div>
            </div>

            {/* Content info */}
            <div className="p-5 space-y-4">
                <div className="flex justify-between items-start">
                    <div>
                        <h4 className="text-sm font-bold text-white truncate max-w-[180px] group-hover:text-primary transition-colors">{take.file_name}</h4>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="text-[9px] font-mono text-editor-muted tracking-widest uppercase">Take {take.number}</span>
                            <span className="h-1 w-1 rounded-full bg-editor-muted" />
                            <span className="text-[9px] font-mono text-editor-muted tracking-widest uppercase">ID {take.id}</span>
                        </div>
                    </div>
                </div>

                {transcript && (
                    <p className="text-[11px] text-gray-400 italic line-clamp-2 leading-relaxed bg-white/5 p-2 rounded-lg border border-white/5">
                        "{transcript}"
                    </p>
                )}

                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="flex flex-col">
                            <span className="text-[8px] text-editor-muted uppercase font-bold tracking-tighter">Acting</span>
                            <span className="text-xs font-black text-primary">{meta.score_breakdown?.acting || 0}</span>
                        </div>
                        <div className="w-[1px] h-6 bg-white/5" />
                        <div className="flex flex-col">
                            <span className="text-[8px] text-editor-muted uppercase font-bold tracking-tighter">Timing</span>
                            <span className="text-xs font-black text-accent">{meta.score_breakdown?.timing || 0}</span>
                        </div>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-[8px] text-editor-muted uppercase font-bold tracking-tighter">Acoustic IQ</span>
                        <span className="text-xs font-black text-success">{audio.quality_score || 0}%</span>
                    </div>
                </div>
            </div>

            {/* AI Reasoning Sparkle (Bottom Right) */}
            <div className="absolute bottom-2 right-2 opacity-10 group-hover:opacity-100 transition-opacity">
                <BrainCircuit size={14} className="text-primary" />
            </div>
        </motion.div>
    );
};

export default EmotionPerformance;
