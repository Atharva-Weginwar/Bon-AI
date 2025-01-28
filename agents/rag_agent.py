from utils.pinecone_helper import PineconeHelper
from utils.llm_helper import LLMHelper
import numpy as np
import openai
import os
from typing import List

class RAGAgent:
    def __init__(self, llm: LLMHelper, pinecone_helper: PineconeHelper):
        self.llm = llm
        self.pinecone_helper = pinecone_helper
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI's text-ada-002 using new API"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None

    def get_context(self, query: str) -> str:
        """Get relevant context from vector database"""
        try:
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return ""
            
            results = self.pinecone_helper.query_index(query_embedding)
            print(f"Query results: {results}")  # Debug print
            
            # Extract and format relevant context
            context = ""
            if hasattr(results, 'matches'):
                for match in results.matches:
                    if match.metadata and 'text' in match.metadata:
                        context += f"{match.metadata['text']}\n"
            
            print(f"Retrieved context: {context}")  # Debug print
            return context
        except Exception as e:
            print(f"Error getting context: {e}")
            return ""

    def get_response(self, query: str) -> str:
        """Get response using RAG"""
        try:
            context = self.get_context(query)
            if not context:
                return "I apologize, but I couldn't find relevant information to answer your question."
            
            response = self.llm.get_completion(query, context)
            return response
        except Exception as e:
            print(f"Error in RAG response: {e}")
            return "I apologize, but I encountered an error while processing your request." 