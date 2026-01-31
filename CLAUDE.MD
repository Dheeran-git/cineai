# SmartCut AI - Testing Strategy & Improvement Recommendations

**Project:** SmartCut AI (Semantic Video Search Engine)
**Type:** Full-stack AI-powered video editing intelligence platform
**Tech Stack:** React 19 + TypeScript + Vite (Frontend) | FastAPI + Python (Backend)
**Review Date:** 2026-01-31

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Current Test Coverage Analysis](#current-test-coverage-analysis)
3. [Critical Testing Gaps](#critical-testing-gaps)
4. [Recommended Testing Strategy](#recommended-testing-strategy)
5. [Priority Test Implementation Roadmap](#priority-test-implementation-roadmap)
6. [Specific Test Recommendations by Module](#specific-test-recommendations-by-module)
7. [Testing Best Practices](#testing-best-practices)
8. [Quick Wins](#quick-wins)

---

## Project Overview

SmartCut AI is a sophisticated video editing assistant that combines:
- **Computer Vision** (YOLOv8) for object detection and quality analysis
- **Speech Recognition** (Whisper) for audio transcription
- **NLP** (spaCy) for semantic understanding
- **Semantic Search** (FAISS) for intent-based footage search
- **Emotion Analysis** for performance evaluation
- **Timeline Management** for editing workflows

### Architecture
```
/src                  # React frontend (TypeScript)
  /pages              # 13 feature pages
  /components         # Layout components
  /store              # Zustand state management
  /lib                # API utilities

/backend              # FastAPI backend (Python)
  /app
    /api/api_v1/endpoints  # 9 REST API route modules
    /services              # 11 AI/ML service modules
    /models                # 6 SQLAlchemy models
    /schemas               # Pydantic validators
  /tests              # Current test suite (minimal)
```

---

## Current Test Coverage Analysis

### Backend Tests (4 files)

#### ✅ `/backend/tests/test_basic.py` (38 lines)
- **What it tests:** Root endpoint integration test
- **Coverage:** Single API endpoint (`GET /`)
- **Issues:**
  - Uses monkeypatch incorrectly (context manager without effect)
  - Database connection not properly mocked
  - Missing `httpx` dependency for `TestClient`
  - No assertion on actual response structure
- **Coverage:** ~0.5% of API endpoints

#### ✅ `/backend/tests/test_services_entropy.py` (58 lines)
- **What it tests:** Audio and video service variety/randomness
- **Coverage:** Fallback logic in `audio_service` and `cv_service`
- **Issues:**
  - Tests synthetic data variety, not actual functionality
  - No real file processing validation
  - Mocks are declared but not properly applied
  - No edge case handling
- **Coverage:** ~5% of service logic (only fallback paths)

#### ⚠️ `/backend/test_api.py` (38 lines)
- **What it tests:** Manual integration test for media upload
- **Issues:**
  - Not using pytest framework (manual script)
  - Hardcoded file paths (Windows-specific)
  - Requires server to be running
  - No assertions or failure detection
  - Not part of automated test suite

#### ⚠️ `/backend/test_whisper.py` (46 lines)
- **What it tests:** Whisper model loading and transcription
- **Issues:**
  - Hardcoded Windows paths (`C:\Users\Prajw\...`)
  - Manual test script (not pytest)
  - No assertions or expected outcomes
  - Platform-dependent (Windows-only)

### Frontend Tests
**❌ ZERO test files found**
- No Jest/Vitest configuration
- No React Testing Library
- No component tests
- No integration tests
- No E2E tests

### Overall Coverage Estimate
- **Backend:** ~2-3% code coverage
- **Frontend:** 0% code coverage
- **Integration:** 0% (no end-to-end tests)

---

## Critical Testing Gaps

### 🔴 High Priority (P0) - Critical Functionality

1. **No API Endpoint Testing**
   - 9 API route groups (`/projects`, `/media`, `/processing`, `/timeline`, `/export`, `/script`, `/intelligence`, `/training`, `/search`)
   - 0 comprehensive endpoint tests
   - **Risk:** Breaking changes undetected, regression bugs in production

2. **No Service Layer Testing**
   - 11 service modules with complex AI/ML logic
   - Only 2 services partially tested (fallback paths only)
   - **Risk:** AI model failures, incorrect embeddings, search quality issues

3. **No Database Model Testing**
   - 6 SQLAlchemy models (Project, Scene, Take, Camera, MomentEmbedding, SearchFeedback)
   - No relationship testing, no constraint validation
   - **Risk:** Data integrity issues, broken foreign keys, orphaned records

4. **No Frontend Testing**
   - 13 pages, 0 component tests
   - Complex state management (Zustand) untested
   - **Risk:** UI bugs, broken workflows, state corruption

5. **No Integration Testing**
   - No end-to-end workflow tests
   - No frontend-backend integration
   - **Risk:** Communication failures, contract mismatches

### 🟡 Medium Priority (P1) - Quality & Reliability

6. **No Error Handling Tests**
   - No validation of error responses
   - No boundary condition testing
   - **Risk:** Poor error messages, crashes

7. **No Performance Testing**
   - Video processing is CPU/GPU intensive
   - No load testing, no concurrency tests
   - **Risk:** Timeouts, resource exhaustion

8. **No Security Testing**
   - File upload validation untested
   - No SQL injection prevention tests
   - **Risk:** Security vulnerabilities

### 🟢 Low Priority (P2) - Developer Experience

9. **No Mock Data Factories**
   - Difficult to write new tests
   - No test fixtures

10. **No CI/CD Test Pipeline**
    - Tests not automated
    - No pre-commit hooks

---

## Recommended Testing Strategy

### Testing Pyramid
```
         /\
        /E2E\       10% - End-to-end (Playwright/Cypress)
       /------\
      /  API  \     20% - API Integration (pytest + TestClient)
     /----------\
    / Component \   30% - Component Tests (Vitest + RTL)
   /--------------\
  /     Unit      \ 40% - Unit Tests (pytest + Vitest)
 /------------------\
```

### Test Distribution Goals
- **Backend Unit Tests:** 150-200 tests (70% coverage target)
- **Backend Integration Tests:** 40-60 tests (all API endpoints)
- **Frontend Unit Tests:** 80-120 tests (components, hooks, utils)
- **Frontend Integration Tests:** 30-50 tests (user workflows)
- **E2E Tests:** 10-20 critical paths

---

## Priority Test Implementation Roadmap

### Phase 1: Foundation (Week 1-2) 🚀
**Goal:** Establish testing infrastructure and critical path coverage

#### Backend Setup
- [ ] Install missing dependencies (`httpx`, `pytest-cov`)
- [ ] Configure pytest.ini with proper test discovery
- [ ] Set up test database (SQLite in-memory)
- [ ] Create conftest.py with fixtures
- [ ] Add coverage reporting

#### Frontend Setup
- [ ] Install Vitest + React Testing Library
- [ ] Configure vitest.config.ts
- [ ] Set up testing utilities (render helpers, mock providers)
- [ ] Install @testing-library/user-event

#### Critical Path Tests
- [ ] Test all `/media` endpoints (upload, list, get, delete)
- [ ] Test `/projects` CRUD operations
- [ ] Test semantic search endpoint
- [ ] Test video processing orchestration
- [ ] Test dashboard page rendering

**Expected Outcome:** 15-20% backend coverage, 5-10% frontend coverage

---

### Phase 2: Core Service Testing (Week 3-4) 🔬
**Goal:** Validate AI/ML services with real and mocked data

#### Service Tests
- [ ] `cv_service.py` - Object detection, quality scoring
- [ ] `audio_service.py` - Transcription, audio analysis
- [ ] `nlp_service.py` - Text processing, entity extraction
- [ ] `scoring_service.py` - Confidence calculation logic
- [ ] `semantic_search_service.py` - FAISS vector search
- [ ] `intent_embedding_service.py` - Embedding generation
- [ ] `visual_embedding_service.py` - CLIP embeddings
- [ ] `timeline_service.py` - Timeline aggregation
- [ ] `export_service.py` - FCP XML and EDL export

#### Mock Strategy
- Mock heavy ML models (Whisper, YOLO, CLIP) in unit tests
- Use small pre-generated embeddings for search tests
- Create fixture videos (2-5 seconds) for integration tests

**Expected Outcome:** 40-50% backend coverage

---

### Phase 3: API & Integration Testing (Week 5-6) 🔗
**Goal:** Comprehensive API testing and frontend-backend integration

#### API Integration Tests
- [ ] Test all 9 API route groups end-to-end
- [ ] Validate request/response schemas (Pydantic)
- [ ] Test error responses (400, 404, 500)
- [ ] Test file upload edge cases (large files, invalid formats)
- [ ] Test CORS and authentication (if implemented)

#### Frontend Integration Tests
- [ ] User upload workflow (select file → upload → processing)
- [ ] Search workflow (query → results → playback)
- [ ] Timeline editing (accept/reject takes, add notes)
- [ ] Export workflow (select format → generate → download)

**Expected Outcome:** 60-70% backend coverage, 30-40% frontend coverage

---

### Phase 4: Component & UI Testing (Week 7-8) 🎨
**Goal:** Comprehensive frontend component coverage

#### Component Tests
- [ ] Layout components (Sidebar, MainLayout, StatusBar)
- [ ] Page components (Dashboard, Upload, Search, Timeline)
- [ ] UI interactions (drag & drop, file selection, form submission)
- [ ] State management (Zustand store actions)
- [ ] Routing and navigation
- [ ] Error boundaries

#### Visual Regression (Optional)
- [ ] Install Chromatic or Percy
- [ ] Capture component snapshots
- [ ] Detect visual regressions

**Expected Outcome:** 70-80% backend coverage, 60-70% frontend coverage

---

### Phase 5: E2E & Performance Testing (Week 9-10) 🚀
**Goal:** Validate complete user journeys and system performance

#### E2E Tests (Playwright)
- [ ] Full video processing pipeline
- [ ] Multi-user collaboration scenarios
- [ ] Export and download workflows
- [ ] Error recovery scenarios

#### Performance Tests
- [ ] Load testing (concurrent uploads)
- [ ] Video processing benchmarks
- [ ] Search query latency
- [ ] Database query optimization

**Expected Outcome:** 80%+ coverage, production-ready test suite

---

## Specific Test Recommendations by Module

### Backend API Endpoints

#### `/api/v1/media` (High Priority)
```python
# test_media_endpoints.py

def test_upload_valid_video(client, tmp_video_file):
    """Test uploading a valid MP4 file."""
    response = client.post("/api/v1/media/upload",
                           files={"file": tmp_video_file})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["file_name"].endswith(".mp4")

def test_upload_invalid_format(client):
    """Test uploading non-video file returns 400."""
    response = client.post("/api/v1/media/upload",
                           files={"file": ("test.txt", b"content", "text/plain")})
    assert response.status_code == 400
    assert "Invalid file format" in response.json()["detail"]

def test_upload_oversized_file(client):
    """Test uploading file exceeding size limit."""
    large_file = b"x" * (500 * 1024 * 1024)  # 500MB
    response = client.post("/api/v1/media/upload",
                           files={"file": ("huge.mp4", large_file, "video/mp4")})
    assert response.status_code == 413

def test_list_media(client, db_session):
    """Test listing all uploaded media."""
    # Setup: Create 3 test takes
    response = client.get("/api/v1/media/")
    assert response.status_code == 200
    takes = response.json()
    assert len(takes) == 3

def test_get_media_by_id(client, sample_take):
    """Test retrieving single media item."""
    response = client.get(f"/api/v1/media/{sample_take.id}")
    assert response.status_code == 200
    assert response.json()["id"] == sample_take.id

def test_get_nonexistent_media(client):
    """Test 404 for non-existent media ID."""
    response = client.get("/api/v1/media/99999")
    assert response.status_code == 404
```

**Tests Needed:** 15-20 tests covering CRUD, validation, edge cases

---

#### `/api/v1/search` (High Priority)
```python
# test_search_endpoints.py

def test_semantic_search_basic(client, indexed_takes):
    """Test basic semantic search query."""
    response = client.post("/api/v1/search/semantic",
                          json={"query": "happy moment with laughter"})
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) > 0
    assert "score" in results[0]

def test_semantic_search_empty_query(client):
    """Test search with empty query returns 400."""
    response = client.post("/api/v1/search/semantic", json={"query": ""})
    assert response.status_code == 400

def test_visual_search(client, sample_image):
    """Test visual similarity search."""
    response = client.post("/api/v1/search/visual",
                          files={"image": sample_image})
    assert response.status_code == 200

def test_search_with_filters(client):
    """Test search with scene/emotion filters."""
    response = client.post("/api/v1/search/semantic",
                          json={"query": "dialogue",
                                "scene_id": 1,
                                "emotion": "neutral"})
    assert response.status_code == 200
```

**Tests Needed:** 10-15 tests for search logic, filters, ranking

---

### Backend Services

#### `cv_service.py` (Critical)
```python
# test_cv_service.py

@pytest.mark.asyncio
async def test_analyze_video_with_objects(mock_yolo_model):
    """Test video analysis detects objects correctly."""
    result = await cv_service.analyze_video("test_video.mp4")
    assert "objects" in result
    assert len(result["objects"]) > 0
    assert result["blur_score"] >= 0

@pytest.mark.asyncio
async def test_analyze_video_fallback_no_opencv():
    """Test fallback behavior when OpenCV unavailable."""
    with patch.object(cv_service, 'CV2_AVAILABLE', False):
        result = await cv_service.analyze_video("test.mp4")
        assert result["video_description"].startswith("Video analysis")
        assert "objects" in result

@pytest.mark.asyncio
async def test_analyze_nonexistent_video():
    """Test error handling for missing video file."""
    with pytest.raises(FileNotFoundError):
        await cv_service.analyze_video("nonexistent.mp4")

def test_blur_detection(sample_video_frame):
    """Test blur score calculation on sample frames."""
    score = cv_service.calculate_blur_score(sample_video_frame)
    assert 0 <= score <= 100
```

**Tests Needed:** 20-25 tests covering detection, scoring, edge cases

---

#### `audio_service.py` (Critical)
```python
# test_audio_service.py

@pytest.mark.asyncio
async def test_transcribe_audio(mock_whisper_model):
    """Test audio transcription with Whisper."""
    result = await audio_service.analyze_audio("test_audio.mp4")
    assert "transcript" in result
    assert len(result["transcript"]) > 0

@pytest.mark.asyncio
async def test_silence_detection():
    """Test silence period detection in audio."""
    result = await audio_service.analyze_audio("silent_video.mp4")
    assert result["silence_percentage"] > 80

@pytest.mark.asyncio
async def test_emotion_detection_in_audio():
    """Test emotion classification from audio features."""
    result = await audio_service.analyze_audio("happy_speech.mp4")
    assert "emotion" in result
    assert result["emotion"] in ["happy", "sad", "neutral", "angry"]

@pytest.mark.asyncio
async def test_audio_quality_metrics():
    """Test audio quality scoring (noise, clipping)."""
    result = await audio_service.analyze_audio("noisy_audio.mp4")
    assert "audio_quality_score" in result
```

**Tests Needed:** 15-20 tests for transcription, emotion, quality

---

#### `semantic_search_service.py` (Critical)
```python
# test_semantic_search.py

def test_build_faiss_index(sample_embeddings):
    """Test FAISS index creation from embeddings."""
    index = semantic_search_service.build_index(sample_embeddings)
    assert index.ntotal == len(sample_embeddings)

def test_search_similar_embeddings():
    """Test finding similar embeddings in FAISS."""
    results = semantic_search_service.search(query_embedding, top_k=5)
    assert len(results) == 5
    assert all(r["score"] >= 0 for r in results)

def test_search_empty_index():
    """Test searching empty index returns empty results."""
    results = semantic_search_service.search(query_embedding, top_k=5)
    assert len(results) == 0

def test_embedding_normalization():
    """Test embeddings are L2 normalized for FAISS."""
    embedding = np.array([1.0, 2.0, 3.0])
    normalized = semantic_search_service.normalize_embedding(embedding)
    assert np.isclose(np.linalg.norm(normalized), 1.0)
```

**Tests Needed:** 12-18 tests for indexing, search, edge cases

---

### Frontend Components

#### Dashboard Page
```typescript
// Dashboard.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import { Dashboard } from '@/pages/Dashboard';
import { useProjectStore } from '@/store/useProjectStore';

vi.mock('@/store/useProjectStore');

describe('Dashboard', () => {
  it('renders project statistics', async () => {
    useProjectStore.mockReturnValue({
      projects: [{ id: 1, name: 'Test Project', takes: 10 }],
      loading: false
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
      expect(screen.getByText('10 takes')).toBeInTheDocument();
    });
  });

  it('shows loading state while fetching data', () => {
    useProjectStore.mockReturnValue({ projects: [], loading: true });

    render(<Dashboard />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('renders issue breakdown chart', () => {
    render(<Dashboard />);
    expect(screen.getByTestId('issue-chart')).toBeInTheDocument();
  });
});
```

**Tests Needed:** 60-80 component tests across 13 pages

---

#### Media Upload Component
```typescript
// MediaUpload.test.tsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MediaUpload } from '@/pages/MediaUpload';
import { api } from '@/lib/api';

vi.mock('@/lib/api');

describe('MediaUpload', () => {
  it('allows file selection via drag and drop', async () => {
    render(<MediaUpload />);

    const file = new File(['video'], 'test.mp4', { type: 'video/mp4' });
    const dropzone = screen.getByText(/drag.*drop/i);

    fireEvent.drop(dropzone, { dataTransfer: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.mp4')).toBeInTheDocument();
    });
  });

  it('uploads file and shows progress', async () => {
    api.post.mockResolvedValue({ data: { id: 1 } });

    render(<MediaUpload />);
    const file = new File(['video'], 'test.mp4', { type: 'video/mp4' });

    // Simulate file drop
    // ...

    await waitFor(() => {
      expect(screen.getByText(/uploading/i)).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText(/upload complete/i)).toBeInTheDocument();
    });
  });

  it('validates file type and shows error', () => {
    render(<MediaUpload />);
    const file = new File(['text'], 'test.txt', { type: 'text/plain' });

    // Simulate drop
    // ...

    expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
  });
});
```

**Tests Needed:** 40-60 interaction tests for forms, uploads, workflows

---

#### Zustand Store Tests
```typescript
// useProjectStore.test.ts

import { renderHook, act } from '@testing-library/react';
import { useProjectStore } from '@/store/useProjectStore';

describe('useProjectStore', () => {
  beforeEach(() => {
    useProjectStore.setState({ projects: [] });
  });

  it('adds a new project', () => {
    const { result } = renderHook(() => useProjectStore());

    act(() => {
      result.current.addProject({ name: 'New Project' });
    });

    expect(result.current.projects).toHaveLength(1);
    expect(result.current.projects[0].name).toBe('New Project');
  });

  it('updates project status', () => {
    const { result } = renderHook(() => useProjectStore());

    act(() => {
      result.current.addProject({ id: 1, name: 'Test' });
      result.current.updateProjectStatus(1, 'processing');
    });

    expect(result.current.projects[0].status).toBe('processing');
  });

  it('removes a project', () => {
    const { result } = renderHook(() => useProjectStore());

    act(() => {
      result.current.addProject({ id: 1, name: 'Test' });
      result.current.removeProject(1);
    });

    expect(result.current.projects).toHaveLength(0);
  });
});
```

**Tests Needed:** 15-20 store tests for state management

---

### Database Models

#### Model Relationship Tests
```python
# test_models.py

def test_create_project(db_session):
    """Test creating a project."""
    project = Project(name="Test Project", description="Test")
    db_session.add(project)
    db_session.commit()

    assert project.id is not None
    assert project.created_at is not None

def test_project_scene_relationship(db_session):
    """Test one-to-many relationship between project and scenes."""
    project = Project(name="Test")
    scene1 = Scene(project=project, number=1, name="Scene 1")
    scene2 = Scene(project=project, number=2, name="Scene 2")

    db_session.add_all([project, scene1, scene2])
    db_session.commit()

    assert len(project.scenes) == 2
    assert scene1.project_id == project.id

def test_cascade_delete_project(db_session):
    """Test deleting project cascades to scenes and takes."""
    project = Project(name="Test")
    scene = Scene(project=project, number=1)
    take = Take(scene=scene, number=1, file_path="/test.mp4")

    db_session.add_all([project, scene, take])
    db_session.commit()

    db_session.delete(project)
    db_session.commit()

    assert db_session.query(Scene).count() == 0
    assert db_session.query(Take).count() == 0

def test_moment_embedding_constraints(db_session):
    """Test embedding vector dimensions are validated."""
    take = Take(scene_id=1, number=1, file_path="/test.mp4")
    embedding = MomentEmbedding(
        take=take,
        embedding_blob=b"invalid"  # Should be 512-dim float array
    )

    with pytest.raises(ValueError):
        db_session.add(embedding)
        db_session.commit()
```

**Tests Needed:** 25-35 tests for models, relationships, constraints

---

## Testing Best Practices

### 1. Test Structure (AAA Pattern)
```python
def test_example():
    # Arrange - Set up test data
    project = Project(name="Test")

    # Act - Perform the action
    result = project_service.create(project)

    # Assert - Verify the outcome
    assert result.id is not None
```

### 2. Fixture Management
```python
# conftest.py

@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def sample_take(db_session):
    """Create a sample take for testing."""
    take = Take(scene_id=1, number=1, file_path="/test.mp4", duration=10.5)
    db_session.add(take)
    db_session.commit()
    return take

@pytest.fixture
def mock_whisper_model():
    """Mock Whisper model for fast tests."""
    with patch('whisper.load_model') as mock:
        mock.return_value.transcribe.return_value = {
            "text": "Sample transcription"
        }
        yield mock
```

### 3. Mock External Dependencies
```python
# Mock heavy ML models to avoid slow tests
@patch('app.services.cv_service.YOLO')
@patch('app.services.audio_service.whisper.load_model')
async def test_processing_pipeline(mock_whisper, mock_yolo):
    mock_yolo.return_value.predict.return_value = []
    mock_whisper.return_value.transcribe.return_value = {"text": "test"}

    result = await orchestrator.process_take("test.mp4")
    assert result["status"] == "complete"
```

### 4. Frontend Testing Utilities
```typescript
// test-utils.tsx

import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

export function renderWithRouter(component: React.ReactElement) {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
}

export const mockProjectStore = {
  projects: [],
  addProject: vi.fn(),
  updateProject: vi.fn(),
  removeProject: vi.fn()
};
```

### 5. Coverage Thresholds
```ini
# pytest.ini
[pytest]
addopts =
    --cov=app
    --cov-report=html
    --cov-report=term
    --cov-fail-under=70
```

```json
// vitest.config.ts
export default {
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      lines: 70,
      branches: 70,
      functions: 70,
      statements: 70
    }
  }
}
```

---

## Quick Wins

These tests can be implemented immediately for fast impact:

### Backend (1-2 hours)
1. ✅ Fix `test_basic.py` - Remove broken monkeypatch, add httpx
2. ✅ Add `/api/v1/projects` GET/POST tests (5 tests)
3. ✅ Add `/api/v1/media/upload` validation tests (3 tests)
4. ✅ Add database model creation tests (5 tests)
5. ✅ Add `export_service.py` FCP XML generation test (2 tests)

### Frontend (2-3 hours)
1. ✅ Install Vitest + React Testing Library
2. ✅ Test Dashboard page renders (1 test)
3. ✅ Test Sidebar navigation (2 tests)
4. ✅ Test useProjectStore actions (3 tests)
5. ✅ Test API utility axios configuration (2 tests)

**Total:** 23 tests in 3-5 hours = 3-5% coverage boost

---

## Testing Infrastructure Setup

### Backend Configuration

#### `pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
    --asyncio-mode=auto
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

#### `backend/conftest.py`
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import Base
from app.core.config import settings

@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(test_db_engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

---

### Frontend Configuration

#### `vitest.config.ts`
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.config.{ts,js}',
        '**/*.d.ts'
      ],
      lines: 70,
      branches: 70,
      functions: 70,
      statements: 70
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
```

#### `src/test/setup.ts`
```typescript
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() { return []; }
  unobserve() {}
};
```

#### Update `package.json`
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  },
  "devDependencies": {
    "@testing-library/react": "^16.0.1",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/user-event": "^14.5.2",
    "@vitest/ui": "^3.0.0",
    "jsdom": "^26.0.0",
    "vitest": "^3.0.0",
    "@vitest/coverage-v8": "^3.0.0"
  }
}
```

---

## CI/CD Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov httpx
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm run test:coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Metrics & Goals

### Current State
- **Backend Coverage:** ~2-3%
- **Frontend Coverage:** 0%
- **Total Test Count:** 4 files, ~20 assertions
- **Test Execution Time:** <5 seconds

### 3-Month Target
- **Backend Coverage:** 70-80%
- **Frontend Coverage:** 60-70%
- **Total Test Count:** 300-400 tests
- **Test Execution Time:** <2 minutes (unit), <10 minutes (integration)

### 6-Month Target
- **Backend Coverage:** 85%+
- **Frontend Coverage:** 75%+
- **E2E Tests:** 15-20 critical paths
- **Performance Tests:** Load testing for video processing
- **Security Tests:** OWASP Top 10 validation

---

## Resources & Tools

### Documentation
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [React Testing Library](https://testing-library.com/react)
- [Vitest Documentation](https://vitest.dev/)

### Recommended Libraries
- **Backend:** `pytest-mock`, `pytest-asyncio`, `faker`, `factory-boy`
- **Frontend:** `msw` (API mocking), `@testing-library/user-event`, `axe-core` (accessibility)
- **E2E:** `Playwright` or `Cypress`

---

## Next Steps

1. **Immediate Actions (Today)**
   - Install missing test dependencies
   - Fix broken test files
   - Set up test database configuration

2. **This Week**
   - Implement 20-30 quick win tests
   - Set up CI/CD pipeline
   - Create test fixtures and utilities

3. **This Month**
   - Complete Phase 1 & 2 of roadmap
   - Achieve 30-40% backend coverage
   - Set up frontend testing infrastructure

4. **Ongoing**
   - Write tests for all new features
   - Maintain 70%+ coverage threshold
   - Run tests before every commit/PR

---

## Conclusion

SmartCut AI is a sophisticated application with **critical testing gaps**. The current test suite provides <5% overall coverage, leaving the majority of functionality untested. This poses significant risks for:

- **Production Stability:** Bugs in AI/ML pipelines can corrupt data
- **User Experience:** Untested UI can break workflows
- **Maintainability:** Refactoring without tests is dangerous

**Recommended Priority:** Treat testing as a **P0 task**. Allocate 30-40% of sprint capacity to building the test suite over the next 2-3 months.

The roadmap above provides a clear path to achieve 70%+ coverage with a balanced testing strategy across unit, integration, and E2E tests.

---

**Questions or concerns?** Review this document with the team and adjust priorities based on business needs and risk tolerance.
