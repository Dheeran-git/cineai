import axios from 'axios';

export const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
    },
});

export const api = {
    projects: {
        getCurrent: () => apiClient.get('/projects'),
        create: (data: any) => apiClient.post('/projects', data),
    },
    media: {
        upload: (file: File) => {
            const formData = new FormData();
            formData.append('file', file);
            return apiClient.post('/media/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
        },
        listTakes: () => apiClient.get('/media/'),
    },
    processing: {
        getStatus: (takeId: number) => apiClient.get(`/processing/status/${takeId}`),
        start: (takeId: number) => apiClient.post(`/processing/start/${takeId}`),
    },
    timeline: {
        get: () => apiClient.get('/timeline/'),
        override: (takeId: number, data: { is_accepted: string; notes?: string }) =>
            apiClient.post(`/timeline/override/${takeId}`, data),
    },
    script: {
        getCoverage: () => apiClient.get('/script/coverage'),
    },
    intelligence: {
        getHeatmap: (takeId: number) => apiClient.get(`/intelligence/heatmap/${takeId}`),
        getRisk: () => apiClient.get('/intelligence/risk'),
    },
    training: {
        getStatus: () => apiClient.get('/training/status'),
        dna: () => apiClient.get('/training/dna'),
    },
    export: {
        download: (format: string) => apiClient.get(`/export/${format}`),
    },
    search: {
        intent: (data: { query: string; top_k?: number; filters?: any }) =>
            apiClient.post('/search/intent', data),
        suggestions: (q: string) => apiClient.get(`/search/suggestions?q=${q}`),
        explain: (id: number) => apiClient.get(`/search/explain/${id}`),
        feedback: (data: { query: string; result_id: number; is_relevant: boolean }) =>
            apiClient.post('/search/feedback', data),
    }
};

export default apiClient;
