from dotenv import load_dotenv
import os

load_dotenv(verbose=True)
KEY = os.getenv("COMPUTER_VISION_SUBSCRIPTION_KEY")
ENDPOINT = os.getenv("COMPUTER_VISION_ENDPOINT")
