import fitz  # PyMuPDF
import boto3  # for AWS
import json

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text()
    return text

# Extract text from the PDF and save it to a text file
pdf_path = "sample_test.pdf"  # Replace with the actual PDF file path
txt_file_path = "extracted_text.txt"  # Output text file path

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

# Function to analyze text using AWS AI services
def analyze_text_with_aws(text, prompt, aws_access_key, aws_secret_key, region, service='comprehend', endpoint_name=None):
    # Initialize AWS client based on service type
    if service == 'comprehend':
        client = boto3.client(
            'comprehend',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

        # Example: Sentiment Analysis (adjust based on your prompt/task)
        response = client.detect_sentiment(Text=text, LanguageCode='en')
        return response['Sentiment']
    
    elif service == 'sagemaker' and endpoint_name:
        client = boto3.client(
            'sagemaker-runtime',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

        # Format the input as needed for the custom SageMaker model
        input_data = {
            "prompt": prompt,
            "context": text
        }

        # Invoke the SageMaker endpoint
        response = client.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType="application/json",
            Body=json.dumps(input_data)
        )

        # Read the model response
        result = json.loads(response['Body'].read().decode("utf-8"))
        return result
    else:
        raise ValueError("Unsupported service or missing endpoint name for SageMaker.")

# Main execution example
file_path = txt_file_path  # Use the saved text file from the PDF

prompt = """Okay, I am gonna give you a text file that contains disoragnized data about a patients blood test report. 
I need you to read it and tell me exactly what reports for the patient are outside the normal range and how"""

aws_access_key = "YOUR_AWS_ACCESS_KEY"  # Replace with your actual AWS Access Key
aws_secret_key = "YOUR_AWS_SECRET_KEY"  # Replace with your actual AWS Secret Key
region = "us-east-1"  # Replace with your desired AWS region

# Read text from file
text = read_text_from_file(file_path)

# Analyze text with AWS Comprehend (adjust the service type or prompt as needed)
result = analyze_text_with_aws(text, prompt, aws_access_key, aws_secret_key, region, service='comprehend')

# For SageMaker with a custom endpoint, uncomment the line below and replace with your endpoint name
# result = analyze_text_with_aws(text, prompt, aws_access_key, aws_secret_key, region, service='sagemaker', endpoint_name="YOUR_SAGEMAKER_ENDPOINT_NAME")

print("AWS AI Analysis Result:", result)
