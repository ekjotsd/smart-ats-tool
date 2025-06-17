from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.utils import secure_filename
import os
import json
import sys
import warnings
from dotenv import load_dotenv
from database import init_db, insert_sample_users, validate_user
from utils import get_groq_response, extract_pdf_text, prepare_prompt, generate_cover_letter, generate_updated_resume, get_groq_chat_response
import requests
from bs4 import BeautifulSoup
from mcq_utils import QuestionGenerator, get_response
from groq import Groq
from PyPDF2 import PdfReader
from pdf_generator import generate_resume_pdf, generate_cover_letter_pdf


# Suppress LangChain deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")

# Add the current directory to sys.path for RAG imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# RAG imports
try:
    from rag.embeddings import get_embedding_function
    from rag.vector_store import get_or_create_vector_store
    from rag.retriever import get_retriever, get_multi_query_retriever, get_contextual_retriever
    from rag.llm_service import get_llm
    from rag.rag_qa_chain import create_rag_chain, create_conversation_chain
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: RAG modules not available: {e}")
    RAG_AVAILABLE = False

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db()
insert_sample_users()

# Model configurations
MODEL_DICT = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3 70B": "llama3-70b-8192",
    "Llama 3 8B": "llama3-8b-8192",
    "Mistral Saba 24B": "mistral-saba-24b",
    # OpenAI Models
    "GPT-4o": "gpt-4o",
    "GPT-4o Mini": "gpt-4o-mini",
    "GPT-4 Turbo": "gpt-4-turbo",
    "GPT-3.5 Turbo": "gpt-3.5-turbo"
}

def get_api_key_for_model(model):
    """Get the appropriate API key for the given model"""
    # OpenAI models
    openai_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    if model in openai_models:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(f"Warning: OPENAI_API_KEY not found in environment variables for model {model}")
            return None
        return api_key
    else:
        # Groq models (default)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print(f"Warning: GROQ_API_KEY not found in environment variables for model {model}")
            return None
        return api_key

def login_required(f):
    """Decorator to require login for protected routes"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def role_required(role):
    """Decorator to require specific role"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if session.get('role') != role:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

