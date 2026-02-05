import os
from dotenv import load_dotenv

load_dotenv()

# PrivateKey Configuration
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")