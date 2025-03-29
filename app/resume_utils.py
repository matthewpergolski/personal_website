import yaml
import os
from pathlib import Path

def load_resume_data():
    """
    Load resume data from YAML file.
    Returns a dictionary with the resume data.
    """
    data_dir = Path(__file__).parent / 'data'
    resume_file = data_dir / 'resume_data.yaml'
    
    if not resume_file.exists():
        print(f"Warning: Resume data file not found at {resume_file}")
        return {}
    
    try:
        with open(resume_file, 'r') as file:
            resume_data = yaml.safe_load(file)
        return resume_data
    except Exception as e:
        print(f"Error loading resume data: {e}")
        return {}

def extract_pdf_text(pdf_path):
    """
    Extract text from a PDF file.
    This would be used for direct PDF parsing, but requires additional libraries.
    """
    # This is a placeholder. To actually implement PDF parsing,
    # you would need to install and use a library like PyPDF2, pdfminer, or pdfplumber
    try:
        # Placeholder for PDF parsing code
        # Actual implementation would use a library to extract text
        text = "PDF parsing not implemented. Please use the YAML file for resume data."
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""

def get_resume_data():
    """
    Get resume data, either from YAML or fallback to placeholder.
    This is the main function that should be used by routes.
    """
    data = load_resume_data()
    
    # If data is empty or missing key sections, return placeholder data
    if not data or not all(key in data for key in ['personal_info', 'experience', 'education']):
        return get_placeholder_data()
    
    return data

def get_placeholder_data():
    """
    Return placeholder data for testing/demo purposes.
    This is only used if the YAML file is not found or incomplete.
    """
    return {
        "personal_info": {
            "name": "Matthew Pergolski",
            "title": "Data Scientist & Machine Learning Engineer",
            "contact": {
                "email": "example@example.com",
                "github": "github.com/example",
                "location": "City, State"
            }
        },
        "education": [
            {
                "degree": "M.S. Data Science",
                "institution": "Example University",
                "years": "2019-2021"
            },
            {
                "degree": "B.S. Computer Science",
                "institution": "Example University",
                "years": "2015-2019"
            }
        ],
        "experience": [
            {
                "title": "Senior Data Scientist",
                "company": "Example Company",
                "period": "2021-Present",
                "description": "Led development of machine learning models.",
                "achievements": [
                    "Improved model accuracy by 15%",
                    "Reduced false positives by 30%",
                    "Implemented CI/CD pipelines"
                ]
            }
        ]
    } 