def get_analysis_data():
    """Retrieve analysis data from temporary storage"""
    if not session.get('has_analysis') or not session.get('analysis_id'):
        return None
    
    analysis_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{session['analysis_id']}_analysis.json")
    
    if not os.path.exists(analysis_file):
        return None
    
    try:
        with open(analysis_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading analysis data: {e}")
        return None

def cleanup_analysis_data():
    """Clean up temporary analysis files"""
    if session.get('analysis_id'):
        analysis_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{session['analysis_id']}_analysis.json")
        if os.path.exists(analysis_file):
            try:
                os.remove(analysis_file)
            except Exception as e:
                print(f"Error cleaning up analysis file: {e}")

def cleanup_old_analysis_files():
    """Clean up old analysis files and PDFs (older than 1 hour)"""
    try:
        import time
        current_time = time.time()
        upload_folder = app.config['UPLOAD_FOLDER']
        
        for filename in os.listdir(upload_folder):
            # Clean up both analysis JSON files and PDF files
            if filename.endswith('_analysis.json') or filename.endswith('.pdf'):
                filepath = os.path.join(upload_folder, filename)
                file_age = current_time - os.path.getmtime(filepath)
                
                # Remove files older than 1 hour (3600 seconds)
                if file_age > 3600:
                    try:
                        os.remove(filepath)
                        print(f"Cleaned up old file: {filename}")
                    except Exception as e:
                        print(f"Error cleaning up old file {filename}: {e}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

@app.route('/')
def index():
    """Landing page - redirect to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        user = validate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    cleanup_analysis_data()  # Clean up temporary files
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard based on user role"""
    role = session.get('role')
    username = session.get('username')
    
    if role == 'Applicant':
        # Check if there's existing analysis data
        analysis_data = None
        if session.get('has_analysis'):
            analysis_data = get_analysis_data()
        
        return render_template('applicant_dashboard.html', 
                             username=username, 
                             models=MODEL_DICT,
                             analysis=analysis_data['analysis'] if analysis_data else None,
                             resume_text=analysis_data['resume_text'] if analysis_data else None,
                             job_description=analysis_data['job_description'] if analysis_data else None,
                             model=analysis_data['model'] if analysis_data else None)
    elif role == 'Recruiter':
        return render_template('recruiter_dashboard.html', username=username)
    elif role == 'Hiring Company':
        return render_template('company_dashboard.html', username=username)
    else:
        flash('Unknown role', 'error')
        return redirect(url_for('login'))

@app.route('/analyze_resume', methods=['POST'])
@login_required
@role_required('Applicant')
def analyze_resume():
    """Analyze resume against job description"""
    try:
        # Clean up old analysis files
        cleanup_old_analysis_files()
        
        # Debug logging
        print("=== ANALYZE RESUME DEBUG ===")
        print(f"Request files: {list(request.files.keys())}")
        print(f"Request form: {dict(request.form)}")
        
        # Get form data
        job_description = request.form.get('job_description', '').strip()
        model = request.form.get('model', 'llama-3.3-70b-versatile')
        
        print(f"Job description length: {len(job_description)}")
        print(f"Model: {model}")
        
        # Check if file was uploaded
        if 'resume_file' not in request.files:
            print("ERROR: 'resume_file' not in request.files")
            flash('Please upload a resume file', 'error')
            return redirect(url_for('dashboard'))
        
        file = request.files['resume_file']
        print(f"File object: {file}")
        print(f"File filename: '{file.filename}'")
        print(f"File content type: {file.content_type}")
        
        # Check file content
        file_content = file.read()
        print(f"File content length: {len(file_content)} bytes")
        file.seek(0)  # Reset file pointer
        
        if not file.filename or file.filename == '':
            print("ERROR: File filename is empty or None")
            flash('Please select a file', 'error')
            return redirect(url_for('dashboard'))
            
        if len(file_content) == 0:
            print("ERROR: File content is empty")
            flash('The uploaded file is empty', 'error')
            return redirect(url_for('dashboard'))
        
        if not job_description:
            print("ERROR: Job description is empty")
            flash('Please provide a job description', 'error')
            return redirect(url_for('dashboard'))
        
        # Save and process file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from PDF (properly close file handle)
        with open(filepath, 'rb') as pdf_file:
            resume_text = extract_pdf_text(pdf_file)
        
        # Get API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            flash('API key not configured', 'error')
            return redirect(url_for('dashboard'))
        
        # Prepare prompt and get analysis
        input_prompt = prepare_prompt(resume_text, job_description)
        response = get_groq_response(model, api_key, input_prompt)
        response_json = json.loads(response)
        
        # Store only essential data in session (to avoid cookie size limit)
        session['has_analysis'] = True
        session['analysis_id'] = filename  # Use filename as unique identifier
        
        # Store full data in a temporary file or database (for production, use Redis/database)
        analysis_data = {
            'resume_text': resume_text,
            'job_description': job_description,
            'analysis': response_json,
            'model': model
        }
        
        # Save to temporary JSON file
        analysis_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}_analysis.json")
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f)
        
        # Clean up uploaded file (with error handling)
        try:
            import time
            time.sleep(0.1)  # Small delay to ensure file handle is released
            os.remove(filepath)
            print(f"Successfully cleaned up uploaded file: {filepath}")
        except Exception as cleanup_error:
            print(f"Warning: Could not delete uploaded file {filepath}: {cleanup_error}")
            # File will be cleaned up by the periodic cleanup function
        
        return render_template('applicant_dashboard.html', 
                             username=session.get('username'),
                             models=MODEL_DICT,
                             analysis=response_json,
                             resume_text=resume_text,
                             job_description=job_description,
                             model=model)
        
    except Exception as e:
        flash(f'Error analyzing resume: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/fetch_linkedin_job', methods=['POST'])
@login_required
@role_required('Applicant')
def fetch_linkedin_job():
    """Fetch job description from LinkedIn"""
    data = request.get_json()
    job_id = data.get('job_id', '').strip()
    
    if not job_id:
        return jsonify({'error': 'Please enter a LinkedIn Job ID'}), 400
    
    try:
        url = f"https://www.linkedin.com/jobs/view/{job_id}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'error': f'Failed to fetch job page: {response.status_code}'}), 400
        
        soup = BeautifulSoup(response.text, "html.parser")
        job_desc_div = soup.select_one("div.show-more-less-html__markup")
        
        if not job_desc_div:
            return jsonify({'error': 'Could not extract job description'}), 400
        
        job_description = job_desc_div.get_text(strip=True)
        return jsonify({'success': True, 'job_description': job_description})
        
    except Exception as e:
        return jsonify({'error': f'Error fetching job description: {str(e)}'}), 500

