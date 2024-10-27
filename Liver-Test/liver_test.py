import os
import fitz  # PyMuPDF
import openai  # for OpenAI API
from fpdf import FPDF  # for PDF generation
from dotenv import load_dotenv

load_dotenv()

note = ""  # Optional note to be added at the bottom of the report

API_KEY = os.getenv("API_KEY")

# Paths to input and output files
pdf_path = "liver_test_sample_report.pdf"  # Updated input file path
txt_file_path = "text.txt"  # Temporary text file path for extracted PDF text

# Function to extract text from the PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text()
    return text

# Extract text from the PDF and save it to a text file
try:
    pdf_text = extract_text_from_pdf(pdf_path)
    with open(txt_file_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(pdf_text)
    print(f"Text saved successfully to {txt_file_path}")
except Exception as e:
    print("Error writing to file:", e)

# Function to read text from the saved text file
def read_text_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text

# Function to analyze text with OpenAI's chat completion API
def analyze_text_with_openai(text, prompt, api_key):
    openai.api_key = api_key
    
    # Prepare the input prompt for the model, requesting structured output
    full_prompt = f"{prompt}\n\nPatient's Liver Function Test Report:\n{text}\n Doctor's Note to be added at the bottom of the report: {note}"

    try:
        # Use the chat completions API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a medical assistant."},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        result = response['choices'][0]['message']['content']
        return result
    except Exception as e:
        print("Error with OpenAI API:", e)
        return None

# Function to create a PDF with a specific format
def create_pdf(output_text, pdf_filename="liver_test_output_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    
    # Load the Unicode fonts with full path
    base_dir = os.path.dirname(__file__)
    pdf.add_font("DejaVu", "", os.path.join(base_dir, "fonts", "DejaVuSans.ttf"), uni=True)
    pdf.add_font("DejaVu", "B", os.path.join(base_dir, "fonts", "DejaVuSans-Bold.ttf"), uni=True)
    pdf.add_font("DejaVu", "I", os.path.join(base_dir, "fonts", "DejaVuSans-Oblique.ttf"), uni=True)

    # Title
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(200, 10, "Patient Liver Function Test Analysis Report", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # Add each section to the PDF with specific formatting
    pdf.set_font("DejaVu", "", 12)
    
    # Split the output into sections based on the requested format
    sections = output_text.split("\n")
    for line in sections:
        line = line.strip()  # Remove leading/trailing whitespace
        if line:  # Only process non-empty lines
            if line.startswith("**Title**") or line.startswith("**Patient Name**"):
                pdf.set_font("DejaVu", "B", 12)
                pdf.multi_cell(180, 10, line)  # Set width to 180
            elif line.startswith("**Findings**"):
                pdf.set_font("DejaVu", "B", 14)
                pdf.cell(0, 10, line, new_x="LMARGIN", new_y="NEXT")
            elif line.startswith("**Recommendations**"):
                pdf.set_font("DejaVu", "B", 14)
                pdf.cell(0, 10, line, new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.set_font("DejaVu", "", 12)
                pdf.multi_cell(180, 10, line)  # Set width to 180 for regular text

    # Output PDF to file
    try:
        pdf.output(pdf_filename)
        print(f"PDF generated: {pdf_filename}")
    except Exception as e:
        print("Error saving PDF:", e)

        
# Main execution example
file_path = txt_file_path  # Use the saved text file from the PDF

# Prompt specific to the Liver Function Test
prompt = """Please read the data from the patient's liver function test report and create a professional, structured doctor's report with the following format:

---

**Title**: Liver Function Test Report

**Patient Name**: [Patient’s Name]  
**Date of Testing**: [Date of Entry]  
**Type of Test**: [Type of Test, e.g., Comprehensive Metabolic Panel]

**Findings**:
For each critical finding, provide a detailed analysis in paragraph form without line breaks between sentences. Emphasize critical values by bolding them, and explain their medical significance. For example, write findings like this:
"The patient's **ALT** level of **75 U/L** is elevated, indicating potential liver inflammation. The **AST** level is also raised, supporting a diagnosis of possible liver injury."

**Required Critical Findings to Address**:
1. ALT (Alanine Aminotransferase)
2. AST (Aspartate Aminotransferase)
3. ALP (Alkaline Phosphatase)
4. Bilirubin (Total, Direct, Indirect)
5. Albumin
6. Total Protein
7. GGT (Gamma-Glutamyl Transferase, if available)

**Recommendations**:
Provide specific recommendations based on the findings. If liver enzyme levels are elevated, suggest possible follow-up tests or actions, such as imaging or referral to a gastroenterologist. Each recommendation should be in a separate paragraph for clarity.

End the report with:
"Sign of Doctor: Dr. [Doctor’s Name]"

---

This format should result in a report with well-organized sections and clear, complete paragraphs for each finding.

"""

api_key = API_KEY  # Replace with your actual OpenAI API Key

# Read text from file
text = read_text_from_file(file_path)

# Analyze text with OpenAI API
result = analyze_text_with_openai(text, prompt, api_key)

# Generate the PDF if we received a result
if result:
    create_pdf(result, pdf_filename="liver_test_output_report.pdf")