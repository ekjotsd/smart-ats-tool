import os
import pandas as pd
import kaggle
from dotenv import load_dotenv

load_dotenv()

def download_kaggle_dataset(dataset_name, output_path):
    """Download dataset from Kaggle"""
    os.makedirs(output_path, exist_ok=True)
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(
        dataset_name,
        path=output_path,
        unzip=True
    )

def process_dataset(input_file, output_file):
    """Process the dataset to keep only job title and description"""
    df = pd.read_csv(input_file)
    
    # Rename columns if needed and keep only relevant ones
    if 'job_title' in df.columns and 'job_description' in df.columns:
        df = df.rename(columns={
            'job_title': 'Job Title',
            'job_description': 'Job Description'
        })
    
    # Select only needed columns
    if 'Job Title' in df.columns and 'Job Description' in df.columns:
        df = df[['Job Title', 'Job Description']]
    
    # Drop rows with missing values
    df = df.dropna()
    
    # Save processed dataset
    df.to_csv(output_file, index=False)
    print(f"Processed dataset saved to {output_file}")

if __name__ == "__main__":
    dataset_name = "kshitizregmi/jobs-and-job-description"
    
    # Resolve absolute path for data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "..", "data")
    output_path = os.path.abspath(output_path)
    
    # Download dataset
    download_kaggle_dataset(dataset_name, output_path)
    
    # Process dataset (adjust filenames as needed)
    input_file = os.path.join(output_path, "job_title_des.csv")
    output_file = os.path.join(output_path, "job_descriptions.csv")
    process_dataset(input_file, output_file)