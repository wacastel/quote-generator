import os
import json
import csv
from PIL import Image
from dotenv import load_dotenv

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key not found. Please ensure GEMINI_API_KEY is set in your .env file.")

client = genai.Client(api_key=api_key)

# 2. Define the Strict JSON Schema using Pydantic
class Dimensions(BaseModel):
    width: float
    height: float
    unit: str

class QuoteRequest(BaseModel):
    project_type: str
    substrate: str
    quantity: int
    dimensions: Dimensions
    confidence_score: str = Field(pattern="^(High|Medium|Low)$")

def extract_quote_specs(email_text: str, image_path: str) -> str:
    """
    Passes an email and an attached sketch to Gemini 2.5 Flash to extract
    manufacturing specifications into a strict JSON format.
    """
    try:
        customer_sketch = Image.open(image_path)
    except FileNotFoundError:
        return json.dumps({"error": f"Could not find image at {image_path}. Please check the file path."})
    except Exception as e:
        return json.dumps({"error": f"Error loading image: {str(e)}"})

    config = types.GenerateContentConfig(
        system_instruction=(
            "You are a manufacturing sales assistant. Analyze the provided email text and image attachment. "
            "Extract the following specifications and return ONLY a valid JSON object matching this schema."
        ),
        response_mime_type="application/json",
        response_schema=QuoteRequest,
        temperature=0.1
    )
    
    prompt = f"Customer Email Body:\n{email_text}\n\nPlease extract the specs based on this email and the attached image."

    try:
        # Using Flash to bypass the Pro free-tier limits
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, customer_sketch],
            config=config
        )
        return response.text
        
    except Exception as e:
        return json.dumps({"error": f"API Error: {str(e)}"})

def save_to_csv(parsed_data: dict, output_filename: str = "quote_output.csv"):
    """
    Flattens the structured JSON data and appends it to a CSV file.
    """
    # Define the headers, flattening the nested 'dimensions' object
    headers = [
        "Project Type",
        "Substrate",
        "Quantity",
        "Width",
        "Height",
        "Unit",
        "Confidence Score"
    ]

    # Extract values safely using .get()
    row_data = [
        parsed_data.get("project_type", ""),
        parsed_data.get("substrate", ""),
        parsed_data.get("quantity", ""),
        parsed_data.get("dimensions", {}).get("width", ""),
        parsed_data.get("dimensions", {}).get("height", ""),
        parsed_data.get("dimensions", {}).get("unit", ""),
        parsed_data.get("confidence_score", "")
    ]

    file_exists = os.path.isfile(output_filename)
    
    # Append to the file (or create it if it doesn't exist)
    with open(output_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Only write the header row if this is a brand new file
        if not file_exists:
            writer.writerow(headers)
            
        writer.writerow(row_data)

# ==========================================
# Execution Block for Testing
# ==========================================
if __name__ == "__main__":
    
    test_email = """
    Hi team, attached is a sketch for a new custom hanging sign. 
    We need 100 of these for our midwest stores. Weather resistant material, die-cut shape. 
    Can you handle? Looking to order soon.
    """
    
    test_image_path = "test_sketch.jpg" 
    csv_filename = "image_works_quotes.csv"
    
    print("Initializing Gemini API Call using modern SDK...")
    print(f"Loading image from: {test_image_path}")
    print("-" * 40)
    
    raw_json_result = extract_quote_specs(test_email, test_image_path)
    
    try:
        parsed_result = json.loads(raw_json_result)
        
        if "error" in parsed_result:
             print(f"Error encountered: {parsed_result['error']}")
        else:
            print("API Response Successfully Received and Parsed:\n")
            print(json.dumps(parsed_result, indent=4))
            
            # Trigger the CSV export
            save_to_csv(parsed_result, csv_filename)
            print(f"\n✅ Data successfully exported to {csv_filename}")
            
    except json.JSONDecodeError:
        print("Failed to decode JSON. Raw response from API:")
        print(raw_json_result)
