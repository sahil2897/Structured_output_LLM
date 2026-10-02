import os
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = "Qwen/Qwen3-4B-Instruct-2507"
HF_TOKEN = os.getenv("HF_TOKEN")