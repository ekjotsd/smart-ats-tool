# 📊 Project Summary - AI Hiring Platform

## 🎯 Overview
The AI Hiring Platform is a comprehensive Flask-based web application that leverages artificial intelligence to streamline the recruitment process for three key user types: applicants, recruiters, and hiring companies.

## 🏗️ Architecture

### Technology Stack
- **Backend**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI/ML**: OpenAI GPT models, Groq LLM, LangChain
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **File Processing**: PyPDF2, ReportLab
- **Vector Database**: FAISS (for RAG system)

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App     │    │   AI Services   │
│   (Bootstrap)   │◄──►│   (Python)      │◄──►│   (OpenAI/Groq) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (SQLite/PG)   │
                       └─────────────────┘
```

## 👥 User Roles

### 🎓 Applicants

### 🏢 Recruiters

### 🏭 Hiring Companies


## 🔧 Core Modules

### 1. Authentication & Authorization
- Role-based access control
- User registration/login

### 2. Resume Processing
- PDF text extraction
- AI-powered analysis
- ATS optimization scoring
- Skills extraction

### 3. AI Integration
- OpenAI API integration
- Groq LLM support
- Multiple model selection
- Error handling & fallbacks

### 4. RAG System
- Document processing
- Vector embeddings
- Semantic search
- Context-aware responses

### 5. PDF Generation
- Dynamic resume creation
- Cover letter formatting
- Professional templates
- Multi-format export

## 📈 Performance Metrics

### Response Times
- Resume analysis: ~10-15 seconds
- Cover letter generation: ~5-8 seconds
- FAQ responses: ~2-3 seconds
- Interview questions: ~3-5 seconds



## 📊 Database Schema

### Core Tables
```sql
users (id, username, email, role, created_at)
analysis_results (id, user_id, resume_data, analysis_data, created_at)
cover_letters (id, user_id, content, tone, created_at)
assessments (id, user_id, questions, responses, scores, created_at)
interviews (id, user_id, questions, responses, evaluation, created_at)
```

## 🔌 API Endpoints

### Public Endpoints
- `GET /` - Home page
- `POST /login` - User authentication
- `GET /logout` - User logout

### Applicant Endpoints
- `POST /analyze_resume` - Resume analysis
- `POST /generate_cover_letter` - Cover letter creation
- `POST /generate_updated_resume` - Resume enhancement
- `POST /faq_chat` - FAQ assistant

### Recruiter Endpoints
- `POST /api/generate_questions` - Psychometric questions
- `POST /api/evaluate_assessment` - Assessment scoring
- `POST /api/rank_resumes` - Resume ranking

### Company Endpoints
- `POST /api/generate_interview_questions` - Interview questions
- `POST /api/evaluate_interview_responses` - Response evaluation

