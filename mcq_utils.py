# Import required libraries
import os
from typing import List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel, Field, validator
import json

# Load environment variables from .env file
load_dotenv()

# Define data model for Multiple Choice Questions using Pydantic
class MCQQuestion(BaseModel):
    # Define the structure of an MCQ with field descriptions
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of 5 possible answers")
    # correct_answer: str = Field(description="The correct answer from the options")

    # Custom validator to clean question text
    # Handles cases where question might be a dictionary or other format
    @validator('question', pre=True)
    def clean_question(cls, v):
        if isinstance(v, dict):
            return v.get('description', str(v))
        return str(v)

def get_llm_for_model(model):
    """Get the appropriate LLM client based on the model type"""
    # OpenAI models
    openai_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    if model in openai_models:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(f"OPENAI_API_KEY not found in environment variables for model {model}")
        return ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=0.9
        )
    else:
        # Groq models (default)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(f"GROQ_API_KEY not found in environment variables for model {model}")
        return ChatGroq(
            api_key=api_key, 
            model=model,
            temperature=0.9
        )

class QuestionGenerator:
    def __init__(self, model):
        """
        Initialize question generator with appropriate API client
        Supports both Groq and OpenAI models
        """
        self.model = model
        self.llm = get_llm_for_model(model)

        # Create memory to maintain chat history
        self.memory = ConversationBufferMemory(return_messages=True)

        self.Personality_Traits = ['Conscientiousness', 'Extraversion', 'Agreeableness', 'Emotional Stability', 'Openness to Experience']
        self.Workplace_Behaviors = ['Teamwork', 'Problem-solving', 'Adaptability', 'Initiative', 'Communication', 'Time Management']

    def generate_mcq(self, topic: str) -> MCQQuestion:
        """
        Generate Multiple Choice Question with robust error handling
        Includes:
        - Output parsing using Pydantic
        - Structured prompt template
        - Multiple retry attempts on failure
        - Validation of generated questions
        """
        # Set up Pydantic parser for type checking and validation
        mcq_parser = PydanticOutputParser(pydantic_object=MCQQuestion)

        if topic == 'Personality Traits':
            # Define the prompt template with specific format requirements
            topic = ', '.join(self.Personality_Traits)
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """
                    Generate a question designed to assess one of the following topics in a professional context: 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Emotional Stability', 'Openness to Experience'.
                    Each question should be answered using one of the following options:
                    "Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree".
                 
                    Review the previous conversation history and ensure that the generated question is not a duplicate or close paraphrase of any previously generated question.

                    You must return a valid JSON object with the following structure:
                    {{
                    "question": "A clear, specific question",
                    "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
                    }}

                    Return ONLY the JSON. Do not add explanations, formatting, or markdown. """),
                    MessagesPlaceholder(variable_name="history"),  # ✅ This is how memory is injected
                    ("human", "{input}")  # Insert user input dynamically
            ])
        else:
            topic = ', '.join(self.Workplace_Behaviors)
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """
                Generate a behavioral question that assesses a candidate's general tendencies towards one of the following topics in the workplace: 'Teamwork', 'Problem-solving', 'Adaptability', 'Initiative', 'Communication', 'Time Management'.
                Each question should be answered using one of the following options:
                "Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree".

                Review the previous conversation history and ensure that the generated question is not a duplicate or close paraphrase of any previously generated question.

                You must return a valid JSON object with the following structure:
                {{
                "question": "A clear, specific question",
                "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
                }}

                Return ONLY the JSON. Do not add explanations, formatting, or markdown.
            """),
            MessagesPlaceholder(variable_name="history"),  # Inject memory here
            ("human", "{input}")  # Insert user input dynamically
        ])
        # Generate response using LLM
        # Set up the chain using the appropriate model, memory, and custom prompt template
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt_template,
            memory=self.memory,
            verbose=False
        )
        # Implement retry logic with maximum attempts
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Generate response using LLM
                response = chain.run(input= " ")
                parsed_response = mcq_parser.parse(response)
                
                # Validate the generated question meets requirements
                if not parsed_response.question or len(parsed_response.options) != 5:
                    raise ValueError("Invalid question format")
                
                return parsed_response
            except Exception as e:
                # On final attempt, raise error; otherwise continue trying
                if attempt == max_attempts - 1:
                    raise RuntimeError(f"Failed to generate valid MCQ after {max_attempts} attempts: {str(e)}")
                continue

