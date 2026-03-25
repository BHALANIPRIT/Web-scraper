import os
from dotenv import load_dotenv
from openai import OpenAI
from .io_processor import IOProcessor
from .data_refiner import refine_structured_data

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("CRITICAL ERROR: OPENROUTER_API_KEY not found in .env file.")

class LLMProcessor:
    def __init__(self):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model_name = "mistralai/mistral-7b-instruct"  # or any OpenRouter model
        self.io = IOProcessor()

    def process_scraped_content(self, raw_headings, target_schema="Name, Price, Description"):
        if not raw_headings:
            return None

        prompt = self.io.prepare_input(raw_headings, target_schema)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            output_text = response.choices[0].message.content

            structured_json = self.io.parse_output(output_text)
            final_df = refine_structured_data(structured_json)

            return final_df

        except Exception as e:
            print(f"LLM Module Error: {e}")
            return None