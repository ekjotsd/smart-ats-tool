import os
import time
import pinecone
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()

def init_pinecone():
    """Initialize Pinecone client"""
    pc = pinecone.Pinecone(
        api_key=os.getenv("PINECONE_API_KEY")
    )
    return pc

def get_or_create_vector_store(embedding_function, index_name=None):
    """Get or create a Pinecone vector store"""
    pc = init_pinecone()
    
    # Use environment variable or default
    if index_name is None:
        index_name = os.getenv("PINECONE_INDEX_NAME", "smart-ats-faq")
    
    # Check if index exists
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        # Get cloud and region from environment
        cloud = os.getenv("PINECONE_CLOUD", "aws")
        region = os.getenv("PINECONE_REGION", "us-east-1")
        
        print(f"Creating index '{index_name}' with cloud={cloud}, region={region}")
        
        # Create the index with serverless spec
        pc.create_index(
            name=index_name,
            dimension=1536,  # Default for OpenAI text-embedding-ada-002
            metric="cosine",
            spec=pinecone.ServerlessSpec(
                cloud=cloud,
                region=region
            )
        )
        
        print(f"Index '{index_name}' created. Waiting for it to be ready...")
        # Wait for index to be ready
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
        print(f"Index '{index_name}' is ready!")
    # Remove the "already exists" message to reduce noise
    
    print(f"Using existing index '{index_name}'")
    # Get the vector store
    vector_store = PineconeVectorStore(
        index_name=index_name,
        embedding=embedding_function,
        text_key="text"
    )
    
    return vector_store

def delete_vector_store(index_name=None):
    """Delete the vector store index"""
    pc = init_pinecone()
    
    # Use environment variable or default
    if index_name is None:
        index_name = os.getenv("PINECONE_INDEX_NAME", "smart-ats-faq")
    
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if index_name in existing_indexes:
        print(f"Deleting index '{index_name}'...")
        pc.delete_index(index_name)
        print(f"Index '{index_name}' deleted successfully")
        return True
    else:
        print(f"Index '{index_name}' does not exist")
        return False

def get_index_stats(index_name=None):
    """Get statistics about the index"""
    pc = init_pinecone()
    
    # Use environment variable or default
    if index_name is None:
        index_name = os.getenv("PINECONE_INDEX_NAME", "smart-ats-faq")
    
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if index_name in existing_indexes:
        index = pc.Index(index_name)
        return index.describe_index_stats()
    else:
        print(f"Index '{index_name}' does not exist")
        return None
