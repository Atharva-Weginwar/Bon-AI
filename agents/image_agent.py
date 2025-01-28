import boto3
from utils.s3_helper import S3Helper
from typing import Optional
from urllib.parse import quote

class ImageAgent:
    def __init__(self, s3_helper: S3Helper):
        self.s3 = s3_helper
        # Map of card names to their exact image filenames
        self.card_image_map = {
            "Chase Freedom Unlimited": "Chase Freedom Unlimited® Credit Card.png",
            "Chase Freedom Flex": "Chase Freedom Flex℠ Credit Card.png",
            "Chase Sapphire Preferred": "Chase Sapphire Preferred® Credit Card.png",
            "Chase Sapphire Reserve": "Chase Sapphire Reserve® Credit Card.png",
            "Discover it": "Discover it® Credit Card.png",
            "Capital One Venture": "Capital One Venture® Credit Card.png",
            "American Express Gold": "American Express Gold® Credit Card.png",
            "American Express Platinum": "American Express Platinum® Credit Card.png"
        }

    def get_card_image(self, card_name: str) -> Optional[str]:
        """Get credit card image URL from S3"""
        try:
            # Clean the card name for matching
            clean_name = card_name.replace('®', '').replace('℠', '').replace('™', '').strip()
            
            # Find the matching image filename
            image_file = None
            for card, filename in self.card_image_map.items():
                if card.lower() in clean_name.lower():
                    image_file = filename
                    break
            
            if not image_file:
                print(f"No image found for card: {card_name}")
                return None

            # Get the URL from S3
            print(f"Getting image for card: {clean_name}")
            print(f"Image filename: {image_file}")
            
            # Use urllib.parse for proper URL encoding
            folder_path = quote("credit cards")
            file_name = quote(image_file)
            image_url = self.s3.get_image_url(f"{folder_path}/{file_name}")
            
            return image_url

        except Exception as e:
            print(f"Error getting card image: {str(e)}")
            return None 