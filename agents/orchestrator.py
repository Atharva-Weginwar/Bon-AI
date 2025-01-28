from typing import Dict, List, Optional
from utils.llm_helper import LLMHelper
from utils.pinecone_helper import PineconeHelper
from utils.s3_helper import S3Helper
from .rag_agent import RAGAgent
from .web_agent import WebAgent
from .image_agent import ImageAgent
from .fact_checker import FactChecker

class Orchestrator:
    def __init__(self, rag_agent: RAGAgent, image_agent: ImageAgent, fact_checker: FactChecker):
        self.rag_agent = rag_agent
        self.image_agent = image_agent
        self.fact_checker = fact_checker
        self.web_agent = WebAgent(self.rag_agent.llm)

    def process_query(self, query: str) -> dict:
        try:
            # List of keywords that indicate a card recommendation request
            recommendation_keywords = [
                "recommend", "suggest", "best card", "which card", 
                "looking for", "need a card", "get a card", "apply",
                "card for", "best credit card"
            ]
            
            # Check if query is asking for a recommendation
            is_recommendation_query = any(keyword in query.lower() for keyword in recommendation_keywords)
            
            if is_recommendation_query:
                # Get recommendations with structured format
                recommendations = self.web_agent.get_card_recommendations(query)
                formatted_recommendations = self.web_agent.format_response(
                    recommendations, 
                    is_recommendation=True
                )
                
                image_url = None
                if recommendations:
                    first_card = list(recommendations.keys())[0]
                    image_url = self.image_agent.get_card_image(first_card)

                return {
                    "answer": formatted_recommendations,
                    "image_url": image_url
                }
            else:
                # Updated system prompt for more detailed factual answers
                messages = [
                    {
                        "role": "system", 
                        "content": """You are a credit card expert. Provide a clear explanation in TWO paragraphs 
                        (around 250-300 words total). 
                        
                        First paragraph should cover:
                        • Definition/explanation of the concept
                        • How it affects cardholders
                        • Important numbers or percentages
                        
                        Second paragraph should cover:
                        • Common scenarios or examples
                        • Best practices or tips
                        • Practical implications for cardholders
                        
                        Keep the tone professional but conversational, and ensure there's a natural flow 
                        between the paragraphs. Use specific numbers and examples where relevant."""
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ]
                
                response = self.rag_agent.llm.get_completion_sync(messages)
                
                return {
                    "answer": response,
                    "image_url": None
                }

        except Exception as e:
            print(f"Error in orchestrator: {str(e)}")
            return {
                "answer": "I apologize, but I encountered an error while processing your request.",
                "image_url": None
            }

    def extract_card_names(self, text: str) -> list:
        """Extract credit card names from text"""
        card_names = []
        common_cards = [
            "Chase Sapphire Preferred",
            "Chase Sapphire Reserve",
            "Chase Freedom Unlimited",
            "Chase Freedom Flex",
            "American Express Gold",
            "American Express Platinum",
            "Citi Double Cash",
            "Capital One Venture",
            "Discover it",
            "Capital One Quicksilver"
        ]
        
        text_lower = text.lower()
        for card in common_cards:
            if card.lower() in text_lower:
                card_names.append(card)
        
        # Also look for patterns like "XXX Card"
        import re
        card_patterns = re.findall(r'([A-Z][a-zA-Z\s]+(?:Card|CARD|card))', text)
        card_names.extend(card_patterns)
        
        return list(set(card_names))  # Remove duplicates

    def needs_web_search(self, rag_response: str) -> bool:
        """Determine if web search is needed based on RAG response"""
        # Implement logic to decide if web search is needed
        return len(rag_response) < 100  # Simple heuristic

    def needs_card_image(self, response: str) -> bool:
        """Determine if response contains credit card recommendation"""
        return any(keyword in response.lower() for keyword in ["recommend", "card", "credit card"])

    def combine_context(self, rag_context: str, web_context: str) -> str:
        """Combine context from different sources"""
        return f"{rag_context}\n\nAdditional Information:\n{web_context}"

    def generate_response(self, query: str, context: str) -> str:
        """Generate response using LLM"""
        messages = [
            {"role": "system", "content": "You are a helpful credit card expert assistant."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]
        return self.rag_agent.llm.get_completion(messages) 