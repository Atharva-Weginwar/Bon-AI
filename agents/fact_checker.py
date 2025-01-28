from together import Together
from utils.llm_helper import LLMHelper
from typing import Optional

class FactChecker:
    def __init__(self, llm_helper: LLMHelper):
        self.client = Together()
        self.model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

    def verify_response(self, response: str, context: str) -> str:
        """Verify if the response is consistent with the context"""
        try:
            messages = [
                {"role": "system", "content": "You are a fact checker. Verify if the response is consistent with the given context."},
                {"role": "user", "content": f"""
                Context: {context}
                
                Response to verify: {response}
                
                Is this response consistent with the context? Say VERIFIED if yes, or point out inconsistencies if no.
                """}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=512,
                temperature=0.7,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stream=False  # Non-streaming for simpler verification
            )
            
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            return "Unable to verify the response at this time."

        except Exception as e:
            print(f"Error in fact checking: {str(e)}")
            return "Unable to verify the response at this time."

    def verify(self, response: str) -> str:
        """Verify the response for factual accuracy"""
        messages = [
            {"role": "system", "content": "You are a fact-checker for credit card information. "
                                        "Verify the following information and correct any inaccuracies."},
            {"role": "user", "content": response}
        ]
        
        verified_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            stop=["<|eot_id|>", "<|eom_id|>"],
            stream=True
        )
        
        full_verified_response = ""
        for token in verified_response:
            if hasattr(token, 'choices'):
                content = token.choices[0].delta.content
                if content:
                    full_verified_response += content
        
        return full_verified_response.strip() 