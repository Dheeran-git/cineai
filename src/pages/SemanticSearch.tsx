import React, { useState, useCallback, useEffect } from 'react';
import { Search, Sparkles, Play, Clock, Brain, ChevronRight, ThumbsUp, ThumbsDown, Filter, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { api, API_BASE_URL } from '../lib/api';

interface SearchResult {
    result_id: number;
    take_id: number;
    moment_id: number;
    start_time: number;
    end_time: number;
    confidence: number;
    transcript_snippet: string;
    emotion_label: string;
    file_name: string;
    video_url: string;
    reasoning: {
        matched_because: string[];
        emotion_detected: string;
        timing_pattern: string;
        confidence_score: number;
    };
}

interface SearchResponse {
    query: string;
    total_results: number;
    results: SearchResult[];
}

const SUGGESTION_EXAMPLES = [
    "hesitant reaction before answering",
    "tense pause before dialogue",
    "awkward silence after confession",
    "relieved smile after conflict",
    "angry interruption mid-sentence",
    "thoughtful pause while listening",
    "surprised reaction to news",
    "emotional breakdown moment"
];

export const SemanticSearch: React.FC = () => {
    const navigate = useNavigate();
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [showFilters, setShowFilters] = useState(false);
    const [selectedEmotion, setSelectedEmotion] = useState<string | null>(null);
    const [totalResults, setTotalResults] = useState(0);
    const [hasSearched, setHasSearched] = useState(false);

    const emotions = ['hesitant', 'tense', 'angry', 'sad', 'happy', 'relieved', 'awkward', 'surprised'];

    // Fetch suggestions as user types
    useEffect(() => {
        if (query.length > 2) {
            const filtered = SUGGESTION_EXAMPLES.filter(s =>
                s.toLowerCase().includes(query.toLowerCase())
            ).slice(0, 5);
            setSuggestions(filtered);
        } else {
            setSuggestions([]);
        }
    }, [query]);

    const handleSearch = useCallback(async () => {
        if (!query.trim()) return;

        setIsLoading(true);
        setHasSearched(true);
        setSuggestions([]);

        try {
            const filters: Record<string, string> = {};
            if (selectedEmotion) {
                filters.emotion = selectedEmotion;
            }

            const response = await api.search.intent({
                query: query.trim(),
                top_k: 20,
                filters: Object.keys(filters).length > 0 ? filters : null
            });

            setResults(response.data.results);
            setTotalResults(response.data.total_results);
        } catch (error) {
            console.error('Search failed:', error);
            setResults([]);
            setTotalResults(0);
        } finally {
            setIsLoading(false);
        }
    }, [query, selectedEmotion]);

    const handleFeedback = async (resultId: number, isRelevant: boolean) => {
        try {
            await api.search.feedback({
                query,
                result_id: resultId,
                is_relevant: isRelevant
            });
        } catch (error) {
            console.error('Feedback failed:', error);
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        setQuery(suggestion);
        setSuggestions([]);
    };

    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const handleJumpToTimeline = (takeId: number, startTime: number) => {
        // Navigate to AI Monitor with the specific take selected
        // In a real app we'd also jump to the timestamp, but let's start with auto-selecting the take
        navigate(`/monitor?takeId=${takeId}`);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-editor-darker via-editor-dark to-editor-darker p-8">
            {/* Header */}
            <div className="max-w-6xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <div className="flex items-center justify-center gap-3 mb-4">
                        <div className="p-3 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30">
                            <Brain className="w-8 h-8 text-purple-400" />
                        </div>
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent">
                            Semantic Search
                        </h1>
                    </div>
                    <p className="text-editor-muted text-lg">
                        Search footage by intent, emotion, and narrative context
                    </p>
                </motion.div>

                {/* Search Box */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="relative mb-8"
                >
                    <div className="relative group">
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 via-pink-500/20 to-orange-500/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all" />
                        <div className="relative bg-editor-dark/80 backdrop-blur-xl border border-white/10 rounded-2xl p-2 flex items-center gap-2">
                            <div className="flex-1 flex items-center gap-3 px-4">
                                <Sparkles className="w-5 h-5 text-purple-400" />
                                <input
                                    type="text"
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                    placeholder='Try: "hesitant reaction before answering"'
                                    className="flex-1 bg-transparent text-white text-lg placeholder:text-editor-muted/50 focus:outline-none py-4"
                                />
                            </div>
                            <button
                                onClick={handleSearch}
                                disabled={isLoading}
                                className="px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold rounded-xl flex items-center gap-2 transition-all disabled:opacity-50"
                            >
                                {isLoading ? (
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                ) : (
                                    <Search className="w-5 h-5" />
                                )}
                                Search
                            </button>
                        </div>
                    </div>

                    {/* Suggestions Dropdown */}
                    <AnimatePresence>
                        {suggestions.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="absolute z-10 top-full left-0 right-0 mt-2 bg-editor-dark/95 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden"
                            >
                                {suggestions.map((suggestion, i) => (
                                    <button
                                        key={i}
                                        onClick={() => handleSuggestionClick(suggestion)}
                                        className="w-full px-4 py-3 text-left hover:bg-white/5 flex items-center gap-3 text-editor-muted hover:text-white transition-colors"
                                    >
                                        <Search className="w-4 h-4" />
                                        {suggestion}
                                    </button>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>

                {/* Filters */}
                <div className="flex items-center gap-4 mb-8">
                    <button
                        onClick={() => setShowFilters(!showFilters)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${showFilters ? 'bg-purple-500/20 border-purple-500/50 text-purple-400' : 'border-white/10 text-editor-muted hover:text-white'
                            }`}
                    >
                        <Filter className="w-4 h-4" />
                        Filters
                    </button>

                    <AnimatePresence>
                        {showFilters && (
                            <motion.div
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="flex items-center gap-2"
                            >
                                <span className="text-editor-muted text-sm">Emotion:</span>
                                {emotions.map(emotion => (
                                    <button
                                        key={emotion}
                                        onClick={() => setSelectedEmotion(selectedEmotion === emotion ? null : emotion)}
                                        className={`px-3 py-1 rounded-full text-sm transition-all ${selectedEmotion === emotion
                                            ? 'bg-purple-500 text-white'
                                            : 'bg-white/5 text-editor-muted hover:bg-white/10'
                                            }`}
                                    >
                                        {emotion}
                                    </button>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Example Queries */}
                {!hasSearched && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.2 }}
                        className="mb-12"
                    >
                        <h3 className="text-editor-muted text-sm font-medium mb-4">Try these example queries:</h3>
                        <div className="flex flex-wrap gap-2">
                            {SUGGESTION_EXAMPLES.slice(0, 6).map((example, i) => (
                                <button
                                    key={i}
                                    onClick={() => {
                                        setQuery(example);
                                        setTimeout(() => handleSearch(), 100);
                                    }}
                                    className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-sm text-editor-muted hover:text-white transition-all flex items-center gap-2"
                                >
                                    <ArrowRight className="w-3 h-3" />
                                    {example}
                                </button>
                            ))}
                        </div>
                    </motion.div>
                )}

                {/* Results */}
                {hasSearched && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-semibold text-white">
                                {totalResults} Results for "{query}"
                            </h2>
                        </div>

                        {results.length === 0 ? (
                            <div className="text-center py-16 text-editor-muted">
                                <Brain className="w-16 h-16 mx-auto mb-4 opacity-30" />
                                <p>No moments found matching your intent.</p>
                                <p className="text-sm mt-2">Try a different query or process more footage.</p>
                            </div>
                        ) : (
                            <div className="grid gap-4">
                                {results.map((result, index) => (
                                    <motion.div
                                        key={result.result_id}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: index * 0.05 }}
                                        className="bg-editor-dark/50 backdrop-blur border border-white/10 rounded-xl p-6 hover:border-purple-500/30 transition-all group"
                                    >
                                        <div className="flex items-start gap-6">
                                            {/* Video Player */}
                                            <div className="w-48 h-28 bg-editor-darker rounded-lg flex items-center justify-center flex-shrink-0 relative overflow-hidden group-hover:scale-105 transition-transform border border-white/5">
                                                {result.video_url ? (
                                                    <video
                                                        src={`${API_BASE_URL.replace('/api/v1', '')}${result.video_url}#t=${result.start_time}`}
                                                        className="w-full h-full object-cover"
                                                        onMouseEnter={(e) => {
                                                            const video = e.currentTarget;
                                                            video.play().catch(() => { }); // Ignore autoplay blocks
                                                        }}
                                                        onMouseLeave={(e) => {
                                                            const video = e.currentTarget;
                                                            video.pause();
                                                            video.currentTime = result.start_time;
                                                        }}
                                                        muted
                                                        playsInline
                                                        poster="/api/placeholder/400/225"
                                                    />
                                                ) : (
                                                    <div className="flex flex-col items-center justify-center">
                                                        <Play className="w-8 h-8 text-white/50 group-hover:text-purple-400 transition-colors" />
                                                        <div className="absolute bottom-2 right-2 bg-black/70 px-2 py-1 rounded text-xs text-white">
                                                            {formatTime(result.start_time)} - {formatTime(result.end_time)}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>

                                            {/* Content */}
                                            <div className="flex-1">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getEmotionColor(result.emotion_label)
                                                        }`}>
                                                        {result.emotion_label}
                                                    </span>
                                                    <span className="text-editor-muted text-sm flex items-center gap-1">
                                                        <Clock className="w-3 h-3" />
                                                        {result.file_name || `Take ${result.take_id}`}
                                                    </span>
                                                    <div className="flex items-center gap-1 ml-auto">
                                                        <div className="w-24 h-2 bg-white/10 rounded-full overflow-hidden">
                                                            <div
                                                                className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                                                                style={{ width: `${result.confidence * 100}%` }}
                                                            />
                                                        </div>
                                                        <span className="text-sm text-editor-muted">
                                                            {Math.round(result.confidence * 100)}%
                                                        </span>
                                                    </div>
                                                </div>

                                                {result.transcript_snippet && (
                                                    <p className="text-white/80 mb-3 italic">
                                                        "{result.transcript_snippet}"
                                                    </p>
                                                )}

                                                {/* Reasoning */}
                                                <div className="bg-white/5 rounded-lg p-3 mb-3">
                                                    <div className="flex items-center gap-2 text-purple-400 text-sm font-medium mb-2">
                                                        <Brain className="w-4 h-4" />
                                                        Why this matched:
                                                    </div>
                                                    <ul className="text-sm text-editor-muted space-y-1">
                                                        {result.reasoning.matched_because.map((reason, i) => (
                                                            <li key={i} className="flex items-start gap-2">
                                                                <ChevronRight className="w-4 h-4 text-purple-400/50 flex-shrink-0 mt-0.5" />
                                                                {reason}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>

                                                {/* Actions */}
                                                <div className="flex items-center gap-3">
                                                    <button
                                                        onClick={() => handleJumpToTimeline(result.take_id, result.start_time)}
                                                        className="px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 rounded-lg text-sm flex items-center gap-2 transition-all"
                                                    >
                                                        <Play className="w-4 h-4" />
                                                        Jump to Timeline
                                                    </button>
                                                    <button className="px-4 py-2 bg-white/5 hover:bg-white/10 text-editor-muted hover:text-white rounded-lg text-sm transition-all">
                                                        Add to Selects
                                                    </button>
                                                    <div className="flex items-center gap-1 ml-auto">
                                                        <span className="text-xs text-editor-muted mr-2">Helpful?</span>
                                                        <button
                                                            onClick={() => handleFeedback(result.result_id, true)}
                                                            className="p-2 hover:bg-green-500/20 rounded-lg transition-colors group"
                                                        >
                                                            <ThumbsUp className="w-4 h-4 text-editor-muted group-hover:text-green-400" />
                                                        </button>
                                                        <button
                                                            onClick={() => handleFeedback(result.result_id, false)}
                                                            className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
                                                        >
                                                            <ThumbsDown className="w-4 h-4 text-editor-muted group-hover:text-red-400" />
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        )}
                    </motion.div>
                )}
            </div>
        </div>
    );
};

// Helper function for emotion colors
function getEmotionColor(emotion: string): string {
    const colors: Record<string, string> = {
        hesitant: 'bg-yellow-500/20 text-yellow-400',
        tense: 'bg-orange-500/20 text-orange-400',
        angry: 'bg-red-500/20 text-red-400',
        sad: 'bg-blue-500/20 text-blue-400',
        happy: 'bg-green-500/20 text-green-400',
        relieved: 'bg-teal-500/20 text-teal-400',
        awkward: 'bg-purple-500/20 text-purple-400',
        surprised: 'bg-pink-500/20 text-pink-400',
        neutral: 'bg-gray-500/20 text-gray-400'
    };
    return colors[emotion] || colors.neutral;
}

export default SemanticSearch;
