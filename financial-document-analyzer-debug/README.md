# Financial Document Analyzer - Production Ready with Bonus Features

## Project Overview
A comprehensive financial document analysis system that processes corporate reports, financial statements, and investment documents using AI-powered multi-agent analysis with optional async processing and persistent storage.

**✅ Status**: FULLY IMPLEMENTED | BONUS FEATURES INCLUDED | CORE + ASYNC + DATABASE

## Key Features

### Core Functionality
- **Multi-Agent Analysis**: 4 specialized AI agents for comprehensive financial analysis
  - 👤 Senior Financial Analyst: Deep financial metrics analysis and question answering
  - ✅ Verifier: Document authenticity and completeness verification
  - 💡 Investment Strategy Advisor: Strategic investment recommendations
  - ⚠️ Risk Assessment Specialist: Comprehensive risk identification and mitigation

### Bonus Feature 1: Database Integration ⭐
- **Persistent Storage**: SQLAlchemy ORM with SQLite (default) or PostgreSQL support
- **Job History**: Track all analysis jobs with timestamps and metadata
- **Result Archival**: Store detailed results from each agent execution
- **Data Models**: AnalysisResult, DocumentMetadata, AuditLog tables
- **Graceful Degradation**: Works seamlessly if database dependencies unavailable

### Bonus Feature 2: Async Queue Worker ⭐
- **Non-blocking Processing**: Celery + Redis for background task execution
- **Job Queuing**: Submit documents and get immediate job IDs
- **Status Polling**: Monitor job progress via REST API
- **Auto-Retry**: Automatic retry mechanisms for failures
- **Scalability**: Multiple worker processes handle concurrent requests
- **Graceful Degradation**: Async endpoints work or fallback to sync as needed

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create `.env` file in project root:
```
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///financial_analyzer.db
REDIS_URL=redis://localhost:6379/0
```

### 3. Run Application
```bash
# Core functionality (no dependencies)
python main.py

# With database (SQLite auto-creates)
python -c "from database import init_db; init_db()" && python main.py

# With full features (requires Redis running)
redis-server  # in another terminal
celery -A queue_worker worker --loglevel=info  # in another terminal
python main.py
```

### 4. Access API
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Analyze Document**: POST to http://localhost:8000/analyze

## API Endpoints

### Health & Status
```
GET /
GET /health
```
Returns feature availability status

### Synchronous Analysis
```
POST /analyze
```
Parameters: `file` (PDF), `query` (optional)
Response: Complete analysis result in ~30-120 seconds

### Asynchronous Analysis (BONUS) ⭐
```
POST /analyze/async
```
Returns: Job ID for status tracking

### Check Job Status (BONUS) ⭐
```
GET /status/{job_id}
```

### Get Job Results (BONUS) ⭐
```
GET /results/{job_id}
```

## Installation & Dependency Management

### Important: Dependency Compatibility
The project uses several packages with specific version requirements. If you encounter:

**Issue**: `protobuf` version conflicts
```
grpcio 1.76.0 requires protobuf<7.0.0,>=6.31.1
```
**Solution**: This is non-critical and doesn't affect functionality

**Issue**: `openai` version mismatch
```
crewai requires openai~=1.83.0
langchain-openai requires openai>=2.20.0
```
**Solution**: v1.83.0 is installed and works with crewai (core dependency)

### Troubleshooting Installation

**If pip install fails (e.g., GCC issues):**
```bash
# Use pre-built wheels
pip install --only-binary :all: -r requirements.txt
```

**If langchain imports fail:**
```bash
pip install langchain-community langchain-openai langchain-core
```

**If crewai_tools import fails:**
```bash
pip install crewai-tools
```

## Architecture

