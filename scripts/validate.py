#!/usr/bin/env python3
"""
Component validation for Smart ATS RAG system
Tests individual components to ensure they work correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def validate_environment():
    """Validate environment setup"""
    print("🔍 Validating Environment Setup")
    print("-" * 35)
    
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API access",
        "PINECONE_API_KEY": "Pinecone vector database",
        "GROQ_API_KEY": "Groq LLM provider (optional)"
    }
    
    all_good = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var}: {masked_value} ({description})")
        else:
            if var == "GROQ_API_KEY":
                print(f"⚠️  {var}: Not set ({description})")
            else:
                print(f"❌ {var}: Missing ({description})")
                all_good = False
    
    return all_good

def validate_data_files():
    """Validate required data files"""
    print("\n📁 Validating Data Files")
    print("-" * 25)
    
    # Resolve absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(script_dir, "..", "data", "job_title_des.csv")
    data_file_path = os.path.abspath(data_file_path)
    download_script_path = os.path.join(script_dir, "download_dataset.py")
    download_script_path = os.path.abspath(download_script_path)
    
    files_to_check = [
        (data_file_path, "Job descriptions dataset"),
        (download_script_path, "Dataset download script")
    ]
    
    all_good = True
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path}: {size:,} bytes ({description})")
        else:
            print(f"❌ {file_path}: Missing ({description})")
            all_good = False
    
    return all_good

def validate_core_files():
    """Validate core application files"""
    print("\n📁 Validating Core Files")
    print("-" * 40)
    
    core_files = [
        ("flask_app.py", "Main Flask application"),
        ("database.py", "Database configuration"),
        ("utils.py", "Utility functions"),
        ("pdf_generator.py", "PDF generation"),
        ("interview_assistant.py", "Interview assistant"),
        ("mcq_utils.py", "MCQ utilities")
    ]
    
    missing_files = []
    for file_path, description in core_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} - {description}")
        else:
            print(f"✗ {file_path} - {description} (MISSING)")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def generate_setup_instructions():
    """Generate setup instructions based on validation results"""
    print("\n📋 Setup Instructions")
    print("-" * 20)
    
    print("1. Environment Variables:")
    print("   Copy .env.example to .env and add your API keys")
    
    print("\n2. Download Dataset:")
    print("   cd data && python download_dataset.py")
    
    print("\n3. Install Dependencies:")
    print("   pipenv install")
    
    print("\n4. Initialize Vector Database:")
    print("   python setup.py")
    
    print("\n5. Run Application:")
    print("   streamlit run app.py")

def main():
    """Main validation function"""
    print("🔍 Smart ATS Flask Application - Validation")
    print("=" * 50)
    
    validations = [
        validate_environment,
        validate_dependencies,
        validate_core_files,
        validate_data_files,
        validate_templates
    ]
    
    all_passed = True
    for validation in validations:
        if not validation():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All validations passed!")
        print("🚀 You can run the application:")
        print("   py flask_app.py")
    else:
        print("❌ Some validations failed!")
        print("Please fix the issues above before running the application.")
    
    return all_passed

if __name__ == "__main__":
    main()
