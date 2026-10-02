from config import LLM_MODEL, HF_TOKEN
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL, token=HF_TOKEN)

print("MODEL:", LLM_MODEL)
print("CHAT TEMPLATE:", tokenizer.chat_template)
print("DEFAULT TEMPLATE:", tokenizer.default_chat_template)