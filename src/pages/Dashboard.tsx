import React from 'react';
import { useProjectStore } from '../store/useProjectStore';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell
} from 'recharts';
import {
    Film,
    Clock,
    Camera,
    Brain,
    AlertCircle,
    Info,
    CheckCircle2,
    Activity,
    type LucideIcon
} from 'lucide-react';

const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6'];

export const Dashboard = () => {
    const project = useProjectStore();

    React.useEffect(() => {
        project.fetchProject();
    }, []);

    const issueData = [
        { name: 'Focus', value: project.issues.focus },
        { name: 'Audio', value: project.issues.audio },
        { name: 'Continuity', value: project.issues.continuity },
        { name: 'Narrative', value: project.issues.narrative },
    ];

    return (
        <div className="p-8 space-y-8 max-w-7xl mx-auto">
            <header className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">{project.projectName}</h1>
                    <div className="flex gap-4 text-sm text-editor-muted">
                        <span className="flex items-center gap-1"><Clock size={16} /> Shoot Date: {project.shootDate}</span>
                        <span className="flex items-center gap-1"><Camera size={16} /> {project.cameras.length} Cameras</span>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-xs uppercase tracking-widest text-editor-muted mb-1 font-bold">Processing Status</div>
                    <div className="flex items-center gap-3">
                        <div className="w-48 h-2 bg-editor-track rounded-full overflow-hidden">
                            <div
                                className="h-full bg-primary transition-all duration-1000"
                                style={{ width: `${project.processingProgress}%` }}
                            />
                        </div>
                        <span className="text-xl font-mono font-bold text-primary">{project.processingProgress}%</span>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    icon={Film}
                    label="Total Footage"
                    value={project.totalFootage}
                    subValue="+2h since yesterday"
                />
                <StatCard
                    icon={Brain}
                    label="AI Confidence"
                    value={`${project.aiConfidenceHealth}%`}
                    subValue="Optimal Performance"
                />
                <StatCard
                    icon={AlertCircle}
                    label="Detected Issues"
                    value={Object.values(project.issues).reduce((a, b: number) => a + b, 0).toString()}
                    subValue="24 items pending review"
                />
                <StatCard
                    icon={CheckCircle2}
                    label="Approved Selects"
                    value="142"
                    subValue="85% of Scene 12 covered"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 glass-panel p-6 rounded-xl">
                    <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                        <Activity className="text-primary" size={20} />
                        Detected Issues Breakdown
                    </h3>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={issueData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                <XAxis dataKey="name" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                    {issueData.map((_entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass-panel p-6 rounded-xl">
                    <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                        <Info className="text-accent" size={20} />
                        AI Recommendations
                    </h3>
                    <div className="space-y-4">
                        <RecommendationItem
                            title="Coverage Gap: Scene 24"
                            desc="Missing close-up for Character B's reaction. 3 alternative takes detected."
                            type="warning"
                        />
                        <RecommendationItem
                            title="High Reshoot Risk"
                            desc="Sequence 48-1 has significant motion blur on primary camera."
                            type="danger"
                        />
                        <RecommendationItem
                            title="Script Sync Peak"
                            desc="Character ad-lib detected in Scene 12. Potential for improved narrative beat."
                            type="info"
                        />
                    </div>
                    <button className="w-full mt-6 py-2 border border-editor-border rounded-md hover:bg-editor-track transition-colors text-sm font-medium">
                        View All Recommendations
                    </button>
                </div>
            </div>
        </div>
    );
};

const StatCard = ({ icon: Icon, label, value, subValue }: { icon: LucideIcon, label: string, value: string, subValue: string }) => (
    <div className="glass-panel p-6 rounded-xl relative overflow-hidden group">
        <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:scale-110 transition-transform duration-500">
            <Icon size={48} />
        </div>
        <div className="relative z-10">
            <div className="flex items-center gap-2 mb-4">
                <Icon size={20} />
                <span className="text-xs font-bold uppercase tracking-widest text-editor-muted">{label}</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1 font-mono">{value}</div>
            <div className="text-[10px] text-editor-muted font-medium">{subValue}</div>
        </div>
    </div>
);

const RecommendationItem = ({ title, desc, type }: { title: string, desc: string, type: 'warning' | 'danger' | 'info' }) => (
    <div className="p-3 bg-editor-track/50 rounded-lg border-l-4" style={{ borderColor: type === 'warning' ? '#f59e0b' : type === 'danger' ? '#ef4444' : '#3b82f6' }}>
        <div className="text-sm font-bold text-white mb-1">{title}</div>
        <div className="text-xs text-editor-muted leading-relaxed">{desc}</div>
    </div>
);