@app.route('/test_upload', methods=['POST'])
@login_required
def test_upload():
    """Test route to debug file upload"""
    print("=== TEST UPLOAD DEBUG ===")
    print(f"Request files: {list(request.files.keys())}")
    print(f"Request form: {dict(request.form)}")
    
    for key, file in request.files.items():
        print(f"File key: {key}, filename: {file.filename}, content_type: {file.content_type}")
    
    return jsonify({
        'files': list(request.files.keys()),
        'form': dict(request.form),
        'status': 'success'
    })

@app.route('/generate_cover_letter', methods=['POST'])
@login_required
@role_required('Applicant')
def generate_cover_letter_route():
    """Generate cover letter based on analysis"""
    try:
        tone = request.form.get('tone', 'professional')
        
        # Get analysis from temporary storage
        analysis_data = get_analysis_data()
        if not analysis_data:
            flash('No analysis data found. Please analyze your resume first.', 'error')
            return redirect(url_for('dashboard'))
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            flash('API key not configured', 'error')
            return redirect(url_for('dashboard'))
        
        # Generate cover letter
        cover_letter = generate_cover_letter(
            analysis_data['model'], 
            api_key, 
            analysis_data['job_description'], 
            analysis_data['resume_text'], 
            analysis_data['analysis'], 
            tone
        )
        
        return render_template('cover_letter_result.html', 
                             cover_letter=cover_letter,
                             tone=tone)
        
    except Exception as e:
        flash(f'Error generating cover letter: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/reset_analysis')
