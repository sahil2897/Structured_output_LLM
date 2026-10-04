from transformers import AutoTokenizer, AutoModelForCausalLM


class LLMClient:
    def __init__(self, model_name: str, hf_token = None):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            token=hf_token
        )

    def generate(self, messages, tools=None, max_new_tokens=400):
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tools=tools,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False
        )

        response = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True
        )

        return response