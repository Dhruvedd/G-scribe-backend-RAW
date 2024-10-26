import fitz  # PyMuPDF
import openai  # for OpenAI API
from fpdf import FPDF  # for PDF generation

# Paths to input and output files
pdf_path = "sample_test.pdf"  # Replace with the actual PDF file path
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
    full_prompt = f"{prompt}\n\nPatient's Blood Test Report:\n{text}\n\nPlease provide the output in the following format:\n\n1. **Critical Findings**: List any values outside normal range.\n2. **Analysis**: Explain the potential implications of these findings.\n3. **Recommendations**: Provide possible next steps for the doctor."

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
def create_pdf(output_text, pdf_filename="output_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Patient Blood Test Analysis Report", ln=True, align="C")
    
    # Add each section to the PDF with specific formatting
    pdf.set_font("Arial", "", 12)
    
    # Split the output into sections based on the requested format
    sections = output_text.split("\n")
    for line in sections:
        # Adjust line spacing and indentation for headings and bullet points
        if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
            pdf.ln(10)  # Add space before each main section
            pdf.set_font("Arial", "B", 12)
        elif line.startswith("-"):
            pdf.set_font("Arial", "I", 12)
            pdf.cell(10)  # Indent for bullet points
        
        pdf.multi_cell(0, 10, line)
    
    # Output PDF to file
    pdf.output(pdf_filename)
    print(f"PDF generated: {pdf_filename}")

# Main execution example
file_path = txt_file_path  # Use the saved text file from the PDF

prompt = """Please read the text file containing disorganized data about a patient's blood test report. 

I need a professional doctor's report with the following structure:

Title: Blood Report

Patient Name: [Patient’s Name]  
Date of Testing: [Date of Entry]  
Type of Test: [Type of Test]  

Findings: [Write a structured, formal analysis in paragraphs with all important values in bold. Do not use bullet points. For example, write findings as you would in a detailed doctor's report, such as "The patient's hemoglobin level of **12.0 g/dL** is within the normal range, whereas the **WBC count** of **15,000/uL** is elevated, indicating..."]

At the end, please include:  
Sign of Doctor: Dr. [Doctor’s Name]
"""

api_key = "sk-6WoL_c40FFZFeAQp1WX4OkkKHMgoIrteTNxlshjROdT3BlbkFJzCvmdqEXdxh5Ny-sPqZPB5VA16T00I7Ib9vhqtdbkA"  # Replace with your actual OpenAI API Key

# Read text from file
text = read_text_from_file(file_path)

# Analyze text with OpenAI API
result = analyze_text_with_openai(text, prompt, api_key)

# Generate the PDF if we received a result
if result:
    create_pdf(result, pdf_filename="blood_test_report.pdf")
