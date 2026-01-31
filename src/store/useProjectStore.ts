import { create } from 'zustand';
import { api } from '../lib/api';

interface ProjectState {
    projectId: number | null;
    projectName: string;
    description: string;
    shootDate: string;
    cameras: string[];
    totalFootage: string;
    processingProgress: number;
    aiConfidenceHealth: number;
    loading: boolean;
    error: string | null;
    issues: {
        focus: number;
        audio: number;
        continuity: number;
        narrative: number;
    };

    // Actions
    timeline: unknown | null;
    fetchProject: () => Promise<void>;
    fetchTimeline: () => Promise<void>;
    getProcessingStatus: (takeId: number) => Promise<unknown>;
    setProcessingProgress: (progress: number) => void;
    uploadMedia: (file: File) => Promise<unknown>;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
    projectId: null,
    projectName: "Loading...",
    description: "",
    shootDate: "",
    cameras: [],
    totalFootage: "0h 0m 0s",
    processingProgress: 0,
    aiConfidenceHealth: 0,
    loading: false,
    error: null,
    issues: {
        focus: 0,
        audio: 0,
        continuity: 0,
        narrative: 0,
    },
    timeline: null,

    fetchProject: async () => {
        set({ loading: true, error: null });
        try {
            const response = await api.projects.getCurrent();
            const project = response.data;
            set({
                projectId: project.id,
                projectName: project.name,
                description: project.description || "",
                shootDate: new Date(project.created_at).toLocaleDateString(),
                loading: false
            });
        } catch (err: unknown) {
            set({ error: err instanceof Error ? err.message : 'Unknown error', loading: false });
        }
    },

    fetchTimeline: async () => {
        set({ loading: true, error: null });
        try {
            const response = await api.timeline.get();
            set({ timeline: response.data, loading: false });
        } catch (err: unknown) {
            set({ error: err instanceof Error ? err.message : 'Unknown error', loading: false });
        }
    },

    getProcessingStatus: async (takeId: number) => {
        try {
            const response = await api.processing.getStatus(takeId);
            return response.data;
        } catch (err: unknown) {
            console.error("Failed to fetch processing status", err);
            return null;
        }
    },

    setProcessingProgress: (progress) => set({ processingProgress: progress }),

    uploadMedia: async (file: File) => {
        set({ loading: true, error: null });
        try {
            const response = await api.media.upload(file);
            set({ loading: false });
            return response.data;
        } catch (err: unknown) {
            set({ error: err instanceof Error ? err.message : 'Unknown error', loading: false });
            throw err;
        }
    }
}));
