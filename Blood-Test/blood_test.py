import os
import fitz  # PyMuPDF
import openai  # for OpenAI API
from fpdf import FPDF  # for PDF generation
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")

# Paths to input and output files
pdf_path = "sample_test2.pdf"  # Replace with the actual PDF file path

txt_file_path = "text.txt"  # Output text file path

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
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    # Write the extracted text to a text file with UTF-8 encoding
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
    full_prompt = f"{prompt}\n\nPatient's Blood Test Report:\n{text}\n"

    try:
        # Use the chat completions API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a medical assistant."},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        # Retrieve and return the generated response
        result = response['choices'][0]['message']['content']
        return result
    except Exception as e:
        print("Error with OpenAI API:", e)
        return None

# Function to create a PDF with a specific format
def create_pdf(output_text, pdf_filename="blood_test_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    
    # Load the Unicode-compatible fonts
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf")
    pdf.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf")
    pdf.add_font("DejaVu", "I", "fonts/DejaVuSans-Oblique.ttf")  # Add italic font

    # Title
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(200, 10, "Patient Blood Test Analysis Report", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # Add each section to the PDF with specific formatting
    pdf.set_font("DejaVu", "", 12)
    
    # Split the output text into sections based on the requested format
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
                pdf.multi_cell(180, 10, line)  # Use a width of 180 for regular text

    # Output PDF to file
    try:
        pdf.output(pdf_filename)
        print(f"PDF generated: {pdf_filename}")
    except Exception as e:
        print("Error saving PDF:", e)

# Main execution example
file_path = txt_file_path  # Use the saved text file from the PDF

prompt = """Please read the text file containing disorganized data about a patient's blood test report. 

I need a professional doctor's report with the following structure:

Title: Blood Report

Patient Name: [Patient’s Name]  
Date of Testing: [Date of Entry]  
Type of Test: [Type of Test]  

Findings: [Write a structured, formal analysis in paragraphs with all important values. Do not use bullet points. For example, write findings as you would in a detailed doctor's report, such as "The patient's hemoglobin level of **12.0 g/dL** is within the normal range, whereas the **WBC count** of **15,000/uL** is elevated, indicating..."]

At the end, please include:  
Sign of Doctor: Dr. [Doctor’s Name]
"""

api_key =  API_KEY # Replace with your actual OpenAI API Key

# Read text from file
text = read_text_from_file(file_path)

# Analyze text with OpenAI API
result = analyze_text_with_openai(text, prompt, api_key)

# Generate the PDF if we received a result
if result:
    create_pdf(result, pdf_filename="blood_test_report.pdf")
