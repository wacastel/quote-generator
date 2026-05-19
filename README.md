# ImageWorks Quote Extractor
A multimodal AI-powered Python script designed to parse unstructured customer RFQ emails and attached design sketches. By leveraging the Gemini 2.5 Flash model and Pydantic for strict structured prompting, this tool extracts key manufacturing specifications and outputs them as a clean JSON payload and a flattened CSV file.
## Features
* Multimodal Ingestion: Processes both raw email text and image attachments (sketches, diagrams) simultaneously.
* Strict JSON Schema: Enforces a rigid data structure using Pydantic, ensuring predictable outputs for the downstream Angular frontend and Supabase edge functions.
* CSV Export: Automatically flattens nested JSON data and appends it to `image_works_quotes.csv` for easy stakeholder review.
## Prerequisites
Ensure you have Python installed, then install the required dependencies:
```bash
pip install google-genai pillow pydantic python-dotenv
```
## Environment Setup
Create a `.env` file in the root directory of this project and add your Google Gemini API key:
```text
GEMINI_API_KEY=your_actual_api_key_here
```
> Note: Ensure your `.env` file is added to your `.gitignore` to prevent leaking credentials.
## Usage
1. Place a sample customer sketch in the project directory (e.g., `test_sketch.jpg`).
2. Execute the script from your terminal:
```bash
python quote_extractor.py
```
## Output
The script will print the structured JSON to the terminal and append a new row to `image_works_quotes.csv` containing the extracted project type, substrate, quantity, dimensions, and the AI's confidence score.
