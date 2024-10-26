import pandas as pd

# Load the dataset
file_path = 'ecg_dataset/ptbxl_database.csv'  # replace with actual path
df = pd.read_csv(file_path)

# Find unique labels in the "report" column
unique_reports = df['report'].unique()
num_unique_reports = len(unique_reports)

# Display the results
print(f"Number of unique labels in 'report' column: {num_unique_reports}")
