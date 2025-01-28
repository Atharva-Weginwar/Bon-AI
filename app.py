import streamlit as st
import os
from dotenv import load_dotenv
from utils.pinecone_helper import PineconeHelper
from utils.s3_helper import S3Helper
from utils.llm_helper import LLMHelper
from agents.orchestrator import Orchestrator
from utils.document_processor import DocumentProcessor
from agents.rag_agent import RAGAgent
from agents.image_agent import ImageAgent
from agents.fact_checker import FactChecker

# Load environment variables
load_dotenv()

def main():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("Credit Card RAG Assistant")
    
    # Initialize helpers
    llm = LLMHelper()
    pinecone_helper = PineconeHelper()
    s3_helper = S3Helper()
    
    # Initialize agents with correct parameters
    rag_agent = RAGAgent(llm=llm, pinecone_helper=pinecone_helper)
    image_agent = ImageAgent(s3_helper)
    fact_checker = FactChecker(llm)
    doc_processor = DocumentProcessor(pinecone_helper)
    
    orchestrator = Orchestrator(rag_agent=rag_agent, 
                              image_agent=image_agent, 
                              fact_checker=fact_checker)
    
    # Add sidebar collapse button
    with st.sidebar:
        st.button("≡", key="collapse_button", help="Collapse/Expand Sidebar")
        st.header("Document Upload")
        uploaded_file = st.file_uploader("Upload a document", type=['pdf', 'docx', 'txt'])
        
        if uploaded_file:
            if st.button("Process Document"):
                with st.spinner("Processing document..."):
                    success = doc_processor.process_document(uploaded_file)
                    if success:
                        st.success("Document processed successfully!")
                    else:
                        st.error("Error processing document")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "image_url" in message and message["image_url"]:
                st.image(message["image_url"])

    # Chat input at the bottom
    if user_input := st.chat_input("What would you like to know about credit cards?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get response from orchestrator with loading spinner
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = orchestrator.process_query(user_input)
                    st.markdown(response["answer"], unsafe_allow_html=True)
                    if response.get("image_url"):
                        st.image(response["image_url"])
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "image_url": response.get("image_url")
                    })
                except Exception as e:
                    error_msg = f"An error occurred: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "I apologize, but I encountered an error processing your request."
                    })

if __name__ == "__main__":
    # Set page config for wider layout and collapsible sidebar
    st.set_page_config(
        page_title="Credit Card RAG Assistant",
        layout="wide",
        initial_sidebar_state="collapsed"  # Start with collapsed sidebar
    )
    
    # Add custom CSS for sidebar toggle
    st.markdown("""
        <style>
        .stButton button {
            background-color: transparent;
            border: none;
            padding: 0;
            font-size: 24px;
        }
        /* Center the title */
        .title-center {
            text-align: center;
            padding: 1rem;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Update title with centered class
    st.markdown("<h1 class='title-center'>Bon AI</h1>", unsafe_allow_html=True)
    
    main() 