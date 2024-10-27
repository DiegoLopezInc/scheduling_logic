import pdfplumber
import re
from still_needed_courses_parser import parse_still_needed_courses

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def parse_degreeworks_pdf(pdf_path):
    full_text = extract_text_from_pdf(pdf_path)
    
    #print("Debug: Full text extracted from PDF")
    #print(f"Debug: Full text length: {len(full_text)}")
    
    # Extract the "Still Needed" sections
    still_needed_matches = re.findall(r'Still needed:\s*(\d+.*?)(?:\n|$)', full_text, re.IGNORECASE | re.MULTILINE)
    
    if still_needed_matches:
        #print("Debug: Found 'Still Needed' sections")
        #for match in still_needed_matches:
            #print(f"Debug: Still Needed text: {match}")
        
        still_needed_text = "\n".join(still_needed_matches)
        still_needed_courses = parse_still_needed_courses(still_needed_text)
    else:
        #print("Debug: 'Still Needed' sections not found")
        still_needed_courses = []

    #print(f"Debug: Parsed still needed courses: {still_needed_courses}")

    return {
        "full_text": full_text,
        "still_needed_courses": still_needed_courses
    }

# Example usage
# if __name__ == "__main__":
#     pdf_path = "degreeworks_pdfs/rohan-salwekar-degreeworks.pdf"
#     result = parse_degreeworks_pdf(pdf_path)
#     print("\nFinal Results:")
#     print("Full Text Length:", len(result["full_text"]))
#     # print the full text to a csv file
#     with open("full_text.csv", "w") as file:
#         file.write(result["full_text"])
#     print("Still Needed Courses:", result["still_needed_courses"])
