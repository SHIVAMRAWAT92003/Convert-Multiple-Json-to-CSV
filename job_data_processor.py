
import streamlit as st
import json
import re
import pandas as pd
from datetime import datetime 

class JobDataProcessor:

    """ calculate_days_posted"""
    def calculate_days_posted(self, posting_date):
        try:
            posting_date = datetime.strptime(posting_date, '%Y-%m-%d')  # Adjust format if needed
            current_date = datetime.now()
            delta = current_date - posting_date
            return delta.days
        except ValueError:
            return "Invalid Date"

        """ Define patterns or keywords to classify job posts"""
    def determine_classified_job_post(self, job_description):
        recruiter_keywords = ['recruiter','recruting', 'staffing agency', 'head hunter', 'placement agency']
        company_keywords = ['company', 'corporation', 'organization', 'firm']

        job_description_lower = job_description.lower()

        if any(keyword in job_description_lower for keyword in recruiter_keywords):
            return "Recruiter"
        elif any(keyword in job_description_lower for keyword in company_keywords):
            return "Company"
        return ""

        """ Define patterns or keywords related to travel requirements"""
    def check_travel_requirements(self, job_description):
        travel_keywords = ['travel required', 'willing to travel', 'traveling', 'travel', 'may require travel']
        job_description_lower = job_description.lower()
        
        if any(keyword in job_description_lower for keyword in travel_keywords):
            return "Yes"
        else:
            return "No"
    
    
    
    """Cleans and formats text by removing unwanted prefixes, patterns, and whitespace."""
    def clean_text(self, text, remove_prefix="", remove_patterns=[]):
        if text:
            if text.startswith(remove_prefix):
                text = text[len(remove_prefix):].strip()
            for pattern in remove_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s+', ' ', text.replace("\n", " "))
            text = re.sub(r'[^\w\s.,-]', '', text)
        return text
    
    
      
    """Formats a string to a more consistent and readable column name."""
    def format_column_name(self, name):
        if name in ["UG", "PG"]:
            return name
        name = re.sub(r's$', '', name)
        name = re.sub(r'\s+', '_', name).title()
        return name if not name.endswith('_') else name[:-1] + 's'
    
    """Removes the "UG " or "PG " prefix from a string if it exists."""
    def remove_ug_pg_prefix(self, text):
        if text.startswith(("UG ", "PG ")):
            return text[3:].strip()
        return text
    
    """Extracts the type of work (e.g., "Work From Home") from the benefits list."""
    def extract_work_type(self, benefits):
        if not benefits:
            return ""
        benefits_text = ' '.join(benefits).lower()

        if 'work from home' in benefits_text:
            return "Work From Home"
        elif 'work from office' in benefits_text:
            return "Work From Office"
        elif 'remote location' in benefits_text:
            return "Remote"
        else:
            return ""
    
    def __init__(self, json_data):
        self.json_data = json_data
        self.others = json_data.get("Others", [""])[0].split("\n")
        self.education_details = json_data.get("Education details", [""])[0].split("\n")
        self.job_description = self.clean_text(json_data.get("Job description", ""))
        self.benefits = json_data.get("Benefits", [])
        self.shift_timing = self.extract_shift_timing(self.job_description)
        self.work_type = self.extract_work_type(self.benefits)
        self.clean_benefits = self.filter_benefits(self.benefits)
        self.job_posting_date = self.clean_text(self.json_data.get("Job_posting_date", ""))
        self.days_posted = self.calculate_days_posted(self.job_posting_date)
        self.classified_job_post = self.determine_classified_job_post(self.job_description)
        self.travel_requirements = self.check_travel_requirements(self.job_description)



    """ Extracts the shift timing (e.g., "Morning", "Evening") from the job description."""
    def extract_shift_timing(self, job_description):
        if re.search(r'\bmorning\b', job_description, re.IGNORECASE):
            return "Morning"
        elif re.search(r'\bevening\b', job_description, re.IGNORECASE):
            return "Evening"
        elif re.search(r'\bnight\b', job_description, re.IGNORECASE):
            return "Night"
        else:
            return ""


    """Filters out any work type-related benefits from the list."""
    def filter_benefits(self, benefits):
        if not benefits:
            return ""

        work_types = ['work from home', 'work from office', 'remote']
        filtered_benefits = [b for b in benefits if not any(work_type in b.lower() for work_type in work_types)]
        return ', '.join(filtered_benefits)


    """ Converts the processed JSON data into a format suitable for CSV export."""
    def convert_json_to_csv(self):
        data = {
            "Title": self.clean_text(self.json_data.get("Title", "")),
            "Company name": self.clean_text(self.json_data.get("Company name", "")),
            "Work experience": self.clean_text(self.json_data.get("Work experience", "")),
            "Portal link": self.clean_text(self.json_data.get("Portal link", "")),
            "Job listing link": self.clean_text(self.json_data.get("job listing link", "")),
            "Company's Rating": self.clean_text(self.json_data.get("Company's Rating", "")),
            "No. of openings": self.clean_text(self.json_data.get("No. of openings", "")),
            "Applicants": self.clean_text(self.json_data.get("Applicants", "")),
            "Job Posting Date": self.clean_text(self.json_data.get("Job_posting_date", "")),
            "Minimum Salary": self.clean_text(self.json_data.get("Minimum salary", "")),
            "Maximum Salary": self.clean_text(self.json_data.get("Maximum salary", "")),
            "Average Salary": self.clean_text(self.json_data.get("Average salary", "")),
            "Benefits": self.clean_text(self.clean_benefits),
            "Work Type": self.work_type,
            "Role": self.clean_text(self.others[0].split(": ")[1] if len(self.others) > 0 and ": " in self.others[0] else ""),
            "Industry Type": self.clean_text(self.others[1].split(": ")[1] if len(self.others) > 1 and ": " in self.others[1] else ""),
            "Department": self.clean_text(self.others[2].split(": ")[1] if len(self.others) > 2 and ": " in self.others[2] else ""),
            "Employment Type": self.clean_text(self.others[3].split(": ")[1] if len(self.others) > 3 and ": " in self.others[3] else ""),
            "Role Category": self.clean_text(self.others[4].split(": ")[1] if len(self.others) > 4 and ": " in self.others[4] else ""),
            "UG": self.remove_ug_pg_prefix(self.clean_text(self.education_details[1] if len(self.education_details) > 1 else "")),
            "PG": self.remove_ug_pg_prefix(self.clean_text(self.education_details[2] if len(self.education_details) > 2 else "")),
            "Skills": self.clean_text(self.json_data.get("Skills", [""])[0].split("\n")[1] if self.json_data.get("Skills") else "",
                                      remove_patterns=["Key Skills", "Skills highlighted with \u2018\u2018 are preferred keyskills"]),
            "Shift Timing": self.shift_timing,
            "About company": self.clean_text(self.json_data.get("About company", ""), remove_prefix="About company"),
            "Job description": self.job_description,
            "Days Since Posting": self.days_posted,
            "Classified Job Post": self.classified_job_post,
            "Travel Requirements": self.travel_requirements,
            "About company": self.clean_text(self.json_data.get("About company", ""), remove_prefix="About company"),
            "Job description": self.job_description,
            
            
        }

        return {self.format_column_name(k): v for k, v in data.items()}


class JsonToCsvConverter:
    def __init__(self):
        self.all_data = []

    def process_files(self, uploaded_files):
        for uploaded_file in uploaded_files:
            try:
                uploaded_file.seek(0)  
                json_data = json.load(uploaded_file)
                cleaner = JobDataProcessor(json_data)
                csv_data = cleaner.convert_json_to_csv()
                self.all_data.append(csv_data)
            except (json.JSONDecodeError, Exception) as e:
                st.error(f"An error occurred: {e}")

    def download_csv(self):
        if self.all_data:
            df = pd.DataFrame(self.all_data)
            st.download_button(
                label="Download Output CSV",
                data=df.to_csv(index=False),
                file_name="output_data.csv",
                mime="text/csv"
            )


def main():
    st.title("Convert mutliple json files to CSV file :(JobDataProcessor)")
    uploaded_files = st.file_uploader("Upload JSON files", type="json", accept_multiple_files=True)

    if uploaded_files:
        converter = JsonToCsvConverter()
        converter.process_files(uploaded_files)
        converter.download_csv()


if __name__ == "__main__":
    main()
    



