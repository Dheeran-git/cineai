import {
    BrainCircuit,
    Dna,
    Mic,
    Zap,
    Plus
} from 'lucide-react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from 'recharts';

const pacingData = [
    { name: 'S1', current: 4.2, target: 3.8 },
    { name: 'S2', current: 2.8, target: 3.2 },
    { name: 'S3', current: 5.4, target: 4.5 },
    { name: 'S4', current: 3.1, target: 3.1 },
    { name: 'S5', current: 1.8, target: 2.4 },
    { name: 'S6', current: 4.9, target: 4.0 },
];

export const DirectorIntelligence = () => {
    return (
        <div className="p-8 space-y-8 max-w-7xl mx-auto h-full overflow-y-auto">
            <header>
                <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                    <BrainCircuit className="text-primary" />
                    Director & Editor Intelligence
                </h1>
                <p className="text-editor-muted">Augmented creativity using detected intent and style signatures.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Director Intent */}
                <div className="glass-panel p-8 rounded-2xl space-y-8">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <Mic className="text-accent" size={20} />
                            On-Set Vocal Cues (Detected)
                        </h3>
                        <span className="text-[10px] bg-accent/20 text-accent px-2 py-1 rounded font-bold">LIVE PARSER ACTIVE</span>
                    </div>

                    <div className="space-y-4">
                        <IntentCue
                            time="00:12:04:12"
                            cue="PRINT IT!"
                            speaker="Director"
                            desc="Detected strong positive sentiment. High probability of being the primary choice."
                            confidence={99}
                        />
                        <IntentCue
                            time="00:12:08:05"
                            cue="Go again, but faster."
                            speaker="Director"
                            desc="Instruction for pacing shift. AI has auto-labeled the next take as 'FAST-PACE'."
                            confidence={94}
                        />
                        <IntentCue
                            time="00:12:15:20"
                            cue="I love that ad-lib."
                            speaker="Producer"
                            desc="Positive stakeholder feedback detected at 00:12:15:20."
                            confidence={88}
                        />
                    </div>

                    <div className="p-4 bg-editor-track/50 rounded-xl border border-white/5 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                                <Zap size={20} />
                            </div>
                            <div>
                                <div className="text-xs font-bold text-white uppercase tracking-wider">Auto-Select Recommendation</div>
                                <div className="text-[10px] text-editor-muted italic">Take 04 is recommended based on "Print It!" cue.</div>
                            </div>
                        </div>
                        <button className="btn-primary text-[10px] uppercase font-bold tracking-widest px-4 py-2">Apply Now</button>
                    </div>
                </div>

                {/* Editor DNA */}
                <div className="glass-panel p-8 rounded-2xl space-y-8">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <Dna className="text-primary" size={20} />
                            Editor DNA Signature: "The Dark Knight"
                        </h3>
                        <button className="text-[10px] text-editor-muted hover:text-white flex items-center gap-1 border border-white/10 px-2 py-1 rounded">
                            <Plus size={12} /> Change Reference
                        </button>
                    </div>

                    <div className="space-y-6">
                        <div className="space-y-2">
                            <div className="flex justify-between text-[10px] font-bold text-editor-muted uppercase tracking-widest">
                                Pacing Accuracy (Shot Length Rhythm)
                                <span className="text-primary">82% Match</span>
                            </div>
                            <div className="h-40">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={pacingData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                        <XAxis dataKey="name" stroke="#555" fontSize={10} hide />
                                        <YAxis stroke="#555" fontSize={10} hide />
                                        <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: 'none' }} />
                                        <Line type="monotone" dataKey="current" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6' }} />
                                        <Line type="monotone" dataKey="target" stroke="#555" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const IntentCue = ({ time, cue, speaker, desc, confidence }: { time: string, cue: string, speaker: string, desc: string, confidence: number }) => (
    <div className="flex gap-4 group">
        <div className="flex flex-col items-center">
            <div className="w-2 h-2 rounded-full bg-accent ring-4 ring-accent/10 mb-1" />
            <div className="flex-1 w-[1px] bg-editor-border group-last:hidden" />
        </div>
        <div className="pb-8 flex-1">
            <div className="flex justify-between items-start mb-2">
                <div>
                    <span className="text-[10px] font-mono font-bold text-editor-muted mr-3">{time}</span>
                    <span className="text-sm font-bold text-white">"{cue}"</span>
                </div>
                <span className="text-[9px] font-bold font-mono text-accent">{confidence}% CONF</span>
            </div>
            <div className="flex items-center gap-2 mb-2">
                <span className="text-[9px] px-1.5 py-0.5 bg-editor-track rounded text-editor-muted font-bold uppercase tracking-widest">{speaker}</span>
            </div>
            <p className="text-xs text-editor-muted leading-relaxed">{desc}</p>
        </div>
    </div>
);