def get_response(model, result):
    """Get AI analysis response using the appropriate model"""
    llm = get_llm_for_model(model)

    question = result['question']
    user_response = result['user_answer']

    prompt_template = ChatPromptTemplate.from_template("""
You are an intelligent psychometric analysis agent.

Given a psychometric question and a user's Likert-scale response, do the following:

1. Identify the most relevant psychological dimension the question assesses.
2. Evaluate the Likert-scale response by mapping it to a normalized score (range: 0.0 to 1.0).
3. Assign a label based on the score:
   - "Low" for 0.0–0.33,
   - "Moderate" for >0.33–0.66,
   - "High" for >0.66–1.0.
4. Write a brief reasoning describing what the user's response reveals about their behavior or personality related to the inferred dimension.

Use only the following list of dimensions:

Personality Traits:
- Conscientiousness
- Extraversion
- Agreeableness
- Emotional Stability
- Openness to Experience

Workplace Behaviors:
- Teamwork
- Problem-solving
- Adaptability
- Initiative
- Communication
- Time Management

Input:
Question: {question}  
Likert Response: {user_response} (e.g., "Strongly Agree", "Disagree", etc.)

⛔ Important:
- You must return **only** a valid JSON object.
- Do **not** include any explanation, headers, bullet points, or markdown.
- The JSON must be the only thing in your output.

Output format:
{{
  "inferred_dimension": "<inferred dimension from list>",
  "original_response": "{user_response}",
  "normalized_score": float between 0.0 and 1.0,
  "label": "Low" | "Moderate" | "High",
  "reasoning": "What the user's response implies about their behavior or personality in relation to the inferred dimension."
}}

Example Input:
Question: "I often take the lead when a new task is assigned to my team."  
Likert Response: "Strongly Agree"

Expected Output:
{{
  "inferred_dimension": "Initiative",
  "original_response": "Strongly Agree",
  "normalized_score": 1.0,
  "label": "High",
  "reasoning": "The user consistently takes charge in team settings, indicating a strong sense of initiative and leadership."
}}
""")

    # Generate response using LLM
    chain = LLMChain(
        llm=llm,
        prompt=prompt_template,
        verbose=False
    )

    # Implement retry logic with maximum attempts
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = chain.run({
                "question": question,
                "user_response": user_response
            }).strip()
            
            print(f"Raw LLM response (attempt {attempt + 1}): {response}")
            
            # Try to clean up the response if it has extra text
            if '{' in response and '}' in response:
                # Extract JSON part
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                json_part = response[start_idx:end_idx]
                print(f"Extracted JSON part: {json_part}")
                response_dict = json.loads(json_part)
            else:
                response_dict = json.loads(response)
            
            # Validate the response has required fields
            required_fields = ['inferred_dimension', 'original_response', 'normalized_score', 'label', 'reasoning']
            if all(field in response_dict for field in required_fields):
                return response_dict
            else:
                missing_fields = [field for field in required_fields if field not in response_dict]
                print(f"Missing fields in response: {missing_fields}")
                raise ValueError(f"Response missing required fields: {missing_fields}")
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed (attempt {attempt + 1}): {e}")
            print(f"Raw LLM output: {response}")
            if attempt == max_attempts - 1:
                # Return a fallback response based on the user's answer
                return create_fallback_response(question, user_response)
            continue
        except Exception as e:
            print(f"Error in get_response (attempt {attempt + 1}): {e}")
            if attempt == max_attempts - 1:
                return create_fallback_response(question, user_response)
            continue

def create_fallback_response(question, user_response):
    """Create a fallback response when AI analysis fails"""
    # Simple heuristic-based analysis
    question_lower = question.lower()
    
    # Determine dimension based on keywords in question
    if any(word in question_lower for word in ['team', 'collaborate', 'group', 'together']):
        dimension = 'Teamwork'
    elif any(word in question_lower for word in ['lead', 'initiative', 'take charge', 'responsibility']):
        dimension = 'Initiative'
    elif any(word in question_lower for word in ['communicate', 'speak', 'express', 'listen']):
        dimension = 'Communication'
    elif any(word in question_lower for word in ['problem', 'solve', 'challenge', 'solution']):
        dimension = 'Problem-solving'
    elif any(word in question_lower for word in ['adapt', 'change', 'flexible', 'adjust']):
        dimension = 'Adaptability'
    elif any(word in question_lower for word in ['time', 'deadline', 'schedule', 'organize']):
        dimension = 'Time Management'
    elif any(word in question_lower for word in ['detail', 'careful', 'thorough', 'precise']):
        dimension = 'Conscientiousness'
    elif any(word in question_lower for word in ['social', 'outgoing', 'people', 'interact']):
        dimension = 'Extraversion'
    elif any(word in question_lower for word in ['help', 'kind', 'considerate', 'cooperative']):
        dimension = 'Agreeableness'
    elif any(word in question_lower for word in ['calm', 'stress', 'pressure', 'emotional']):
        dimension = 'Emotional Stability'
    elif any(word in question_lower for word in ['creative', 'new', 'innovative', 'ideas']):
        dimension = 'Openness to Experience'
    else:
        dimension = 'Communication'  # Default fallback
    
    # Determine score based on response
    score_map = {
        'Strongly Agree': 1.0,
        'Agree': 0.75,
        'Neutral': 0.5,
        'Disagree': 0.25,
        'Strongly Disagree': 0.0
    }
    
    score = score_map.get(user_response, 0.5)
    
    # Determine label
    if score <= 0.33:
        label = 'Low'
    elif score <= 0.66:
        label = 'Moderate'
    else:
        label = 'High'
    
    return {
        'inferred_dimension': dimension,
        'original_response': user_response,
        'normalized_score': score,
        'label': label,
        'reasoning': f'Based on the response "{user_response}" to a question about {dimension.lower()}, this indicates a {label.lower()} level in this dimension.'
    }
            