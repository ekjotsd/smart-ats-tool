#!/usr/bin/env python3
"""
Complete setup script for Smart ATS RAG FAQ Assistant
This script performs initial setup including vector database initialization
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_environment():
    """Check if environment variables are set"""
    print("🔍 Checking Environment Variables...")
    print("=" * 50)
    
    required_vars = [
        "OPENAI_API_KEY",
        "GROQ_API_KEY", 
        "PINECONE_API_KEY",
        "PINECONE_CLOUD",
        "PINECONE_REGION",
        "KAGGLE_USERNAME",
        "KAGGLE_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * (len(value) - 4) + value[-4:]}")
        else:
            print(f"✗ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with the required API keys.")
        return False
    
    print("✅ All environment variables are set!")
    return True

def check_dependencies():
    """Check if dependencies are installed"""
    print("\n📦 Checking Dependencies...")
    print("=" * 50)
    
    try:
        import langchain
        import openai
        import groq
        import pandas
        import numpy
        print("✅ All required packages are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pipenv install")
        return False

def download_dataset():
    """Download the Kaggle dataset if not present"""
    print("\n📊 Checking Dataset...")
    print("=" * 50)
    
    # Resolve absolute path for data file
    script_dir = Path(__file__).parent
    data_file = script_dir.parent / "data" / "job_title_des.csv"
    
    if data_file.exists():
        print(f"✅ Dataset already exists: {data_file}")
        return True
    
    print("📥 Downloading dataset from Kaggle...")
    try:
        # Run the download script
        result = subprocess.run([
            sys.executable, "download_dataset.py"
        ], capture_output=True, text=True, check=True, cwd=os.path.dirname(__file__))
        
        print(result.stdout)
        
        if data_file.exists():
            print("✅ Dataset downloaded successfully!")
            return True
        else:
            print("❌ Dataset download failed!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading dataset: {e}")
        print("Please check your Kaggle credentials.")
        return False

def initialize_vector_database():
    """Initialize the vector database"""
    print("\n🗄️ Initializing Vector Database...")
    print("=" * 50)
    
    try:
        from rag.vector_store import init_pinecone, get_or_create_vector_store
        from rag.embeddings import get_embedding_function
        
        # Test Pinecone connection
        pc = init_pinecone()
        index_name = os.getenv("PINECONE_INDEX_NAME", "smart-ats-faq")
        
        # Check if index exists and has data
        existing_indexes = [index.name for index in pc.list_indexes()]
        
        if index_name in existing_indexes:
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            
            if total_vectors > 0:
                print(f"✅ Vector database already initialized with {total_vectors} vectors")
                return True
            else:
                print("Vector database exists but is empty. Initializing...")
        else:
            print("Creating new vector database...")
        
        # Initialize the vector database
        from init_vector_db import init_vector_database
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(script_dir, "..", "data", "job_title_des.csv")
        data_path = os.path.abspath(data_path)
        
        if not os.path.exists(data_path):
            print(f"❌ Dataset not found: {data_path}")
            return False
        
        print("🔄 This may take several minutes...")
        vector_store = init_vector_database(data_path, recreate=False)
        
        print("✅ Vector database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing vector database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_tests():
    """Run basic tests to verify setup"""
    print("\n🧪 Running Basic Tests...")
    print("=" * 50)
    
    try:
        # Run the test runner
        result = subprocess.run([
            sys.executable, "../tests/run_tests.py"
        ], capture_output=True, text=True, check=False)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        if success:
            print("✅ All tests passed!")
        else:
            print("⚠️ Some tests failed, but setup may still be functional.")
        
        return success
        
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Smart ATS RAG FAQ Assistant - Complete Setup")
    print("=" * 60)
    
    steps = [
        ("Environment Variables", check_environment),
        ("Dependencies", check_dependencies),
        ("Dataset Download", download_dataset),
        ("Vector Database", initialize_vector_database),
        ("System Tests", run_tests)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at step: {step_name}")
            print("Please resolve the issues above and run setup again.")
            return False
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print("\n🚀 You can now run the application:")
    print("   py flask_app.py")
    print("\n📚 Or run tests anytime:")
    print("   python ../tests/run_tests.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
