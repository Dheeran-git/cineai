import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { MediaUpload } from './pages/MediaUpload';
import { AIMonitor } from './pages/AIMonitor';
import { Timeline } from './pages/Timeline';
import { ScriptCoverage } from './pages/ScriptCoverage';
import { EmotionPerformance } from './pages/EmotionPerformance';
import { ContinuityQuality } from './pages/ContinuityQuality';
import { DirectorIntelligence } from './pages/DirectorIntelligence';
import { ExportCenter } from './pages/ExportCenter';
import { SemanticSearch } from './pages/SemanticSearch';

// Additional Placeholders
const ReshootRisk = () => <div className="p-8"><h1 className="text-3xl font-bold mb-4">Reshoot Risk & Production Insights</h1><p className="text-editor-muted">Analyzing sequence risk factors...</p></div>;
const TrainingLearning = () => <div className="p-8"><h1 className="text-3xl font-bold mb-4">Training & Learning</h1><p className="text-editor-muted">Fine-tuning AI models on your editing style...</p></div>;
const Settings = () => <div className="p-8"><h1 className="text-3xl font-bold mb-4">System Settings</h1><p className="text-editor-muted">Configure GPU acceleration and AI model weights...</p></div>;

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="upload" element={<MediaUpload />} />
          <Route path="monitor" element={<AIMonitor />} />
          <Route path="timeline" element={<Timeline />} />
          <Route path="script" element={<ScriptCoverage />} />
          <Route path="emotion" element={<EmotionPerformance />} />
          <Route path="continuity" element={<ContinuityQuality />} />
          <Route path="intelligence" element={<DirectorIntelligence />} />
          <Route path="search" element={<SemanticSearch />} />
          <Route path="risk" element={<ReshootRisk />} />
          <Route path="training" element={<TrainingLearning />} />
          <Route path="export" element={<ExportCenter />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
