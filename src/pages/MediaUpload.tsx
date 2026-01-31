import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useProjectStore } from '../store/useProjectStore';
import {
    Upload,
    File,
    X,
    CheckCircle2,
    Database,
    Video,
    Music,
    FileJson,
    Plus,
    type LucideIcon
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface UploadingFile {
    id: string;
    name: string;
    size: number;
    progress: number;
    status: 'uploading' | 'completed' | 'error';
    type: 'video' | 'audio' | 'script' | 'other';
    rawFile?: File;
}

import { api } from '../lib/api';

export const MediaUpload = () => {
    const [files, setFiles] = useState<UploadingFile[]>([]);
    const uploadMedia = useProjectStore(state => state.uploadMedia);

    const getFileType = useCallback((name: string): UploadingFile['type'] => {
        const ext = name.split('.').pop()?.toLowerCase();
        if (['mp4', 'mov', 'mxf'].includes(ext || '')) return 'video';
        if (['wav', 'mp3', 'aac'].includes(ext || '')) return 'audio';
        if (['pdf', 'txt', 'fdx'].includes(ext || '')) return 'script';
        return 'other';
    }, []);

    // Fetch existing media on mount
    React.useEffect(() => {
        const fetchMedia = async () => {
            try {
                const response = await api.media.listTakes();
                const takes = response.data;
                if (!Array.isArray(takes)) {
                    console.error("Expected array of takes, got:", takes);
                    return;
                }
                const mappedFiles: UploadingFile[] = takes.map((take: any) => ({
                    id: take.id.toString(),
                    name: take.file_name,
                    size: take.file_size || 0,
                    progress: 100,
                    status: 'completed',
                    type: getFileType(take.file_name)
                }));
                // Sort by ID descending (newest first)
                mappedFiles.sort((a, b) => parseInt(b.id) - parseInt(a.id));
                setFiles(mappedFiles);
            } catch (err) {
                console.error("Failed to fetch media list", err);
            }
        };
        fetchMedia();
    }, [getFileType]);

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        const newFiles = acceptedFiles.map(file => ({
            id: Math.random().toString(36).substr(2, 9),
            name: file.name,
            size: file.size,
            progress: 0,
            status: 'uploading' as const,
            type: getFileType(file.name),
            rawFile: file
        }));

        setFiles((prev: UploadingFile[]) => [...newFiles, ...prev]);

        for (const fileObj of newFiles) {
            try {
                // In a real app with axios.post(url, data, { onUploadProgress }), 
                // we'd update the progress here. 
                // Since our store wrapper is a simple async, we'll call it and mark complete.
                await uploadMedia(fileObj.rawFile as File);
                setFiles((prev: UploadingFile[]) => prev.map((f: UploadingFile) => f.id === fileObj.id ? { ...f, progress: 100, status: 'completed' } : f));
            } catch (err: any) {
                console.error("Upload error details:", err);
                const msg = err.response?.data?.detail || err.message || "Network Error";
                alert(`Upload Failed: ${msg}\n\nCheck console for details.`);
                setFiles((prev: UploadingFile[]) => prev.map((f: UploadingFile) => f.id === fileObj.id ? { ...f, status: 'error' } : f));
            }
        }
    }, [getFileType, uploadMedia]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

    return (
        <div className="p-8 space-y-8 max-w-5xl mx-auto">
            <header>
                <h1 className="text-3xl font-bold text-white mb-2">Media Ingest</h1>
                <p className="text-editor-muted">Upload footage, audio, scripts, and reference material for AI processing.</p>
            </header>

            <div
                {...getRootProps()}
                className={cn(
                    "border-2 border-dashed rounded-xl p-12 flex flex-col items-center justify-center transition-all cursor-pointer",
                    isDragActive ? "border-primary bg-primary/5 scale-[1.01]" : "border-editor-border hover:border-editor-muted bg-surface/30"
                )}
            >
                <input {...getInputProps()} />
                <div className="w-16 h-16 rounded-full bg-editor-track flex items-center justify-center mb-4 transition-transform group-hover:scale-110">
                    <Upload className={cn("text-primary transition-all", isDragActive && "animate-bounce")} size={32} />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Drag & Drop Media Files</h3>
                <p className="text-editor-muted text-center max-w-md">
                    Support for RAW, ProRes, DNxHR, MXF, and all major cinema formats.
                    Multiple files and folders supported.
                </p>
                <button className="mt-8 btn-primary flex items-center gap-2">
                    <Plus size={18} />
                    Browse Files
                </button>
            </div>

            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold flex items-center gap-2">
                        <Database size={20} className="text-primary" />
                        Active Uploads ({files.length})
                    </h3>
                    {files.length > 0 && (
                        <button className="text-xs text-editor-muted hover:text-white transition-colors" onClick={() => setFiles([])}>
                            Clear All
                        </button>
                    )}
                </div>

                {files.length === 0 ? (
                    <div className="glass-panel p-12 rounded-xl text-center text-editor-muted italic">
                        No active uploads. All files will appear here during processing.
                    </div>
                ) : (
                    <div className="grid gap-3">
                        {files.map((file: UploadingFile) => (
                            <UploadItem key={file.id} file={file} onRemove={(id: string) => setFiles((prev: UploadingFile[]) => prev.filter((f: UploadingFile) => f.id !== id))} />
                        ))}
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <UploadInfoCard
                    icon={Video}
                    title="Video Processing"
                    desc="AI will automatically run OCR, YOLO object detection, and sync audio markers."
                />
                <UploadInfoCard
                    icon={Music}
                    title="Audio Transcription"
                    desc="Whisper-engine powered transcription for every take with speaker identification."
                />
                <UploadInfoCard
                    icon={FileJson}
                    title="Metadata Mapping"
                    desc="Auto-linking scene numbers and take metadata from file headers and slates."
                />
            </div>
        </div>
    );
};

const UploadItem = ({ file, onRemove }: { file: UploadingFile, onRemove: (id: string) => void }) => {
    const Icon = file.type === 'video' ? Video : file.type === 'audio' ? Music : file.type === 'script' ? FileJson : File;

    const isError = file.status === 'error';
    const isCompleted = file.status === 'completed';

    return (
        <div className={cn(
            "glass-panel p-4 rounded-lg flex items-center gap-4 group transition-colors",
            isError && "border-danger/50 bg-danger/5"
        )}>
            <div className={cn(
                "w-10 h-10 rounded-md flex items-center justify-center",
                isCompleted ? "bg-success/20 text-success" :
                    isError ? "bg-danger/20 text-danger" :
                        "bg-primary/20 text-primary"
            )}>
                {isCompleted ? <CheckCircle2 size={20} /> :
                    isError ? <X size={20} /> :
                        <Icon size={20} />}
            </div>

            <div className="flex-1 min-w-0">
                <div className="flex justify-between mb-1">
                    <span className={cn("text-sm font-bold truncate pr-4", isError && "text-danger")}>
                        {file.name} {isError && "(Upload Failed)"}
                    </span>
                    <span className="text-xs text-editor-muted font-mono">{(file.size / (1024 * 1024)).toFixed(1)} MB</span>
                </div>
                <div className="w-full h-1.5 bg-editor-track rounded-full overflow-hidden">
                    <div
                        className={cn(
                            "h-full transition-all duration-300",
                            isCompleted ? "bg-success" :
                                isError ? "bg-danger" :
                                    "bg-primary"
                        )}
                        style={{ width: isError ? '100%' : `${file.progress}%` }}
                    />
                </div>
            </div>

            <button onClick={() => onRemove(file.id)} className="p-2 hover:bg-editor-border rounded-md text-editor-muted hover:text-danger transition-colors opacity-0 group-hover:opacity-100">
                <X size={18} />
            </button>
        </div>
    );
};

const UploadInfoCard = ({ icon: Icon, title, desc }: { icon: LucideIcon, title: string, desc: string }) => (
    <div className="glass-panel p-6 rounded-xl border-t-2 border-primary/30">
        <Icon className="text-primary mb-4" size={24} />
        <h4 className="font-bold mb-2">{title}</h4>
        <p className="text-xs text-editor-muted leading-relaxed">{desc}</p>
    </div>
);
