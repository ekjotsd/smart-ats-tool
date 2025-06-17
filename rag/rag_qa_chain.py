import warnings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Suppress LangChain deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")

def create_rag_chain(llm, retriever):
    """Create RAG QA chain"""
    template = """You are an expert career advisor and job search assistant with extensive knowledge about:
- Resume writing and optimization
- Job search strategies and best practices  
- Interview preparation and techniques
- Career development and advancement
- Salary negotiation
- Industry trends and requirements
- ATS (Applicant Tracking System) optimization

Use the following context to provide comprehensive, actionable advice to help users with their career and job application questions.

Instructions:
- Provide specific, practical advice based on the context
- Use bullet points and numbered lists when appropriate for clarity
- Include relevant examples when helpful
- If the question is outside your expertise area, acknowledge limitations
- Be encouraging and professional in your responses
- Focus on actionable steps the user can take

Context: {context}

Question: {question}

Helpful Answer:"""
    
    QA_PROMPT = PromptTemplate.from_template(template)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_PROMPT}
    )
    
    return qa_chain

def create_conversation_chain(llm, retriever):
    """Create a conversation chain for multi-turn dialogue"""
    from langchain.chains import ConversationalRetrievalChain
    import warnings
    
    # Suppress deprecation warnings for memory
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        from langchain.memory import ConversationBufferMemory
        
        # Use the memory with warning suppression
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    
    template = """You are an expert career advisor continuing a conversation about job search and career development.

Previous conversation context and current relevant information:
{context}

Chat History: {chat_history}

Current Question: {question}

Please provide a helpful, specific response that builds on our previous conversation while incorporating relevant information from the knowledge base. Use bullet points when appropriate for clarity.

Answer:"""

    QA_PROMPT = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=template
    )

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT}
    )
    
    return conversation_chain