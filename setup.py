#!/usr/bin/env python3
"""
Setup script for AI Hiring Platform
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        'uploads',
        'logs',
        'rag/vector_store',
        'static/uploads',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment():
    """Setup environment file"""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            shutil.copy('env.example', '.env')
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your API keys")
        else:
            print("❌ env.example not found")
    else:
        print("✅ .env file already exists")

def install_dependencies():
    """Install Python dependencies"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    return True

def initialize_database():
    """Initialize the database"""
    try:
        from database import init_db
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False
    return True

def setup_rag_system():
    """Setup RAG system"""
    try:
        # Check if vector store initialization script exists
        if os.path.exists('scripts/init_vector_db.py'):
            subprocess.check_call([sys.executable, 'scripts/init_vector_db.py'])
            print("✅ RAG system initialized successfully")
        else:
            print("⚠️  RAG initialization script not found, skipping...")
    except Exception as e:
        print(f"⚠️  RAG system setup failed: {e}")

def main():
    """Main setup function"""
    print("🚀 Setting up AI Hiring Platform...")
    print("=" * 50)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Setup environment
    print("\n🔧 Setting up environment...")
    setup_environment()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return
    
    # Initialize database
    print("\n🗄️  Initializing database...")
    if not initialize_database():
        print("❌ Setup failed at database initialization")
        return
    
    # Setup RAG system
    print("\n🤖 Setting up RAG system...")
    setup_rag_system()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python flask_app.py")
    print("3. Visit: http://localhost:5000")
    print("\n💡 For help, check README.md or CONTRIBUTING.md")

if __name__ == "__main__":
    main() 