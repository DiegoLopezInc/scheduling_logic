import re

class DegreeWorksPDFParser:
    def __init__(self, text):
        self.text = text
        self.major_headers = {}
        self.current_major = None

    def parse(self):
        self.extract_major_headers()
        return self.extract_still_needed_courses()

    def extract_major_headers(self):
        major_pattern = re.compile(r"(General Education|Major.*?|Concentration.*?|Minor.*?) (INCOMPLETE|COMPLETE)", re.IGNORECASE)
        still_needed_pattern = re.compile(r"Still needed:\s*(.*)")

        for line in self.text.splitlines():
            line = line.strip()

            major_match = major_pattern.match(line)
            if major_match:
                self.current_major = major_match.group(1).strip()

            needed_match = still_needed_pattern.match(line)
            if needed_match and self.current_major:
                requirement_name = needed_match.group(1).strip()
                self.major_headers[requirement_name] = self.current_major

    def extract_still_needed_courses(self):
        still_needed_courses = []
        needed_pattern = re.compile(r"Still needed:.*?(?=\n\n|\Z)", re.DOTALL)
        course_code_pattern = re.compile(r"([A-Z]{4}\s*\d{4})")

        for block in needed_pattern.findall(self.text):
            course_codes = course_code_pattern.findall(block)
            for code in course_codes:
                still_needed_courses.append(code.replace(" ", ""))

        return list(dict.fromkeys(still_needed_courses))

def parse_still_needed_courses(still_needed_text):
    courses = []
    lines = still_needed_text.split('\n')

    print("Debug: Parsing still needed courses")
    print(f"Debug: Input text:\n{still_needed_text}")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        print(f"Debug: Processing line: {line}")

        # Extract course codes (assuming they are in the format of 4 letters followed by 4 numbers)
        course_matches = re.findall(r'\b([A-Z]{4}\s*\d{4})\b', line)
        
        if len(course_matches) > 1:
            # Extract the number of courses to pick
            num_to_pick = re.search(r'(\d+)\s*(?:Class|Classes)', line)
            if num_to_pick:
                num_to_pick = int(num_to_pick.group(1))
            else:
                num_to_pick = 1  # Default to 1 if not specified
            
            options = [course.replace(" ", "") for course in course_matches]
            course_entry = {
                "type": "options",
                "num_to_pick": num_to_pick,
                "courses": options
            }
            courses.append(course_entry)
            print(f"Debug: Added course options: {course_entry}")
        elif len(course_matches) == 1:
            course = course_matches[0].replace(" ", "")
            courses.append(course)
            print(f"Debug: Added single course: {course}")
        else:
            # If no course codes found, add the entire line as a requirement
            courses.append(line)
            print(f"Debug: Added requirement: {line}")

    print(f"Debug: Final courses list: {courses}")
    return courses

# Example usage
if __name__ == "__main__":
    sample_text = """
    Still needed: 3 Classes in MATH 1001, MATH 1002, MATH 1003
    Still needed: PHYS 2001
    Still needed: 2 Classes in CHEM 3001, CHEM 3002, CHEM 3003, CHEM 3004
    Still needed: 1 Class in BIOL 4001
    Still needed: 120 credit hours are required. You have 104, you need 16 more credits
    """
    result = parse_still_needed_courses(sample_text)
    print("Parsed courses:")
    print(result)
