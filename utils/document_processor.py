import PyPDF2
import docx2txt
from typing import List, Dict
import numpy as np
import openai
import os
from time import sleep

class DocumentProcessor:
    def __init__(self, pinecone_helper):
        self.pinecone = pinecone_helper
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.CHUNK_SIZE = 500  # Reduced chunk size
        self.BATCH_SIZE = 100  # Number of vectors to upsert at once

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI's text-ada-002 using new API"""
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings

    def process_document(self, file) -> bool:
        """Process uploaded document and update vector database in batches"""
        try:
            # Extract text based on file type
            text = self.extract_text(file)
            
            # Split text into chunks
            chunks = self.chunk_text(text)
            
            # Process chunks in batches
            for i in range(0, len(chunks), self.BATCH_SIZE):
                batch_chunks = chunks[i:i + self.BATCH_SIZE]
                
                # Generate embeddings for batch
                embeddings = self.get_embeddings(batch_chunks)
                
                # Create metadata for batch
                metadata = [{"text": chunk} for chunk in batch_chunks]
                
                # Upload batch to Pinecone
                self.pinecone.upsert_embeddings(embeddings, metadata)
                
                # Sleep briefly to avoid rate limits
                sleep(0.5)
            
            return True
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return False

    def extract_text(self, file) -> str:
        """Extract text from different file formats"""
        file_type = file.name.split('.')[-1].lower()
        
        if file_type == 'pdf':
            return self.extract_from_pdf(file)
        elif file_type == 'docx':
            return self.extract_from_docx(file)
        elif file_type == 'txt':
            return file.getvalue().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def extract_from_pdf(self, file) -> str:
        """Extract text from PDF"""
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    def extract_from_docx(self, file) -> str:
        """Extract text from DOCX"""
        return docx2txt.process(file)

    def chunk_text(self, text: str) -> List[str]:
        """Split text into smaller chunks"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_size += len(word) + 1
            if current_size > self.CHUNK_SIZE:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks 