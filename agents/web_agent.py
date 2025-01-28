from utils.llm_helper import LLMHelper
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup
import praw
import re
import os
import json

class WebAgent:
    def __init__(self, llm: LLMHelper):
        self.llm = llm
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Initialize Reddit client
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent="CreditCardRAGBot/1.0"
        )
        # Store card data with application links
        self.card_data = {
            "Chase Freedom Unlimited®": {
                "key_benefits": [
                    "1.5% cash back on all purchases",
                    "3% cash back on dining and drugstores",
                    "No annual fee"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$0",
                "intro_apr": "0% for 15 months",
                "regular_apr": "19.24% - 27.99% Variable",
                "apply_link": "https://creditcards.chase.com/cash-back-credit-cards/freedom/unlimited",
                "category": ["cashback", "no-annual-fee", "low-apr"]
            },
            "Chase Freedom Flex℠": {
                "key_benefits": [
                    "5% cash back on rotating quarterly categories",
                    "3% on dining and drugstores",
                    "1% on all other purchases"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$0",
                "intro_apr": "0% for 15 months",
                "regular_apr": "19.24% - 27.99% Variable",
                "apply_link": "https://creditcards.chase.com/cash-back-credit-cards/freedom/flex",
                "category": ["cashback", "rotating-categories", "no-annual-fee"]
            },
            "Chase Sapphire Preferred®": {
                "key_benefits": [
                    "5x points on travel through Chase Ultimate Rewards",
                    "3x points on dining and online grocery purchases",
                    "60,000 bonus points after spending $4,000 in first 3 months"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$95",
                "intro_apr": "None",
                "regular_apr": "20.49% - 27.49% Variable",
                "apply_link": "https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred",
                "category": ["travel", "rewards", "points"]
            },
            "Discover it® Cash Back": {
                "key_benefits": [
                    "5% cash back on rotating quarterly categories (up to quarterly maximum)",
                    "1% cash back on all other purchases",
                    "Cashback Match™ - Discover automatically matches all cash back earned in first year",
                    "No annual fee"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$0",
                "intro_apr": "0% for 15 months",
                "regular_apr": "16.24% - 27.24% Variable",
                "apply_link": "https://www.discover.com/credit-cards/cash-back/it-card.html",
                "category": ["cashback", "rotating-categories", "no-annual-fee"]
            },
            "Discover it® Student Cash Back": {
                "key_benefits": [
                    "5% cash back on rotating quarterly categories (up to quarterly maximum)",
                    "1% cash back on all other purchases",
                    "Good Grades Rewards - $20 statement credit each school year for 3.0+ GPA",
                    "Cashback Match™ for first year"
                ],
                "credit_score": "Fair to Good (630+)",
                "annual_fee": "$0",
                "intro_apr": "0% for 6 months",
                "regular_apr": "17.24% - 26.24% Variable",
                "apply_link": "https://www.discover.com/credit-cards/student/it-card.html",
                "category": ["student", "cashback", "no-annual-fee"]
            },
            "Discover it® Miles": {
                "key_benefits": [
                    "1.5x miles on every purchase",
                    "Mile-for-mile match at end of first year",
                    "Redeem miles for travel purchases or cash back",
                    "No blackout dates"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$0",
                "intro_apr": "0% for 15 months",
                "regular_apr": "16.24% - 27.24% Variable",
                "apply_link": "https://www.discover.com/credit-cards/travel/it-miles.html",
                "category": ["travel", "miles", "no-annual-fee"]
            },
            "Wells Fargo Active Cash®": {
                "key_benefits": [
                    "2% cash rewards on all purchases",
                    "$200 cash rewards bonus after spending $1,000 in first 3 months",
                    "No category restrictions or quarterly activations"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$0",
                "intro_apr": "0% for 15 months",
                "regular_apr": "19.24% - 29.24% Variable",
                "apply_link": "https://www.wellsfargo.com/credit-cards/active-cash/",
                "category": ["cashback", "no-annual-fee", "flat-rate"]
            },
            "Wells Fargo Autograph℠": {
                "key_benefits": [
                    "3x points on restaurants, travel, gas stations, transit",
                    "3x points on streaming services and phone plans",
                    "20,000 bonus points after spending $1,000 in first 3 months"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$0",
                "intro_apr": "0% for 12 months",
                "regular_apr": "19.24% - 29.24% Variable",
                "apply_link": "https://www.wellsfargo.com/credit-cards/autograph/",
                "category": ["rewards", "no-annual-fee", "travel"]
            },
            "Wells Fargo Reflect®": {
                "key_benefits": [
                    "Up to 21 months 0% intro APR on purchases and balance transfers",
                    "Cell phone protection up to $600",
                    "Zero liability protection"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$0",
                "intro_apr": "0% for up to 21 months",
                "regular_apr": "17.24% - 29.24% Variable",
                "apply_link": "https://www.wellsfargo.com/credit-cards/reflect/",
                "category": ["balance-transfer", "no-annual-fee", "low-apr"]
            },
            "American Express Gold Card": {
                "key_benefits": [
                    "4X points at restaurants worldwide and U.S. supermarkets (up to $25,000 per year)",
                    "3X points on flights booked directly with airlines",
                    "$120 dining credit annually ($10 monthly)",
                    "$120 Uber Cash annually ($10 monthly)"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$250",
                "intro_apr": "None",
                "regular_apr": "20.24% - 28.24% Variable",
                "apply_link": "https://www.americanexpress.com/us/credit-cards/card/gold/",
                "category": ["rewards", "dining", "travel"]
            },
            "American Express Platinum Card": {
                "key_benefits": [
                    "5X points on flights booked directly with airlines or through Amex Travel",
                    "5X points on prepaid hotels booked through Amex Travel",
                    "$200 hotel credit annually",
                    "Access to Centurion Lounges and Priority Pass lounges",
                    "$200 airline fee credit annually"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$695",
                "intro_apr": "None",
                "regular_apr": "20.24% - 28.24% Variable",
                "apply_link": "https://www.americanexpress.com/us/credit-cards/card/platinum/",
                "category": ["premium", "travel", "luxury"]
            },
            "American Express Blue Cash Preferred®": {
                "key_benefits": [
                    "6% cash back at U.S. supermarkets (up to $6,000 per year)",
                    "6% cash back on select U.S. streaming services",
                    "3% cash back on transit and U.S. gas stations",
                    "1% cash back on other purchases"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$95",
                "intro_apr": "0% for 12 months",
                "regular_apr": "18.24% - 29.24% Variable",
                "apply_link": "https://www.americanexpress.com/us/credit-cards/card/blue-cash-preferred/",
                "category": ["cashback", "groceries", "streaming"]
            },
            "American Express Blue Cash Everyday®": {
                "key_benefits": [
                    "3% cash back at U.S. supermarkets (up to $6,000 per year)",
                    "3% cash back at U.S. gas stations",
                    "3% cash back on U.S. online retail purchases",
                    "1% cash back on other purchases"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$0",
                "intro_apr": "0% for 15 months",
                "regular_apr": "18.24% - 29.24% Variable",
                "apply_link": "https://www.americanexpress.com/us/credit-cards/card/blue-cash-everyday/",
                "category": ["cashback", "no-annual-fee", "groceries"]
            }
        }

    def search_web(self, query: str) -> Dict[str, Dict]:
        """Use LLM to analyze and format credit card information"""
        try:
            search_prompt = f"""
            Analyze and provide credit card recommendations for: {query}
            
            Return ONLY a valid JSON object in this exact format, with no additional text or markdown:
            {{
                "Chase Freedom Unlimited®": {{
                    "key_benefits": [
                        "1.5% cash back on all purchases",
                        "3% cash back on dining and drugstores",
                        "No annual fee"
                    ],
                    "credit_score": "Good to Excellent (670+)",
                    "annual_fee": "$0",
                    "intro_apr": "0% for 15 months",
                    "regular_apr": "19.24% - 27.99% Variable"
                }}
            }}
            """
            
            response = self.llm.get_completion_sync([
                {
                    "role": "system", 
                    "content": "You are a credit card expert. You must return only a valid JSON object, no markdown formatting or additional text."
                },
                {
                    "role": "user", 
                    "content": search_prompt
                }
            ])
            
            # Clean the response
            response = response.strip()
            if response.startswith('```'):
                response = response.split('\n', 1)[1]  # Remove first line
            if response.startswith('json'):
                response = response.split('\n', 1)[1]  # Remove json line if present
            if response.endswith('```'):
                response = response.rsplit('\n', 1)[0]  # Remove last line
            response = response.strip()
            
            print(f"Cleaned JSON response: {response}")  # Debug print
            
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Response that failed parsing: {response}")
                return self.get_fallback_recommendations()

        except Exception as e:
            print(f"Error in search_web: {str(e)}")
            return self.get_fallback_recommendations()

    def get_card_recommendations(self, query: str) -> Dict[str, Dict]:
        """Get card recommendations based on query"""
        query = query.lower()
        try:
            # Get initial recommendations based on query
            if "american express" in query or "amex" in query:
                cards = {k: v for k, v in self.card_data.items() if "American Express" in k}
            elif "wells fargo" in query or "wf" in query:
                cards = {k: v for k, v in self.card_data.items() if "Wells Fargo" in k}
            elif "discover" in query:
                cards = {k: v for k, v in self.card_data.items() if "Discover" in k}
            elif "chase" in query:
                cards = {k: v for k, v in self.card_data.items() if "Chase" in k}
            else:
                # Other filtering logic...
                cards = self.card_data

            # Limit to top 4 cards
            card_items = list(cards.items())[:4]  # Take only first 4 cards
            return dict(card_items)

        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return dict(list(self.card_data.items())[:2])  # Return only 2 cards in case of error

    def get_fallback_recommendations(self) -> Dict[str, Dict]:
        """Fallback recommendations when search fails"""
        return {
            "Chase Freedom Unlimited®": {
                "key_benefits": [
                    "1.5% cash back on all purchases",
                    "3% cash back on dining and drugstores",
                    "No annual fee"
                ],
                "credit_score": "Good to Excellent (670+)",
                "annual_fee": "$0",
                "intro_apr": "0% for 15 months",
                "regular_apr": "19.24% - 27.99% Variable"
            }
        }

    def format_response(self, recommendations: Dict[str, Dict], is_recommendation: bool = True) -> str:
        """Format response based on query type"""
        if not recommendations:
            return "I apologize, but I couldn't find any relevant information at this time."

        # For factual questions, return a simple paragraph
        if not is_recommendation:
            response = []
            for card_name, details in recommendations.items():
                benefits = details.get('key_benefits', [])
                features = [
                    f"credit score ({details.get('credit_score', 'Not specified')})",
                    f"annual fee ({details.get('annual_fee', 'Not specified')})",
                    f"intro APR ({details.get('intro_apr', 'Not specified')})"
                ]
                response.append(f"The {card_name} offers {', '.join(benefits)}. It requires a {' and has a '.join(features)}.")
            return " ".join(response)

        # For card recommendations, use a structured table format
        response = ["**Recommended Credit Cards:**\n"]
        
        # Add CSS for better table styling
        response.append("""
<style>
.credit-card-table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
}
.credit-card-table td {
    padding: 15px;
    vertical-align: top;
    border: 1px solid #2e2e2e;
    background-color: #1e1e1e;
}
.card-title {
    font-size: 1.1em;
    font-weight: bold;
    margin-bottom: 10px;
    color: #ffffff;
}
.benefit-list {
    margin: 10px 0;
}
.apply-button {
    display: inline-block;
    margin-top: 10px;
    padding: 8px 20px;
    background: none;  /* Remove background */
    color: #FFFFFF;  /* Pure bright white */
    text-decoration: none;
    border-radius: 4px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    font-weight: 700;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    border: none;
    text-align: center;
    min-width: 120px;
}
.apply-button:hover {
    text-decoration: none;
    color: #FFFFFF;  /* Keep text white on hover */
}
</style>
""")

        # Convert recommendations to list for easier handling
        cards = list(recommendations.items())
        
        # Process cards in pairs
        for i in range(0, len(cards), 2):
            card1_name, card1_details = cards[i]
            
            # Start table row
            response.append('<table class="credit-card-table"><tr>')
            
            # First card
            card1_html = f"""
<td width="50%">
    <div class="card-title">{card1_name}</div>
    <div class="benefit-list">
        {'<br>'.join(f"• {benefit}" for benefit in card1_details.get('key_benefits', []))}
    </div>
    <div class="card-details">
        • Credit Score: {card1_details.get('credit_score', 'Not specified')}<br>
        • Annual Fee: {card1_details.get('annual_fee', 'Not specified')}<br>
        • Intro APR: {card1_details.get('intro_apr', 'Not specified')}
    </div>
    <a href="{card1_details.get('apply_link')}" class="apply-button">Apply Now</a>
</td>"""
            response.append(card1_html)

            # Second card (if exists)
            if i + 1 < len(cards):
                card2_name, card2_details = cards[i + 1]
                card2_html = f"""
<td width="50%">
    <div class="card-title">{card2_name}</div>
    <div class="benefit-list">
        {'<br>'.join(f"• {benefit}" for benefit in card2_details.get('key_benefits', []))}
    </div>
    <div class="card-details">
        • Credit Score: {card2_details.get('credit_score', 'Not specified')}<br>
        • Annual Fee: {card2_details.get('annual_fee', 'Not specified')}<br>
        • Intro APR: {card2_details.get('intro_apr', 'Not specified')}
    </div>
    <a href="{card2_details.get('apply_link')}" class="apply-button">Apply Now</a>
</td>"""
                response.append(card2_html)
            else:
                # Empty cell for alignment if odd number of cards
                response.append('<td width="50%"></td>')
            
            response.append('</tr></table>')

        # Add general sections at the bottom with consistent styling
        response.extend([
            '\n<div style="margin-top: 20px;">',
            '<strong>Important Considerations:</strong>',
            '<ul style="margin-top: 10px;">',
            '<li>A good to excellent credit score (670+) is required for approval</li>',
            '<li>Regular APR ranges from 19.24% to 27.99% variable after the intro period</li>',
            '<li>Credit limit depends on creditworthiness and income</li>',
            '</ul>',
            '</div>',
            
            '<div style="margin-top: 20px;">',
            '<strong>Quick Tips:</strong>',
            '<ul style="margin-top: 10px;">',
            '<li>Pay your balance in full each month to avoid interest charges</li>',
            '<li>Monitor your credit utilization (keep it below 30% of your limit)</li>',
            '<li>Set up automatic payments to avoid missing due dates</li>',
            '<li>Consider your spending habits when choosing between cards</li>',
            '</ul>',
            '</div>'
        ])

        return "\n".join(response)

    def get_card_reviews(self, card_name: str) -> Dict[str, str]:
        """Get card reviews using AI analysis"""
        try:
            review_prompt = f"""
            Provide user experience data for {card_name} in this exact JSON format, with no additional text or markdown:
            {{
                "rating": "4.5/5",
                "app_rating": "4.7/5",
                "customer_service": "24/7 phone support available",
                "user_highlights": "Easy to use mobile app, quick approval process"
            }}
            """
            
            response = self.llm.get_completion_sync([
                {
                    "role": "system", 
                    "content": "You are a credit card review analyst. Return only a valid JSON object, no markdown or additional text."
                },
                {
                    "role": "user", 
                    "content": review_prompt
                }
            ])
            
            # Clean the response
            response = response.strip()
            if response.startswith('```'):
                response = response.split('\n', 1)[1]  # Remove first line
            if response.startswith('json'):
                response = response.split('\n', 1)[1]  # Remove json line if present
            if response.endswith('```'):
                response = response.rsplit('\n', 1)[0]  # Remove last line
            response = response.strip()
            
            print(f"Cleaned review JSON response: {response}")  # Debug print
            
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                print(f"Review JSON parsing error: {str(e)}")
                print(f"Review response that failed parsing: {response}")
                return self.get_fallback_reviews()
                
        except Exception as e:
            print(f"Error getting reviews: {str(e)}")
            return self.get_fallback_reviews()

    def get_fallback_reviews(self) -> Dict[str, str]:
        """Fallback reviews when AI analysis fails"""
        return {
            "rating": "4.5/5",
            "app_rating": "4.6/5",
            "customer_service": "24/7 support available",
            "user_highlights": "Mobile app access, digital wallet integration"
        }

    def get_card_details(self, card_name: str) -> Dict[str, str]:
        """Get card details from issuer website"""
        try:
            # Clean card name for search
            clean_name = card_name.lower().replace(' ', '-')
            
            # Try to get details from issuer website
            if 'chase' in clean_name:
                url = f"https://creditcards.chase.com/credit-cards/{clean_name}"
            elif 'amex' in clean_name or 'american-express' in clean_name:
                url = f"https://www.americanexpress.com/us/credit-cards/card/{clean_name}"
            elif 'discover' in clean_name:
                url = f"https://www.discover.com/credit-cards/{clean_name}"
            else:
                return None

            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract key details (customize based on each issuer's HTML structure)
                details = {
                    "recommended_for": self.extract_recommended_for(soup),
                    "key_benefits": self.extract_benefits(soup),
                    "requirements": self.extract_requirements(soup)
                }
                return details

            return None

        except Exception as e:
            print(f"Error getting card details: {e}")
            return None

    def extract_recommended_for(self, soup: BeautifulSoup) -> str:
        # Implementation of extract_recommended_for method
        pass

    def extract_benefits(self, soup: BeautifulSoup) -> str:
        # Implementation of extract_benefits method
        pass

    def extract_requirements(self, soup: BeautifulSoup) -> str:
        # Implementation of extract_requirements method
        pass 