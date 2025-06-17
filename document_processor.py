import pandas as pd
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_job_descriptions(file_path):
    """Load job descriptions from CSV file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Job descriptions file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} job descriptions from {file_path}")
    return df

def process_job_descriptions(df):
    """Process job descriptions into documents"""
    documents = []
    
    # Handle different possible column names
    title_cols = ['Job Title', 'job_title', 'title', 'Title']
    desc_cols = ['Job Description', 'job_description', 'description', 'Description']
    
    title_col = next((col for col in title_cols if col in df.columns), None)
    desc_col = next((col for col in desc_cols if col in df.columns), None)
    
    if not title_col or not desc_col:
        raise ValueError(f"Required columns not found. Available columns: {df.columns.tolist()}")
    
    # Process each job description
    for idx, row in df.iterrows():
        title = str(row[title_col]).strip()
        description = str(row[desc_col]).strip()
        
        if pd.isna(row[title_col]) or pd.isna(row[desc_col]):
            continue
            
        # Create a comprehensive document
        content = f"""Job Title: {title}

Job Description:
{description}

Key Information:
- Position: {title}
- Industry Context: This role involves responsibilities and requirements typical for {title} positions
- Skills and Qualifications: As outlined in the job description above
"""
        
        # Create a document with metadata
        doc = Document(
            page_content=content,
            metadata={
                "title": title,
                "source": "job_descriptions_dataset",
                "doc_type": "job_description",
                "doc_id": f"job_{idx}"
            }
        )
        documents.append(doc)
    
    print(f"Processed {len(documents)} job description documents")
    return documents

def add_career_guidance_documents():
    """Add general career guidance documents"""
    career_docs = []
    
    # Resume writing tips
    resume_content = """
    Resume Writing Best Practices:
    
    1. Format and Structure:
    - Use a clean, professional format with consistent fonts and spacing
    - Keep it to 1-2 pages for most positions
    - Use reverse chronological order for work experience
    - Include clear section headers: Contact Info, Summary, Experience, Education, Skills
    
    2. Content Guidelines:
    - Write a compelling professional summary that highlights your key strengths
    - Use action verbs to describe your accomplishments
    - Quantify achievements with specific numbers and metrics
    - Tailor your resume for each job application
    - Include relevant keywords from the job description
    
    3. Common Mistakes to Avoid:
    - Don't include irrelevant personal information
    - Avoid gaps in employment without explanation
    - Don't use generic templates without customization
    - Avoid spelling and grammar errors
    """
    
    career_docs.append(Document(
        page_content=resume_content,
        metadata={"title": "Resume Writing Guide", "source": "career_guidance", "doc_type": "guidance"}
    ))
    
    # Interview preparation
    interview_content = """
    Interview Preparation Guide:
    
    1. Research and Preparation:
    - Research the company, its mission, values, and recent news
    - Understand the job role and requirements thoroughly
    - Prepare specific examples using the STAR method (Situation, Task, Action, Result)
    - Practice common interview questions and behavioral questions
    
    2. During the Interview:
    - Dress professionally and arrive 10-15 minutes early
    - Maintain good eye contact and confident body language
    - Listen carefully to questions and provide specific examples
    - Ask thoughtful questions about the role and company
    
    3. Follow-up:
    - Send a thank-you email within 24 hours
    - Reiterate your interest in the position
    - Address any concerns that may have come up during the interview
    """
    
    career_docs.append(Document(
        page_content=interview_content,
        metadata={"title": "Interview Preparation Guide", "source": "career_guidance", "doc_type": "guidance"}
    ))
    
    # Job search strategies
    job_search_content = """
    Job Search Strategies:
    
    1. Job Search Platforms:
    - Use major job boards like LinkedIn, Indeed, Glassdoor
    - Check company websites directly for openings
    - Network through professional associations and alumni networks
    - Consider working with recruiters in your field
    
    2. Application Best Practices:
    - Customize your resume and cover letter for each application
    - Follow application instructions carefully
    - Apply within the first few days of posting when possible
    - Keep track of your applications and follow up appropriately
    
    3. Building Your Professional Brand:
    - Optimize your LinkedIn profile with a professional photo and compelling headline
    - Share relevant industry content and engage with your network
    - Consider creating a portfolio website for creative fields
    - Maintain a consistent professional image across platforms
    """
    
    career_docs.append(Document(
        page_content=job_search_content,
        metadata={"title": "Job Search Strategies", "source": "career_guidance", "doc_type": "guidance"}
    ))
    
    # Salary negotiation
    salary_content = """
    Salary Negotiation Guide:
    
    1. Research and Preparation:
    - Research market rates for your position using sites like Glassdoor, PayScale
    - Consider your experience level, location, and company size
    - Prepare a range rather than a single number
    - Document your achievements and value proposition
    
    2. Negotiation Strategies:
    - Wait for an offer before discussing salary
    - Express enthusiasm for the role before negotiating
    - Consider the total compensation package, not just base salary
    - Be prepared to justify your requested salary with specific examples
    
    3. Beyond Salary:
    - Consider negotiating benefits, vacation time, flexible work arrangements
    - Professional development opportunities and training budgets
    - Stock options or equity participation
    - Job title and career advancement opportunities
    """
    
    career_docs.append(Document(
        page_content=salary_content,
        metadata={"title": "Salary Negotiation Guide", "source": "career_guidance", "doc_type": "guidance"}
    ))
    
    return career_docs

def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Split documents into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunked_documents = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunked_documents)} chunks")
    return chunked_documents

def process_all_documents(job_descriptions_path=None):
    """Process both job descriptions and career guidance documents"""
    all_documents = []
    
    # Add career guidance documents
    career_docs = add_career_guidance_documents()
    all_documents.extend(career_docs)
    
    # Add job descriptions if path provided
    if job_descriptions_path and os.path.exists(job_descriptions_path):
        df = load_job_descriptions(job_descriptions_path)
        job_docs = process_job_descriptions(df)
        all_documents.extend(job_docs)
    
    return all_documents