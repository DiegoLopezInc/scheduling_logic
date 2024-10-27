import json
import os
from typing import List, Dict, Union
from collections import defaultdict

class Course:
    def __init__(self, data: Dict):
        self.crn = data.get('courseReferenceNumber')
        self.subject = data.get('subject')
        self.course_number = data.get('courseNumber')
        self.title = data.get('courseTitle')
        self.credit_hours = data.get('creditHours')
        self.meetings = data.get('meetingsFaculty', [])
        
        if self.meetings and len(self.meetings) > 0:
            meeting = self.meetings[0].get('meetingTime', {})
            self.begin_time = meeting.get('beginTime')
            self.end_time = meeting.get('endTime')
            self.building = meeting.get('building')
            self.room = meeting.get('room')
            self.days = self._get_meeting_days(meeting)
            self.start_date = meeting.get('startDate')
            self.end_date = meeting.get('endDate')
        else:
            self.begin_time = self.end_time = self.building = self.room = self.days = self.start_date = self.end_date = None

        # print(f"Debug: Created Course object:")
        # print(f"  CRN: {self.crn}")
        # print(f"  Subject: {self.subject}")
        # print(f"  Course Number: {self.course_number}")
        # print(f"  Title: {self.title}")
        # print(f"  Credit Hours: {self.credit_hours}")
        # print(f"  Begin Time: {self.begin_time}")
        # print(f"  End Time: {self.end_time}")
        # print(f"  Days: {self.days}")

    def _get_meeting_days(self, meeting):
        days = []
        if meeting.get('monday'): days.append('M')
        if meeting.get('tuesday'): days.append('T')
        if meeting.get('wednesday'): days.append('W')
        if meeting.get('thursday'): days.append('R')
        if meeting.get('friday'): days.append('F')
        if meeting.get('saturday'): days.append('S')
        if meeting.get('sunday'): days.append('U')
        return ''.join(days)

def load_course_data() -> Dict[str, Dict[str, List[Course]]]:
    data = []
    directory = 'all_courses'
    
    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist.")
        return {}

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                if isinstance(json_data, dict) and 'data' in json_data:
                    data.extend(json_data['data'])
    
    # print(f"Debug: Loaded {len(data)} courses from JSON files")

    course_dict = defaultdict(lambda: defaultdict(list))
    for course_data in data:
        course = Course(course_data)
        if course.subject and course.course_number:
            course_dict[course.subject][course.course_number].append(course)
        # else:
        #     print(f"Debug: Invalid course data: Subject={course.subject}, Number={course.course_number}")
    
    # print(f"Debug: Processed {len(course_dict)} subjects")
    # for subject, numbers in course_dict.items():
    #     print(f"Debug: Subject {subject} has {len(numbers)} course numbers")

    return course_dict

def get_available_courses(course_data: Dict[str, Dict[str, List[Course]]], subjects: List[str], course_numbers: List[str]) -> List[Course]:
    available_courses = []
    for subject, course_number in zip(subjects, course_numbers):
        # print(f"Debug: Searching for {subject} {course_number}")
        if subject in course_data:
            if course_number in course_data[subject]:
                courses = course_data[subject][course_number]
                available_courses.extend(courses)
                # print(f"Debug: Found {len(courses)} courses for {subject} {course_number}")
            # else:
            #     print(f"Debug: Course number {course_number} not found for subject {subject}")
            #     print(f"Debug: Available course numbers for {subject}: {', '.join(course_data[subject].keys())}")
        # else:
        #     print(f"Debug: Subject {subject} not found in course data")
    
    # print(f"Debug: Total found {len(available_courses)} courses")
    return available_courses

def generate_schedules(eligible_courses: List[Course], max_credits: int) -> List[List[Course]]:
    # Implement scheduling algorithm to generate possible schedules
    pass

def main():
    course_data = load_course_data()
    
    # print("\nDebug: Course data structure:")
    # for subject, numbers in course_data.items():
    #     print(f"Subject: {subject}")
    #     for number, courses in numbers.items():
    #         print(f"  Number: {number}")
    #         for course in courses:
    #             print(f"    CRN: {course.crn}, Title: {course.title}, Days: {course.days}, Time: {course.begin_time}-{course.end_time}")
    
    # Example usage
    subject = "PSYC"  # Example subject
    course_number = "1101"  # Example course number
    
    available_courses = get_available_courses(course_data, [subject], [course_number])
    print(f"\nFound {len(available_courses)} section(s) for {subject} {course_number}:")
    for course in available_courses:
        print(f"  CRN: {course.crn}, Title: {course.title}, Days: {course.days}, Time: {course.begin_time}-{course.end_time}")

if __name__ == "__main__":
    main()