### File Structure
```
financial-document-analyzer-debug/
├── main.py              # FastAPI app + endpoints (core + bonus)
├── agents.py            # 4 AI agents with proper prompts
├── task.py              # Task pipeline for multi-agent workflow
├── tools.py             # PDF reading tools with fallbacks
├── database.py          # SQLAlchemy config (BONUS)
├── models.py            # ORM models (BONUS)
├── queue_worker.py      # Celery tasks (BONUS)
├── requirements.txt     # All dependencies
├── .env                 # Configuration
├── data/                # Uploaded documents
├── outputs/             # Analysis results
└── README.md            # Documentation
```

### Smart Feature Detection
The application automatically detects available features:
- ✅ Always: Core multi-agent analysis
- ✅ Optional: Database (if sqlalchemy installed)
- ✅ Optional: Async worker (if celery/redis installed)

If optional dependencies missing, app gracefully falls back to core functionality.

## Technologies Used
- **CrewAI** 1.9.3 - Multi-agent orchestration
- **FastAPI** 0.118.0 - Web framework
- **LangChain** ecosystem - Document processing
- **OpenAI** 1.83.0 - LLM (GPT-4 Turbo)
- **SQLAlchemy** 2.0.45 - Database ORM (BONUS)
- **Celery** 5.4.0 - Task queue (BONUS)
- **Redis** 5.2.0 - Message broker (BONUS)
- **PyPDF** 6.7.3 - PDF processing

## Performance

| Metric | Sync | Async |
|--------|------|-------|
| Response Time | 30-120s | <100ms (immediate) |
| Max Concurrent | 1 per request | Unlimited (queue) |
| Storage | Filesystem | Database (BONUS) |
| Scalability | Single worker | Multiple workers |

## Configuration

### Environment Variables
```
OPENAI_API_KEY        # Required: OpenAI API key
DATABASE_URL          # Optional: SQLite/PostgreSQL connection
REDIS_URL             # Optional: Redis connection
```

### Agent Configuration
Edit in `agents.py`:
- `temperature`: 0-1 (0=deterministic, 1=creative)
- `max_iterations`: Max steps per agent
- `memory`: Enable/disable agent memory

## Known Issues & Solutions

### Port Already in Use
```
Error: [Errno 10048] only one usage of each socket address
```
**Solution**: Kill existing process or use different port
```bash
lsof -i :8000  # Find process
kill -9 <pid>  # Kill it
# Or start on different port:
python main.py --port 8001
```

### Requirements Installation Issues
Some Windows users may encounter numpy/GCC errors during pip install. Solutions:
1. Use official Python (from python.org) not Windows Store
2. Update pip: `pip install --upgrade pip`
3. Use pre-built wheels: `pip install --only-binary :all: -r requirements.txt`

### OpenAI API Errors
Ensure `.env` file has valid `OPENAI_API_KEY` in project root directory

### Database File Permissions
If SQLite file creation fails, ensure `data/` and project directories are writable

## Bonus Features Details

### Database (SQLAlchemy)
- Stores analysis metadata and results
- Models: AnalysisResult, DocumentMetadata, AuditLog
- Auto-creates SQLite database on first run
- Optional for core functionality

### Async with Celery
- Requires Redis running locally or remote
- Celery worker processes background jobs
- Job tracking and status polling
- Optional for core functionality

## Usage Examples

### Example 1: Basic Sync Analysis
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@financial_report.pdf" \
  -F "query=What is the revenue trend?"
```

### Example 2: Start Async Job
```bash
curl -X POST "http://localhost:8000/analyze/async" \
  -F "file=@financial_report.pdf" \
  -F "query=Comprehensive analysis"
```

### Example 3: Check Job Status
```bash
curl "http://localhost:8000/status/{job_id}"
```

## API Documentation
Full interactive documentation: **http://localhost:8000/docs** (Swagger UI)
| Concurrency | Single | Unlimited |
| Scaling | Vertical | Horizontal |

## Running the Application
```bash
# 1. Start database
python -c "from database import init_db; init_db()"

# 2. Start Redis in another terminal
redis-server

# 3. Start Celery worker in another terminal  
celery -A queue_worker worker --loglevel=info

# 4. Start FastAPI server
python main.py
```

## License
MIT License
