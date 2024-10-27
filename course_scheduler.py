from typing import List, Dict, Union
from collections import defaultdict
import itertools

from data_preprocessing import load_course_data, Course, get_available_courses
from degreeworks_pdf_parser import parse_degreeworks_pdf
from still_needed_courses_parser import parse_still_needed_courses

class CourseScheduler:
    def __init__(self, degreeworks_pdf_file: str):
        self.course_data = load_course_data()
        self.still_needed_courses = self._get_still_needed_courses(degreeworks_pdf_file)
        self.available_courses = self._get_available_courses()

    def _get_still_needed_courses(self, pdf_file: str) -> List[Union[str, Dict]]:
        pdf_result = parse_degreeworks_pdf(pdf_file)
        return pdf_result["still_needed_courses"]

    def _get_available_courses(self) -> Dict[str, List[Course]]:
        available_courses = defaultdict(list)
        print(f"Debug: Still needed courses: {self.still_needed_courses}")
        
        for course in self.still_needed_courses:
            if isinstance(course, str):
                course_code = course.replace(" ", "")
                if len(course_code) >= 7:
                    subject, number = course_code[:4], course_code[4:]
                    print(f"Debug: Searching for {subject} {number}")
                    sections = get_available_courses(self.course_data, [subject], [number])
                    print(f"Debug: Found {len(sections)} sections for {subject} {number}")
                    available_courses[course].extend(sections)
                else:
                    print(f"Debug: Invalid course format: {course}")
            elif isinstance(course, dict) and course["type"] == "options":
                for option in course["courses"]:
                    option_code = option.replace(" ", "")
                    if len(option_code) >= 7:
                        subject, number = option_code[:4], option_code[4:]
                        print(f"Debug: Searching for option {subject} {number}")
                        sections = get_available_courses(self.course_data, [subject], [number])
                        print(f"Debug: Found {len(sections)} sections for option {subject} {number}")
                        available_courses[option].extend(sections)
                    else:
                        print(f"Debug: Invalid course option format: {option}")
        
        total_available = sum(len(sections) for sections in available_courses.values())
        print(f"Debug: Total available courses: {total_available}")
        return available_courses

    def generate_schedules(self, desired_credits: int, max_schedules: int = 4) -> List[List[Course]]:
        all_courses = [course for courses in self.available_courses.values() for course in courses]
        
        print(f"Debug: Total available courses: {len(all_courses)}")
        print(f"Debug: Desired credits: {desired_credits}")
        
        credit_tolerance = 3  # Allow ±3 credits from the desired amount
        valid_schedules = []
        
        # Group courses by subject and course number
        course_groups = defaultdict(list)
        for course in all_courses:
            course_groups[(course.subject, course.course_number)].append(course)
        
        # Generate combinations using one course from each group
        unique_courses = [group[0] for group in course_groups.values()]
        
        for r in range(1, len(unique_courses) + 1):
            for combination in itertools.combinations(unique_courses, r):
                total_credits = sum(course.credit_hours for course in combination if course.credit_hours is not None)
                if desired_credits - credit_tolerance <= total_credits <= desired_credits + credit_tolerance:
                    if self._is_valid_schedule(combination):
                        valid_schedules.append(list(combination))
                        if len(valid_schedules) >= max_schedules:
                            break
            if len(valid_schedules) >= max_schedules:
                break
        
        print(f"Debug: Found {len(valid_schedules)} valid schedules")
        
        if not valid_schedules:
            print("Debug: No valid schedules generated. Reasons could be:")
            print(f"1. Not enough courses to reach {desired_credits} credits (±{credit_tolerance})")
            print("2. Required courses conflict with each other")
            print(f"3. No combination of courses falls within {desired_credits} ±{credit_tolerance} credits")
        
        return valid_schedules

    def _is_valid_schedule(self, schedule: List[Course]) -> bool:
        for i, course1 in enumerate(schedule):
            for course2 in schedule[i+1:]:
                if self._courses_overlap(course1, course2):
                    return False
        return True

    def _courses_overlap(self, course1: Course, course2: Course) -> bool:
        if not (course1.days and course2.days and course1.begin_time and course2.begin_time and course1.end_time and course2.end_time):
            return False

        days_overlap = any(day in course2.days for day in course1.days)
        if not days_overlap:
            return False

        time1 = (self._time_to_minutes(course1.begin_time), self._time_to_minutes(course1.end_time))
        time2 = (self._time_to_minutes(course2.begin_time), self._time_to_minutes(course2.end_time))

        return max(time1[0], time2[0]) < min(time1[1], time2[1])

    @staticmethod
    def _time_to_minutes(time_str: str) -> int:
        if not time_str:
            return 0
        try:
            # Handle 24-hour time format without colon
            if len(time_str) == 4:
                hours = int(time_str[:2])
                minutes = int(time_str[2:])
            else:
                hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except ValueError:
            print(f"Debug: Invalid time format: {time_str}")
            return 0

    def print_available_courses(self):
        for course, sections in self.available_courses.items():
            print(f"Course: {course}")
            for section in sections:
                print(f"  CRN: {section.crn}, Title: {section.title}, Days: {section.days}, Time: {section.begin_time}-{section.end_time}")
            print()

def main():
    scheduler = CourseScheduler("degreeworks_pdfs/rohan-salwekar-degreeworks.pdf")
    print("Available Courses:")
    scheduler.print_available_courses()
    desired_credits = 15  # Example: 15 credit hours
    schedules = scheduler.generate_schedules(desired_credits)
    print(f"\nGenerated {len(schedules)} possible schedules.")
    
    if schedules:
        print("\nExample schedules:")
        for i, schedule in enumerate(schedules, 1):
            print(f"\nSchedule {i}:")
            total_credits = sum(course.credit_hours for course in schedule if course.credit_hours is not None)
            print(f"Total Credits: {total_credits}")
            for course in schedule:
                print(f"{course.subject} {course.course_number}: {course.title} - Credits: {course.credit_hours}, Days: {course.days}, Time: {course.begin_time}-{course.end_time}")
    else:
        print("No valid schedules generated.")

if __name__ == "__main__":
    main()
