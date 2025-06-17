#!/usr/bin/env python3
"""
Setup script for Smart ATS RAG FAQ Assistant
This script initializes the vector database with job descriptions and career guidance
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_requirements():
    """Check if all required environment variables and files are present"""
    print("🔍 Checking requirements...")
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please set these in your .env file")
        return False
    
    # Check data file
    data_file = "data/job_title_des.csv"
    if not os.path.exists(data_file):
        print(f"❌ Dataset file not found: {data_file}")
        print("💡 Run the download script: cd data && python download_dataset.py")
        return False
    
    print("✅ All requirements met")
    return True

def setup_vector_database():
    """Initialize the vector database with job descriptions and career guidance"""
    print("\n🚀 Setting up vector database...")
    
    try:
        from rag.init_vector_db import init_vector_database
        
        # Initialize with the downloaded dataset
        data_path = "data/job_title_des.csv"
        print(f"📁 Using dataset: {data_path}")
        
        # Initialize vector database (recreate if exists)
        vector_store = init_vector_database(data_path, recreate=True)
        
        print("✅ Vector database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up vector database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main setup function"""
    print("🤖 Smart ATS RAG FAQ Assistant - Setup")
    print("=" * 45)
    print()
    
    if not check_requirements():
        print("\n❌ Setup failed. Please fix the issues above.")
        return
    
    if setup_vector_database():
        print("\n🎉 Setup completed successfully!")
        print("\n🚀 You can now run the application:")
        print("   py flask_app.py")
        print("\n💡 Or test the RAG system:")
        print("   python test_rag.py")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()
