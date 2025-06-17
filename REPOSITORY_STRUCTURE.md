# 🏗️ Smart ATS Flask Application - Repository Structure

## 📁 **Root Directory**
```
Smart ATS Tool/
├── 📄 flask_app.py              # Main Flask application (1,325 lines)
├── 📄 database.py               # Database configuration and models
├── 📄 utils.py                  # Utility functions and helpers
├── 📄 pdf_generator.py          # PDF generation with professional templates (994 lines)
├── 📄 interview_assistant.py    # AI-powered interview question generation (281 lines)
├── 📄 mcq_utils.py             # Multiple choice question utilities
├── 📄 requirements.txt          # Python dependencies
├── 📄 setup.py                  # Package setup configuration
├── 📄 compile_scss.py          # SCSS compilation script
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