@login_required
@role_required('Applicant')
def reset_analysis():
    """Reset analysis and return to initial state"""
    try:
        # Clean up analysis data
        cleanup_analysis_data()
        
        # Clear analysis session data
        session.pop('has_analysis', None)
        session.pop('analysis_id', None)
        
        flash('Analysis reset successfully. You can start a new analysis.', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        flash(f'Error resetting analysis: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/generate_updated_resume', methods=['POST'])
@login_required
@role_required('Applicant')
def generate_updated_resume_route():
    """Generate updated resume based on analysis"""
    try:
        # Get analysis from temporary storage
        analysis_data = get_analysis_data()
        if not analysis_data:
            flash('No analysis data found. Please analyze your resume first.', 'error')
            return redirect(url_for('dashboard'))
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            flash('API key not configured', 'error')
            return redirect(url_for('dashboard'))
        
        # Generate updated resume
        updated_resume = generate_updated_resume(
            analysis_data['model'], 
            api_key, 
            analysis_data['job_description'], 
            analysis_data['resume_text'], 
            analysis_data['analysis']
        )
        
        return render_template('updated_resume_result.html', 
                             updated_resume=updated_resume)
        
    except Exception as e:
        flash(f'Error generating updated resume: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/download_resume_pdf', methods=['POST'])
@login_required
@role_required('Applicant')
def download_resume_pdf():
    """Generate and download resume as PDF"""
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        
        if not resume_text:
            return jsonify({'error': 'Resume text is required'}), 400
        
        # Generate PDF
        pdf_data = generate_resume_pdf(resume_text)
        
        # Return PDF as response
        response = Response(
            pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': 'attachment; filename=optimized_resume.pdf',
                'Content-Type': 'application/pdf'
            }
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

@app.route('/api/download_cover_letter_pdf', methods=['POST'])
@login_required
@role_required('Applicant')
def download_cover_letter_pdf():
    """Generate and download cover letter as PDF"""
    try:
        data = request.get_json()
        cover_letter_text = data.get('cover_letter_text', '')
        applicant_name = data.get('applicant_name', '')
        contact_info = data.get('contact_info', '')
        tone = data.get('tone', 'professional')
        
        if not cover_letter_text:
            return jsonify({'error': 'Cover letter text is required'}), 400
        
        # Generate PDF
        pdf_data = generate_cover_letter_pdf(cover_letter_text, applicant_name, contact_info)
        
        # Return PDF as response
        response = Response(
            pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=cover_letter_{tone}.pdf',
                'Content-Type': 'application/pdf'
            }
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

# Interview Assistant Routes for Hiring Companies
@app.route('/interview_assistant')
@login_required
@role_required('Hiring Company')
def interview_assistant():
    """Interview Assistant dashboard for hiring companies"""
    return render_template('interview_assistant.html', 
                         username=session.get('username'),
                         models=MODEL_DICT)

@app.route('/api/generate_interview_questions', methods=['POST'])
@login_required
@role_required('Hiring Company')
def generate_interview_questions():
    """Generate AI-powered interview questions"""
    try:
        from interview_assistant import InterviewAssistant
        
        data = request.get_json()
        job_description = data.get('job_description', '')
        candidate_resume = data.get('candidate_resume', '')
        model = data.get('model', 'llama-3.3-70b-versatile')
        question_count = int(data.get('question_count', 10))
        categories = data.get('categories', ['technical', 'behavioral', 'cultural'])
        difficulty = data.get('difficulty', 'mid')
        interview_type = data.get('interview_type', 'screening')
        
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
        
        # Get API key
        api_key = get_api_key_for_model(model)
        if not api_key:
            return jsonify({'error': f'API key not configured for model: {model}'}), 400
        
        # Generate questions
        assistant = InterviewAssistant()
        questions_data = assistant.generate_interview_questions(
            model=model,
            api_key=api_key,
            job_description=job_description,
            candidate_resume=candidate_resume,
            question_count=question_count,
            categories=categories,
            difficulty=difficulty,
            interview_type=interview_type
        )
        
        if 'error' in questions_data:
            return jsonify({'error': questions_data['error']}), 500
        
        # Extract the questions array from the response
        questions_list = questions_data.get('questions', [])
        
        return jsonify({
            'success': True,
            'questions': questions_list,
            'interview_tips': questions_data.get('interview_tips', []),
            'total_duration': questions_data.get('total_duration', 60)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating questions: {str(e)}'}), 500

@app.route('/api/evaluate_interview_responses', methods=['POST'])
@login_required
@role_required('Hiring Company')
def evaluate_interview_responses():
    """Evaluate candidate interview responses"""
    try:
        from interview_assistant import InterviewAssistant
        
        data = request.get_json()
        questions = data.get('questions', [])
        responses = data.get('responses', {})
        model = data.get('model', 'llama-3.3-70b-versatile')
        
        if not questions or not responses:
            return jsonify({'error': 'Questions and responses are required'}), 400
        
        # Get API key
        api_key = get_api_key_for_model(model)
        if not api_key:
            return jsonify({'error': f'API key not configured for model: {model}'}), 400
        
        # Evaluate responses
        assistant = InterviewAssistant()
        evaluation_data = assistant.evaluate_responses(
            model=model,
            api_key=api_key,
            questions=questions,
            responses=responses
        )
        
        if 'error' in evaluation_data:
            return jsonify({'error': evaluation_data['error']}), 500
        
        return jsonify({
            'success': True,
            'evaluation': evaluation_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error evaluating responses: {str(e)}'}), 500

@app.route('/psychometric_test')
@login_required
@role_required('Recruiter')
def psychometric_test():
    """Psychometric test page for recruiters"""
    return render_template('psychometric_test.html', models=MODEL_DICT)

@app.route('/api/generate_questions', methods=['POST'])
@login_required
@role_required('Recruiter')
def generate_questions():
    """API endpoint to generate psychometric questions"""
    print("=== GENERATE QUESTIONS DEBUG ===")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    print(f"Session user: {session.get('username')}")
    print(f"Session role: {session.get('role')}")
    
    try:
        data = request.get_json()
        print(f"Request data: {data}")
        
        from mcq_utils import QuestionGenerator
        
        model = data.get('model', 'llama3-8b-8192')
        num_questions = int(data.get('num_questions', 10))
        test_type = data.get('test_type', 'mixed')
        
        print(f"Model: {model}, Questions: {num_questions}, Type: {test_type}")
        
        generator = QuestionGenerator(model)
        questions = []
        
        if test_type == 'mixed':
            # Half personality, half workplace
            personality_count = num_questions // 2
            workplace_count = num_questions - personality_count
            
            # Generate personality questions
            for _ in range(personality_count):
                question = generator.generate_mcq(topic="Personality Traits")
                questions.append({
                    'type': 'MCQ',
                    'question': question.question,
                    'options': question.options,
                    'category': "Personality Traits"
                })
            
            # Generate workplace questions
            for _ in range(workplace_count):
                question = generator.generate_mcq(topic="Workplace Behaviors")
                questions.append({
                    'type': 'MCQ',
                    'question': question.question,
                    'options': question.options,
                    'category': "Workplace Behaviors"
                })
        
        elif test_type == 'personality':
            # All personality questions
            for _ in range(num_questions):
                question = generator.generate_mcq(topic="Personality Traits")
                questions.append({
                    'type': 'MCQ',
                    'question': question.question,
                    'options': question.options,
                    'category': "Personality Traits"
                })
        
        elif test_type == 'workplace':
            # All workplace questions
            for _ in range(num_questions):
                question = generator.generate_mcq(topic="Workplace Behaviors")
                questions.append({
                    'type': 'MCQ',
                    'question': question.question,
                    'options': question.options,
                    'category': "Workplace Behaviors"
                })
        
        return jsonify({
            'success': True,
            'questions': questions,
            'config': data
        })
        
    except Exception as e:
        print(f"Error in generate_questions: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to generate questions: {str(e)}'
        }), 500

@app.route('/api/evaluate_assessment', methods=['POST'])
@login_required
@role_required('Recruiter')
def evaluate_assessment():
    """API endpoint to evaluate psychometric assessment"""
    print("=== EVALUATE ASSESSMENT DEBUG ===")
    try:
        from mcq_utils import get_response
        
        data = request.get_json()
        print(f"Request data: {data}")
        
        questions = data.get('questions', [])
        answers = data.get('answers', [])
        config = data.get('config', {})
        model = config.get('model', 'llama3-8b-8192')
        
        print(f"Model: {model}")
        print(f"Questions count: {len(questions)}")
        print(f"Answers count: {len(answers)}")
        print(f"Config: {config}")
        
        results = []
        
        for i, (question, answer) in enumerate(zip(questions, answers)):
            if answer is None:
                print(f"Skipping question {i+1} - no answer provided")
                continue
                
            result_dict = {
                'question_number': i + 1,
                'question': question['question'],
                'question_type': question['type'],
                'user_answer': answer,
                'category': question.get('category', 'Unknown')
            }
            
            print(f"Processing question {i+1}: {question['question'][:50]}...")
            print(f"User answer: {answer}")
            
            try:
                # Get AI analysis
                response = get_response(model, result_dict)
                print(f"AI response for question {i+1}: {response}")
                
                result_dict['Dimension'] = response.get('inferred_dimension', 'Unknown')
                result_dict['Score'] = response.get('normalized_score', 0.0)
                result_dict['Label'] = response.get('label', 'Unknown')
                result_dict['Reasoning'] = response.get('reasoning', 'No analysis available')
                
                results.append(result_dict)
                print(f"Successfully processed question {i+1}")
                
            except Exception as question_error:
                print(f"Error processing question {i+1}: {str(question_error)}")
                print(f"Question error type: {type(question_error)}")
                import traceback
                traceback.print_exc()
                
                # Add a fallback result
                result_dict['Dimension'] = 'Unknown'
                result_dict['Score'] = 0.5
                result_dict['Label'] = 'Moderate'
                result_dict['Reasoning'] = f'Analysis failed: {str(question_error)}'
                results.append(result_dict)
        
        print(f"Total results: {len(results)}")
        
        return jsonify({
            'success': True,
            'results': results,
            'config': config
        })
        
    except Exception as e:
        print(f"Error in evaluate_assessment: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to evaluate assessment: {str(e)}'
        }), 500

@app.route('/faq_assistant')
@login_required
@role_required('Applicant')
def faq_assistant():
    """FAQ Assistant page for applicants"""
    return render_template('faq_assistant.html', username=session.get('username'))

# RAG Helper Functions
def classify_query_intent(query, llm):
    """Use LLM to intelligently classify if query needs RAG retrieval or simple response"""
    intent_prompt = f"""
    You are an intelligent query classifier for a career assistant. Analyze the user input and determine if it requires:

    1. RAG_RETRIEVAL - Questions that need specific information from documents about careers, jobs, industries, skills, etc.
       Examples: "How do I optimize my resume?", "What skills are needed for data science?", "How to prepare for interviews?"
    
    2. SIMPLE_RESPONSE - Greetings, thanks, casual conversation, or questions that can be answered without document retrieval.
       Examples: "Hi", "Hello", "Thank you", "How are you?", "What can you help with?"

    User input: "{query}"
    
    Think about whether this query would benefit from searching through job descriptions, career guides, and professional documents.
    
    Respond with only: RAG_RETRIEVAL or SIMPLE_RESPONSE
    """
    
    try:
        # Use the LLM to classify intent
        if hasattr(llm, 'invoke'):
            response = llm.invoke(intent_prompt)
        else:
            response = llm(intent_prompt)
        
        # Extract the intent from response - handle response objects properly
        if hasattr(response, 'content'):
            intent = response.content.strip().upper()
        elif isinstance(response, str):
            intent = response.strip().upper()
        else:
            intent = str(response).strip().upper()
        
        # Validate the intent
        if 'RAG_RETRIEVAL' in intent:
            return 'RAG_RETRIEVAL'
        elif 'SIMPLE_RESPONSE' in intent:
            return 'SIMPLE_RESPONSE'
        else:
            # Default to RAG_RETRIEVAL for ambiguous cases
            return 'RAG_RETRIEVAL'
            
    except Exception as e:
        # Fallback: use simple heuristics
        query_lower = query.lower().strip()
        
        # Simple greetings and short phrases - likely don't need RAG
        if (len(query.split()) <= 3 and 
            any(word in query_lower for word in ['hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye'])):
            return 'SIMPLE_RESPONSE'
        
        # Career-related keywords - likely need RAG
        career_keywords = ['resume', 'cv', 'job', 'career', 'interview', 'salary', 'skill', 'industry', 'position', 'application']
        if any(keyword in query_lower for keyword in career_keywords):
            return 'RAG_RETRIEVAL'
        
        # Default to RAG for longer queries
        return 'RAG_RETRIEVAL' if len(query.split()) > 3 else 'SIMPLE_RESPONSE'

def classify_career_query_type(query):
    """Classify the career query type for contextual retrieval"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['resume', 'cv', 'application', 'portfolio']):
        return "resume"
    elif any(word in query_lower for word in ['interview', 'preparation', 'questions', 'behavioral']):
        return "interview"
    elif any(word in query_lower for word in ['salary', 'compensation', 'negotiate', 'pay', 'benefits']):
        return "salary"
    else:
        return "general"

def generate_simple_response(query, llm):
    """Generate appropriate responses for non-career queries using LLM"""
    
    response_prompt = f"""
    You are a helpful AI career assistant. The user has said: "{query}"
    
    This appears to be a simple greeting, casual conversation, or general question that doesn't require searching through career documents.
    
    Respond appropriately:
    - If it's a greeting: Welcome them warmly and briefly introduce your career guidance capabilities
    - If it's thanks: Acknowledge their gratitude and offer continued help
    - If it's goodbye: Wish them well in their career journey
    - If it's casual conversation: Politely redirect to career topics while being friendly
    - If it's asking what you can help with: List your main capabilities
    
    Keep your response:
    - Friendly and professional
    - Concise (2-3 sentences max)
    - Focused on career guidance topics
    - Use appropriate emojis
    
    Mention that you can specifically help with:
    - Resume optimization and ATS systems
    - Interview preparation
    - Job search strategies
    - Salary negotiation
    - Career development
    """
    
    try:
        if hasattr(llm, 'invoke'):
            response = llm.invoke(response_prompt)
        else:
            response = llm(response_prompt)
        
        # Extract content from response object
        if hasattr(response, 'content'):
            return response.content
        elif isinstance(response, str):
            return response
        else:
            return str(response)
    except Exception as e:
        # Fallback response that adapts to the query
        query_lower = query.lower()
        if any(word in query_lower for word in ['hi', 'hello', 'hey', 'good']):
            return "Hi there! 👋 I'm your AI career assistant. I can help you with resumes, interviews, job search strategies, and career development. What would you like to know about?"
        elif any(word in query_lower for word in ['thank', 'thanks']):
            return "You're welcome! 😊 Feel free to ask me anything else about your career or job search."
        elif any(word in query_lower for word in ['bye', 'goodbye', 'see you']):
            return "Goodbye! 👋 Best of luck with your career journey. Feel free to come back anytime!"
        elif any(word in query_lower for word in ['help', 'what', 'can', 'do']):
            return "I'm here to help with your career! 🚀 I can assist with resume optimization, interview prep, job search strategies, salary negotiation, and career development. What specific topic interests you?"
        else:
            return "I'm specialized in career guidance! 💼 I can help you with resumes, interviews, job searching, and career development. What career topic would you like to explore?"

def process_rag_question(prompt, llm_provider="groq", model="llama3-8b-8192", retrieval_strategy="contextual", num_sources=5, enable_memory=True):
    """Process a question using the RAG system"""
    try:
        if not RAG_AVAILABLE:
            return "Sorry, the RAG system is not available. Please check the system configuration.", [], "RAG system not available"
        
        # Initialize RAG components
        embedding_function = get_embedding_function()
        vector_store = get_or_create_vector_store(embedding_function)
        
        # Select retriever based on strategy
        search_kwargs = {"k": num_sources}
        
        if retrieval_strategy == "contextual":
            query_type = classify_career_query_type(prompt)
            retriever = get_contextual_retriever(vector_store, query_type, search_kwargs)
        elif retrieval_strategy == "multi_query":
            llm = get_llm(provider=llm_provider, model=model)
            retriever = get_multi_query_retriever(vector_store, llm, search_kwargs)
        else:
            retriever = get_retriever(vector_store, search_kwargs, retrieval_strategy)
        
        llm = get_llm(provider=llm_provider, model=model)
        
        # Create QA chain
        if enable_memory:
            qa_chain = create_conversation_chain(llm, retriever)
        else:
            qa_chain = create_rag_chain(llm, retriever)
        
        # First, classify the intent of the query
        intent = classify_query_intent(prompt, llm)
        
        # Handle non-career queries without RAG
        if intent == 'SIMPLE_RESPONSE':
            response = generate_simple_response(prompt, llm)
            return response, [], None
        
        # For career questions, proceed with RAG pipeline
        if intent == 'RAG_RETRIEVAL':
            # Use contextual retriever if selected
            if retrieval_strategy == "contextual":
                query_type = classify_career_query_type(prompt)
                contextual_retriever = get_contextual_retriever(vector_store, query_type, search_kwargs)
                # Create a new chain with the contextual retriever
                if enable_memory:
                    qa_chain = create_conversation_chain(llm, contextual_retriever)
                else:
                    qa_chain = create_rag_chain(llm, contextual_retriever)
            
            # Prepare input based on chain type
            if enable_memory and hasattr(qa_chain, 'memory'):
                # For conversation chain with memory
                if hasattr(qa_chain, 'combine_docs_chain'):
                    response = qa_chain.invoke({"question": prompt, "chat_history": []})
                else:
                    response = qa_chain.invoke({"question": prompt})
            else:
                # For regular RAG chain
                response = qa_chain.invoke({"query": prompt})
            
            # Extract answer from response - handle different response formats
            answer = None
            if isinstance(response, dict):
                answer = response.get("answer") or response.get("result", "I apologize, but I couldn't generate a response.")
            else:
                answer = str(response)
                
            sources = response.get("source_documents", []) if isinstance(response, dict) else []
            
            return answer, sources, None
        
        # Fallback for any unhandled cases
        response = generate_simple_response(prompt, llm)
        return response, [], None
        
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        return None, [], error_msg

@app.route('/faq_chat', methods=['POST'])
@login_required
@role_required('Applicant')
def faq_chat():
    """Handle FAQ chat messages via AJAX"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        llm_provider = data.get('llm_provider', 'groq')
        model = data.get('model', 'llama3-8b-8192')
        retrieval_strategy = data.get('retrieval_strategy', 'contextual')
        num_sources = int(data.get('num_sources', 5))
        enable_memory = data.get('enable_memory', True)
        
        if not message:
            return jsonify({'error': 'Please enter a message'}), 400
        
        # Process the question using RAG
        answer, sources, error_msg = process_rag_question(
            message, llm_provider, model, retrieval_strategy, num_sources, enable_memory
        )
        
        if error_msg:
            return jsonify({'error': error_msg}), 500
        
        # Format sources for JSON response
        formatted_sources = []
        if sources:
            for i, doc in enumerate(sources):
                source_info = {
                    'title': doc.metadata.get('title', f'Document {i+1}'),
                    'doc_type': doc.metadata.get('doc_type', 'Unknown'),
                    'content_preview': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    'relevance': 1 - doc._distance if hasattr(doc, '_distance') else None
                }
                formatted_sources.append(source_info)
        
        return jsonify({
            'success': True,
            'response': answer,
            'sources': formatted_sources
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500

@app.route('/resume_ranking')
@login_required
@role_required('Recruiter')
def resume_ranking():
    """Resume ranking page for recruiters"""
    return render_template('resume_ranking.html', models=MODEL_DICT)

@app.route('/api/rank_resumes', methods=['POST'])
@login_required
@role_required('Recruiter')
def rank_resumes_api():
    """API endpoint to rank resumes against job description"""
    try:
        # Get form data
        job_description = request.form.get('job_description', '').strip()
        model = request.form.get('model', 'deepseek-r1-distill-llama-70b')
        method = request.form.get('method', 'tfidf')
        
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
        
        # Get uploaded files
        resume_files = []
        for key in request.files:
            if key.startswith('resume_'):
                file = request.files[key]
                if file and file.filename.endswith('.pdf'):
                    resume_files.append(file)
        
        if not resume_files:
            return jsonify({'error': 'At least one resume file is required'}), 400
        
        # Extract text from PDFs
        resumes_data = []
        for file in resume_files:
            try:
                # Extract text from PDF
                pdf_reader = PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                resumes_data.append({
                    'filename': file.filename,
                    'text': text
                })
            except Exception as e:
                return jsonify({'error': f'Error processing {file.filename}: {str(e)}'}), 400
        
        # Rank resumes based on method
        if method == 'tfidf':
            results = rank_resumes_tfidf(job_description, resumes_data)
        else:  # llm method
            results = rank_resumes_llm(job_description, resumes_data, model)
        
        return jsonify({
            'success': True,
            'method': method,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': f'Error ranking resumes: {str(e)}'}), 500

def rank_resumes_tfidf(job_description, resumes_data):
    """Rank resumes using TF-IDF similarity"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Prepare documents
    documents = [job_description] + [resume['text'] for resume in resumes_data]
    
    # Calculate TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Calculate cosine similarity
    job_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(job_vector, resume_vectors).flatten()
    
    # Create results with rankings
    results = []
    for i, resume in enumerate(resumes_data):
        results.append({
            'filename': resume['filename'],
            'score': float(similarities[i]),
            'explanation': None
        })
    
    # Sort by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results

def rank_resumes_llm(job_description, resumes_data, model):
    """Rank resumes using LLM-based scoring"""
    from groq import Groq
    
    # Determine which API to use based on model
    openai_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    if model in openai_models:
        # Use OpenAI API
        try:
            from openai import OpenAI
        except ImportError:
            raise Exception("OpenAI library not installed. Please install it with: pip install openai")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OPENAI_API_KEY not found in environment variables")
        
        client = OpenAI(api_key=api_key)
    else:
        # Use Groq API
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise Exception("GROQ_API_KEY not found in environment variables")
        
        client = Groq(api_key=api_key)
    
    results = []
    
    for resume in resumes_data:
        try:
            prompt = f"""
            You are a hiring assistant. Evaluate the following resume against this job description and provide a score from 0 to 100 for how well it fits. Also provide a short explanation.

            Job Description:
            {job_description}

            Resume:
            {resume['text']}

            Return the output in the format:
            Score: <score>
            Explanation: <reason>
            """
            
            if model in openai_models:
                # OpenAI API call
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": " "}
                    ],
                    temperature=0.7,
                    top_p=1
                )
            else:
                # Groq API call
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": " "}
                    ],
                    temperature=0.7,
                    top_p=1,
                    stream=False,
                    stop=None,
                )
            
            response = completion.choices[0].message.content
            
            # Parse the response
            score = 0
            explanation = ""
            for line in response.split("\n"):
                if line.startswith("Score:"):
                    try:
                        score = int(line.split(":")[1].strip())
                    except:
                        score = 0
                elif line.startswith("Explanation:"):
                    explanation = line.split(":", 1)[1].strip()
            
            results.append({
                'filename': resume['filename'],
                'score': score,
                'explanation': explanation
            })
            
        except Exception as e:
            results.append({
                'filename': resume['filename'],
                'score': 0,
                'explanation': f'Error processing resume: {str(e)}'
            })
    
    # Sort by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results

@app.route('/interview_session/<session_id>')
@login_required
@role_required('Hiring Company')
def interview_session(session_id):
    """Individual interview session page"""
    return render_template('interview_session.html', 
                         session_id=session_id,
                         username=session.get('username'),
                         models=MODEL_DICT)

@app.route('/api/extract_resume_text', methods=['POST'])
def extract_resume_text():
    """Extract text from uploaded PDF resume"""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Extract text from PDF using the existing utility function
        from utils import extract_pdf_text
        
        try:
            resume_text = extract_pdf_text(file)
            
            if not resume_text or resume_text.strip() == '':
                return jsonify({'error': 'Could not extract text from PDF. Please ensure the PDF contains readable text.'}), 400
            
            return jsonify({
                'success': True,
                'text': resume_text,
                'filename': file.filename
            })
            
        except Exception as pdf_error:
            return jsonify({'error': f'Failed to process PDF: {str(pdf_error)}'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Job Matching functionality removed - focusing on other agentic features

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  
