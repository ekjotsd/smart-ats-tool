# 🏗️ Smart ATS Flask Application - Repository Structure

## 📁 **Root Directory**
```
MCP/
├── 📄 flask_app.py              # Main Flask application (1,325 lines)
├── 📄 database.py               # Database configuration and models
├── 📄 utils.py                  # Utility functions and helpers
├── 📄 pdf_generator.py          # PDF generation with professional templates (994 lines)
├── 📄 interview_assistant.py    # AI-powered interview question generation (281 lines)
├── 📄 mcq_utils.py             # Multiple choice question utilities
├── 📄 requirements.txt          # Python dependencies
├── 📄 setup.py                  # Package setup configuration
├── 📄 test_api.py              # API testing utilities
├── 📄 test_psychometric.py     # Psychometric testing utilities
├── 📄 compile_scss.py          # SCSS compilation script
├── 📄 cookies.txt              # Session cookies storage
├── 📄 env.example              # Environment variables template
├── 📄 .gitignore               # Git ignore patterns
├── 📄 Dockerfile               # Docker container configuration
├── 📄 docker-compose.yml       # Multi-service Docker setup
└── 📄 quick_start.sh/.bat      # Platform-specific startup scripts
```

## 📂 **Core Directories**

### `/data/` - **Dataset Storage**
```
data/
├── 📊 job_descriptions.csv     # Job descriptions dataset
└── 📊 job_title_des.csv       # Job titles and descriptions mapping
```

### `/rag/` - **RAG System Components**
```
rag/
├── 📄 __init__.py              # Package initialization
├── 📄 document_processor.py    # Document processing pipeline (209 lines)
├── 📄 embeddings.py           # Embedding generation functions
├── 📄 llm_service.py          # LLM service providers
├── 📄 rag_qa_chain.py         # Question-answering chain
├── 📄 retriever.py            # Document retrieval strategies
└── 📄 vector_store.py         # Vector database operations
```

### `/scripts/` - **Setup & Automation**
```
scripts/
├── 📄 complete_setup.py        # Comprehensive setup automation
├── 📄 download_dataset.py      # Kaggle dataset downloader
├── 📄 index.py                # Index management utilities
├── 📄 init_vector_db.py       # Vector database initialization
├── 📄 setup.py                # Basic setup script
└── 📄 validate.py             # System validation checks
```

### `/templates/` - **HTML Templates**
```
templates/
├── 📄 base.html               # Base template with navigation
├── 📄 login.html              # User authentication
├── 📄 applicant_dashboard.html # Applicant interface
├── 📄 company_dashboard.html   # Company interface
├── 📄 recruiter_dashboard.html # Recruiter interface
├── 📄 analysis_results.html    # Resume analysis results
├── 📄 cover_letter_result.html # Cover letter generation
├── 📄 updated_resume_result.html # Resume optimization results
├── 📄 interview_assistant.html # Interview preparation
├── 📄 faq_assistant.html      # FAQ assistant interface
├── 📄 psychometric_test.html  # Psychometric testing
└── 📄 resume_ranking.html     # Resume ranking interface
```

### `/static/` - **Frontend Assets**
```
static/
├── css/
│   ├── 📄 dashboard.css       # Compiled dashboard styles
│   └── 📄 dashboard.scss      # SCSS source files
├── img/                       # Image assets
└── js/                        # JavaScript files
```

### `/uploads/` - **File Storage**
```
uploads/                       # User uploaded files (resumes, documents)
```

## 🔧 **Configuration Files**

### **Environment & Setup**
- `env.example` - Environment variables template
- `requirements.txt` - Python dependencies (Flask-focused)
- `.gitignore` - Comprehensive ignore patterns
- `setup.py` - Package configuration

### **Containerization**
- `Dockerfile` - Production-ready container
- `docker-compose.yml` - Multi-service setup

### **CI/CD**
- `.github/workflows/ci.yml` - GitHub Actions pipeline

## 📚 **Documentation**

### **Core Documentation**
- `README.md` - Complete project overview
- `CONTRIBUTING.md` - Contribution guidelines
- `DEPLOYMENT.md` - Deployment instructions
- `PROJECT_SUMMARY.md` - Technical architecture
- `LICENSE` - MIT license

### **Technical Documentation**
- `README_FLASK.md` - Flask-specific documentation
- `README_PDF_Enhancement.md` - PDF generation details
- `PDF_Layout_Improvements.md` - PDF layout specifications

## 🎯 **Key Features by File**

### **Core Application (`flask_app.py`)**
- User authentication and session management
- Resume analysis with ATS optimization
- AI-powered cover letter generation
- Interview question generation
- Psychometric testing with AI evaluation
- RAG-powered FAQ assistant
- Resume ranking and bulk processing
- PDF generation with professional templates

### **AI Components**
- `interview_assistant.py` - Interview question generation (281 lines)
- `mcq_utils.py` - Multiple choice question utilities
- `pdf_generator.py` - Professional PDF templates (994 lines)

### **RAG System**
- Complete document processing pipeline
- Vector database operations
- Intelligent question-answering
- Multi-provider LLM support

## 📊 **Repository Statistics**
- **Total Files**: 45+ files
- **Lines of Code**: 10,000+ lines
- **Main Application**: 1,325 lines (flask_app.py)
- **Templates**: 12 HTML files (5,000+ total lines)
- **AI Components**: 2,000+ lines
- **RAG System**: 1,000+ lines
- **Scripts**: 700+ lines

## 🚀 **Technology Stack**
- **Backend**: Flask, SQLite/PostgreSQL
- **AI/ML**: OpenAI/Groq APIs, LangChain, scikit-learn
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Vector DB**: Pinecone (for RAG system)

## 🎭 **User Types Supported**
1. **Applicants** - Resume optimization, cover letters, interview prep
2. **Recruiters** - Resume ranking, candidate evaluation
3. **Companies** - Bulk processing, hiring analytics

## 🔄 **Development Workflow**
1. **Setup**: Run `py setup.py` or `./quick_start.sh`
2. **Development**: `py flask_app.py` (development server)
3. **Testing**: `python test_api.py`
4. **Production**: Docker deployment with `docker-compose up`

---
*This structure represents a production-ready Flask application with comprehensive AI-powered hiring tools.* 