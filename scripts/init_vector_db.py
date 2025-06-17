import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.document_processor import load_job_descriptions, process_job_descriptions, chunk_documents
from rag.embeddings import get_embedding_function
from rag.vector_store import get_or_create_vector_store, delete_vector_store

def init_vector_database(data_path, recreate=False):
    """Initialize vector database with job descriptions"""
    print("Initializing vector database...")
    
    # Get embedding function
    embedding_function = get_embedding_function()
    print("✓ Embedding function loaded")
    
    # Delete existing index if recreate is True
    if recreate:
        print("Deleting existing vector store...")
        delete_vector_store()
        print("✓ Existing vector store deleted")
    
    # Get or create vector store
    vector_store = get_or_create_vector_store(embedding_function)
    print("✓ Vector store created/loaded")
    
    # Load and process job descriptions
    print(f"Loading job descriptions from {data_path}...")
    df = load_job_descriptions(data_path)
    print(f"✓ Loaded {len(df)} job descriptions")
    
    # Process documents
    print("Processing job descriptions...")
    documents = process_job_descriptions(df)
    print(f"✓ Processed {len(documents)} documents")
    
    # Chunk documents
    print("Chunking documents...")
    chunked_documents = chunk_documents(documents)
    print(f"✓ Created {len(chunked_documents)} document chunks")
    
    # Add documents to vector store in batches
    batch_size = 100
    print(f"Adding documents to vector store in batches of {batch_size}...")
    
    for i in range(0, len(chunked_documents), batch_size):
        batch = chunked_documents[i:i+batch_size]
        vector_store.add_documents(batch)
        print(f"✓ Added batch {i//batch_size + 1}/{(len(chunked_documents)-1)//batch_size + 1}")
    
    print(f"✓ Successfully added {len(chunked_documents)} document chunks to vector store")
    return vector_store

if __name__ == "__main__":
    # Use the actual downloaded dataset file - resolve absolute path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "..", "data", "job_title_des.csv")
    data_path = os.path.abspath(data_path)
    
    print("Starting vector database initialization...")
    print(f"Data path: {data_path}")
    
    try:
        vector_store = init_vector_database(data_path, recreate=False)
        print("🎉 Vector database initialization completed successfully!")
    except Exception as e:
        print(f"❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()