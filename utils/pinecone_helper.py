import sys
from pinecone import Pinecone  # This is the correct import
from typing import List, Dict
import os

class PineconeHelper:
    def __init__(self):
        try:
            self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            self.index_name = "credit-card-rag"
            
            # Check if index exists, if not create it
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            if self.index_name not in existing_indexes:
                # Create index with 1536 dimensions (OpenAI's embedding size)
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,
                    metric="cosine"
                )
                print(f"Created new index: {self.index_name}")
            
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            raise

    def upsert_embeddings(self, embeddings: List[List[float]], metadata: List[Dict]):
        """Upsert embeddings with metadata to Pinecone"""
        vectors = [
            (str(i), embedding, meta)
            for i, (embedding, meta) in enumerate(zip(embeddings, metadata))
        ]
        self.index.upsert(vectors=vectors)

    def query_index(self, query_embedding: List[float], top_k: int = 5):
        """Query the index with the given embedding"""
        return self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        ) 