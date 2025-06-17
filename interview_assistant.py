#!/usr/bin/env python3
"""
Intelligent Interview Assistant for Hiring Companies
Provides AI-powered interview question generation, candidate evaluation, and interview management
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils import get_groq_response, get_openai_response

class InterviewAssistant:
    """AI-powered interview assistant for hiring companies"""
    
    def __init__(self):
        self.question_categories = {
            'technical': 'Technical Skills & Knowledge',
            'behavioral': 'Behavioral & Situational',
            'cultural': 'Cultural Fit & Values',
            'leadership': 'Leadership & Management',
            'problem_solving': 'Problem Solving & Critical Thinking',
            'communication': 'Communication & Collaboration'
        }
        
        self.difficulty_levels = {
            'junior': 'Entry Level (0-2 years)',
            'mid': 'Mid Level (3-5 years)',
            'senior': 'Senior Level (6+ years)',
            'lead': 'Lead/Principal Level'
        }
        
        self.interview_types = {
            'screening': 'Initial Screening',
            'technical': 'Technical Interview',
            'behavioral': 'Behavioral Interview',
            'final': 'Final Round',
            'panel': 'Panel Interview'
        }

    def generate_interview_questions(self, model: str, api_key: str, job_description: str, 
                                   candidate_resume: str = "", question_count: int = 10,
                                   categories: List[str] = None, difficulty: str = "mid",
                                   interview_type: str = "screening") -> Dict:
        """Generate AI-powered interview questions"""
        
        if categories is None:
            categories = ['technical', 'behavioral', 'cultural']
        
        prompt = f"""
        You are an expert interview assistant. Generate exactly {question_count} professional interview questions for this position.

        Job Description: {job_description}
        Candidate Resume: {candidate_resume if candidate_resume else "No resume provided"}
        Difficulty Level: {difficulty}
        Question Categories: {', '.join(categories)}

        IMPORTANT: Return ONLY valid JSON in this exact format. Do not include any explanations or markdown formatting:

        {{
            "questions": [
                {{
                    "id": 1,
                    "category": "technical",
                    "question": "What is your experience with Python web frameworks?",
                    "follow_up_questions": ["Can you compare Django and Flask?", "How do you handle database migrations?"],
                    "evaluation_criteria": ["Technical knowledge", "Problem-solving ability"],
                    "time_minutes": 8
                }},
                {{
                    "id": 2,
                    "category": "behavioral", 
                    "question": "Tell me about a challenging project you worked on.",
                    "follow_up_questions": ["How did you overcome obstacles?", "What would you do differently?"],
                    "evaluation_criteria": ["Communication skills", "Learning ability"],
                    "time_minutes": 7
                }}
            ],
            "interview_tips": ["Focus on specific examples", "Ask follow-up questions"],
            "total_duration": 45
        }}

        Generate {question_count} questions covering these categories: {', '.join(categories)}. Ensure all JSON syntax is correct with proper quotes and commas.
        """

        try:
            if model.startswith('gpt-'):
                response = get_openai_response(model, prompt)
            else:
                response = get_groq_response(model, api_key, prompt)
            
            # Try to parse JSON directly first
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract and fix JSON
                import re
                
                # Remove any markdown formatting
                response = re.sub(r'```json\s*', '', response)
                response = re.sub(r'```\s*$', '', response)
                
                # Try to find JSON object
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    
                    # Common fixes for malformed JSON
                    json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                    json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                    json_str = re.sub(r'"(\d+)":', r'\1:', json_str)  # Fix quoted numbers as keys
                    
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass
                
                # If all parsing attempts fail, return a fallback structure
                return {
                    'error': f'Failed to parse JSON response: {response[:200]}...',
                    'questions': [],
                    'interview_tips': ['Unable to generate tips due to parsing error'],
                    'total_duration': 60
                }
            
        except Exception as e:
            return {'error': str(e)}

    def evaluate_responses(self, model: str, api_key: str, questions: List[Dict], 
                         responses: Dict) -> Dict:
        """Evaluate candidate responses"""
        
        prompt = f"""
        Evaluate these interview responses:
        
        Questions: {json.dumps(questions)}
        Responses: {json.dumps(responses)}
        
        Return JSON with scores (1-5), feedback, and recommendation.
        """
        
        try:
            if model.startswith('gpt-'):
                response = get_openai_response(model, prompt)
            else:
                response = get_groq_response(model, api_key, prompt)
            
            return json.loads(response)
            
        except Exception as e:
            return {'error': str(e)}

    def generate_interview_report(self, questions_data: Dict, evaluation_data: Dict,
                                candidate_info: Dict, interviewer_notes: str = "") -> Dict:
        """Generate comprehensive interview report"""
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'candidate_name': candidate_info.get('name', 'Unknown'),
                'position': candidate_info.get('position', 'Unknown'),
                'interviewer': candidate_info.get('interviewer', 'Unknown'),
                'interview_date': candidate_info.get('interview_date', datetime.now().date().isoformat())
            },
            'executive_summary': {
                'overall_score': evaluation_data.get('overall_assessment', {}).get('percentage', 'N/A'),
                'recommendation': evaluation_data.get('overall_assessment', {}).get('recommendation', 'N/A'),
                'key_highlights': evaluation_data.get('overall_feedback', {}).get('key_strengths', []),
                'main_concerns': evaluation_data.get('overall_feedback', {}).get('areas_for_improvement', [])
            },
            'detailed_evaluation': evaluation_data,
            'interview_questions': questions_data,
            'interviewer_notes': interviewer_notes,
            'next_steps': evaluation_data.get('next_steps', {}),
            'attachments': {
                'candidate_resume': candidate_info.get('resume_path', ''),
                'job_description': candidate_info.get('job_description', '')
            }
        }
        
        return report

    def get_question_suggestions(self, job_title: str, industry: str = "") -> Dict:
        """Get pre-built question suggestions for common roles"""
        
        suggestions = {
            'software_engineer': {
                'technical': [
                    "Explain the difference between REST and GraphQL APIs",
                    "How do you handle database optimization in your applications?",
                    "Describe your approach to code review and testing"
                ],
                'behavioral': [
                    "Tell me about a challenging bug you had to fix",
                    "How do you stay updated with new technologies?",
                    "Describe a time when you had to work with a difficult team member"
                ]
            },
            'product_manager': {
                'strategic': [
                    "How do you prioritize features in a product roadmap?",
                    "Describe your approach to gathering user requirements",
                    "How do you measure product success?"
                ],
                'behavioral': [
                    "Tell me about a product launch that didn't go as planned",
                    "How do you handle conflicting stakeholder requirements?",
                    "Describe your experience with cross-functional teams"
                ]
            },
            'marketing_manager': {
                'strategic': [
                    "How do you develop a go-to-market strategy?",
                    "Describe your approach to measuring marketing ROI",
                    "How do you identify and target new customer segments?"
                ],
                'behavioral': [
                    "Tell me about a successful campaign you led",
                    "How do you handle budget constraints in marketing?",
                    "Describe your experience with digital marketing tools"
                ]
            }
        }
        
        # Normalize job title for lookup
        normalized_title = job_title.lower().replace(' ', '_').replace('-', '_')
        
        return suggestions.get(normalized_title, {
            'general': [
                "Tell me about yourself and your career journey",
                "Why are you interested in this position?",
                "What are your greatest strengths and weaknesses?",
                "Where do you see yourself in 5 years?",
                "Why are you leaving your current position?"
            ]
        })

def create_interview_session(candidate_info: Dict, job_description: str, 
                           interviewer_info: Dict) -> Dict:
    """Create a new interview session with metadata"""
    
    session_id = f"INT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{candidate_info.get('name', 'Unknown').replace(' ', '_')}"
    
    session = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'status': 'scheduled',
        'candidate_info': candidate_info,
        'job_description': job_description,
        'interviewer_info': interviewer_info,
        'questions': [],
        'responses': {},
        'evaluation': {},
        'notes': '',
        'duration': None,
        'completed_at': None
    }
    
    return session

def save_interview_session(session: Dict, filename: str = None) -> str:
    """Save interview session to file"""
    
    if filename is None:
        filename = f"interview_session_{session['session_id']}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        return filename
    except Exception as e:
        raise Exception(f"Failed to save interview session: {str(e)}")

def load_interview_session(filename: str) -> Dict:
    """Load interview session from file"""
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Failed to load interview session: {str(e)}") 