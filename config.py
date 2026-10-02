import os
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
HF_TOKEN = os.getenv("HF_TOKEN")