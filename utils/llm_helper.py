from together import Together
from typing import Optional, List, Dict
import openai
import time
import os
from tenacity import retry, stop_after_attempt, wait_exponential
import streamlit as st

class LLMHelper:
    def __init__(self):
        # Use st.secrets in production, fallback to os.environ for local development
        api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
        self.max_retries = 3
        self.base_delay = 1  # Base delay in seconds

    def get_completion(self, prompt: str, context: Optional[str] = None) -> str:
        try:
            # Format messages
            if context:
                messages = [
                    {"role": "system", "content": "You are a helpful credit card expert assistant."},
                    {"role": "user", "content": f"Using this context: {context}\n\nAnswer this question: {prompt}"}
                ]
            else:
                messages = [
                    {"role": "system", "content": "You are a helpful credit card expert assistant."},
                    {"role": "user", "content": prompt}
                ]

            # Call the Together API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=512,
                temperature=0.7,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=["\n"],
                stream=True
            )
            
            full_response = ""
            try:
                for chunk in response:
                    if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                        if hasattr(chunk.choices[0], 'delta'):
                            if hasattr(chunk.choices[0].delta, 'content'):
                                content = chunk.choices[0].delta.content
                                if content:
                                    full_response += content
            except Exception as e:
                print(f"Error processing stream: {str(e)}")
                if not full_response:
                    return "I apologize, but I couldn't generate a response at this time."
            
            return full_response.strip() if full_response else "I apologize, but I couldn't generate a response at this time."

        except Exception as e:
            print(f"Error in LLM completion: {str(e)}")
            return "I apologize, but I encountered an error while processing your request."

    @retry(
        stop=stop_after_attempt(3),  # Retry 3 times
        wait=wait_exponential(multiplier=1, min=4, max=10),  # Wait between retries with exponential backoff
        reraise=True  # Raise the last exception if all retries fail
    )
    def get_completion_sync(self, messages: List[Dict[str, str]]) -> str:
        """Get completion from OpenAI with retry logic"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content

        except openai.APIError as e:
            if "503" in str(e):  # Service Unavailable
                print(f"OpenAI API temporarily unavailable, retrying... Error: {e}")
                raise  # Retry through decorator
            else:
                print(f"OpenAI API error: {e}")
                return self._get_fallback_response(messages[-1]["content"])

        except Exception as e:
            print(f"Unexpected error in get_completion_sync: {e}")
            return self._get_fallback_response(messages[-1]["content"])

    def _get_fallback_response(self, query: str) -> str:
        """Provide a fallback response when API fails"""
        # Basic fallback responses for common credit card questions
        fallback_responses = {
            "apr": "APR (Annual Percentage Rate) is the yearly interest rate you'll pay if you carry a balance on your credit card. It's important to pay your full balance each month to avoid paying interest.",
            "credit score": "A credit score is a number between 300-850 that represents your creditworthiness. Higher scores (700+) typically qualify for better credit cards and lower interest rates.",
            "annual fee": "An annual fee is a yearly charge some credit cards have for their benefits and services. Many cards offer no annual fee options.",
            "cash back": "Cash back credit cards return a percentage of your purchases as a reward, typically 1-5% depending on the category and card.",
            "balance transfer": "A balance transfer moves debt from one credit card to another, often with a 0% intro APR period to help save on interest."
        }

        # Check if query contains any keywords and return relevant response
        query_lower = query.lower()
        for keyword, response in fallback_responses.items():
            if keyword in query_lower:
                return response

        # Default fallback response
        return "I apologize, but I'm having trouble accessing the latest information. Please try your question again in a few moments."

    def get_completion_sync_formatted(self, messages: List[Dict]) -> str:
        """Non-streaming version for simpler calls"""
        try:
            # Add formatting instructions to system message
            messages[0]["content"] += """
            Provide a concise response (50-100 words) in this format:

            **Key Benefits:**
            • [Main benefit with specific numbers/details]
            • [Second benefit with specific features]
            • [Third benefit with unique value proposition]

            **Important Considerations:**
            • [Key limitation or requirement]
            • [Important fee or restriction]

            **User Experience:**
            • [App/Website rating and features]
            • [Customer service highlights]
            • [Unique user benefits]

            **Quick Tips:**
            • [Most important tip]
            • [Secondary tip]
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stream=False
            )
            
            if hasattr(response, 'choices') and len(response.choices) > 0:
                generated_text = response.choices[0].message.content.strip()
                if len(generated_text.split()) < 30:  # Minimum 30 words
                    return "I apologize, but I couldn't generate a detailed enough response. Please try again."
                return generated_text
            return "I apologize, but I couldn't generate a response at this time."
            
        except Exception as e:
            print(f"Error in sync completion: {str(e)}")
            return "I apologize, but I encountered an error while processing your request." 