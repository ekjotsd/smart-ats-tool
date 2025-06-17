from langchain_core.prompts import PromptTemplate

try:
    from langchain.retrievers import EnsembleRetriever
    from langchain.retrievers.multi_query import MultiQueryRetriever
    ADVANCED_RETRIEVERS_AVAILABLE = True
except ImportError:
    ADVANCED_RETRIEVERS_AVAILABLE = False
    print("Warning: Advanced retrievers not available. Install langchain-community for full functionality.")

def get_retriever(vector_store, search_kwargs=None, retriever_type="similarity"):
    """Get retriever from vector store with various search strategies"""
    if search_kwargs is None:
        search_kwargs = {"k": 5}
        
    if retriever_type == "similarity":
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs
        )
    elif retriever_type == "mmr":
        # Maximum Marginal Relevance retrieval for diverse results
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={**search_kwargs, "fetch_k": 20, "lambda_mult": 0.5}
        )
    elif retriever_type == "similarity_score_threshold":
        # Similarity with score threshold
        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={**search_kwargs, "score_threshold": 0.5}
        )
    else:
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs
        )
    
    return retriever

def get_multi_query_retriever(vector_store, llm, search_kwargs=None):
    """Get a multi-query retriever that generates multiple queries for better results"""
    if not ADVANCED_RETRIEVERS_AVAILABLE:
        print("Warning: Multi-query retriever not available. Using standard retriever.")
        return get_retriever(vector_store, search_kwargs)
    
    base_retriever = get_retriever(vector_store, search_kwargs)
    
    # Custom prompt for generating multiple queries
    prompt_template = """You are an AI language model assistant. Your task is to generate five 
    different versions of the given user question to retrieve relevant documents from a vector 
    database. By generating multiple perspectives on the user question, your goal is to help 
    the user overcome some of the limitations of the distance-based similarity search. 
    Provide these alternative questions separated by newlines.

    Original question: {question}"""
    
    prompt = PromptTemplate(
        input_variables=["question"],
        template=prompt_template
    )
    
    retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm,
        prompt=prompt
    )
    
    return retriever

def get_ensemble_retriever(vector_store, search_kwargs=None):
    """Get an ensemble retriever that combines multiple search strategies"""
    if not ADVANCED_RETRIEVERS_AVAILABLE:
        print("Warning: Ensemble retriever not available. Using standard retriever.")
        return get_retriever(vector_store, search_kwargs)
    
    if search_kwargs is None:
        search_kwargs = {"k": 3}  # Reduced k for each retriever since we're combining
    
    # Create multiple retrievers with different strategies
    similarity_retriever = get_retriever(vector_store, search_kwargs, "similarity")
    mmr_retriever = get_retriever(vector_store, search_kwargs, "mmr")
    
    # Combine retrievers with weights
    ensemble_retriever = EnsembleRetriever(
        retrievers=[similarity_retriever, mmr_retriever],
        weights=[0.6, 0.4]  # Favor similarity but include diversity
    )
    
    return ensemble_retriever

def get_contextual_retriever(vector_store, query_type="general", search_kwargs=None):
    """Get a retriever optimized for different query types"""
    if search_kwargs is None:
        search_kwargs = {"k": 5}
    
    if query_type == "resume":
        # For resume-related queries, prefer diverse results
        return get_retriever(vector_store, search_kwargs, "mmr")
    elif query_type == "interview":
        # For interview queries, prefer high-relevance results
        return get_retriever(vector_store, search_kwargs, "similarity_score_threshold")
    elif query_type == "salary":
        # For salary queries, prefer comprehensive results
        search_kwargs["k"] = 8
        return get_retriever(vector_store, search_kwargs, "similarity")
    else:
        # Default to similarity search
        return get_retriever(vector_store, search_kwargs, "similarity")