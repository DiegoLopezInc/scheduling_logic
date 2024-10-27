import streamlit as st
from course_scheduler import CourseScheduler
from weekly_calendar import initialize_calendar_state, create_calendar, add_schedule_to_calendar, calculate_stress_level, display_stress_meter
import os

st.set_page_config(layout="wide")

st.title("Course Scheduler")

# Initialize session state
if 'step' not in st.session_state:
    st.session_state['step'] = 1

if 'scheduler' not in st.session_state:
    st.session_state['scheduler'] = None

if 'schedules' not in st.session_state:
    st.session_state['schedules'] = []

initialize_calendar_state()

# Step 1: Upload DegreeWorks PDF
if st.session_state['step'] == 1:
    st.header("Step 1: Upload Your DegreeWorks PDF")
    uploaded_file = st.file_uploader("Choose a file", type="pdf")
    if uploaded_file is not None:
        with open("temp_degreeworks.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())
        st.session_state['scheduler'] = CourseScheduler("temp_degreeworks.pdf")
        st.session_state['step'] = 2
        st.success("PDF uploaded successfully!")
        st.rerun()

# Step 2: Select credit hours
elif st.session_state['step'] == 2:
    st.header("Step 2: Select Desired Credit Hours")
    credit_hours = st.selectbox("How many credit hours do you want to take?", [12, 15, 18])
    st.session_state['desired_credits'] = credit_hours
    if st.button("Generate Schedules"):
        with st.spinner("Generating schedules..."):
            st.session_state['schedules'] = st.session_state['scheduler'].generate_schedules(desired_credits=credit_hours)
        st.success(f"Generated {len(st.session_state['schedules'])} schedules")
        st.session_state['step'] = 3
        st.rerun()

# Step 3: Display remaining courses and select a schedule
elif st.session_state['step'] == 3:
    st.header("Step 3: Review and Select a Schedule")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Remaining Courses")
        for course in st.session_state['scheduler'].still_needed_courses:
            if isinstance(course, str):
                st.write(f"• {course}")
            elif isinstance(course, dict) and course["type"] == "options":
                st.write(f"• Choose {course['num_to_pick']} from: {', '.join(course['courses'])}")

    with col2:
        st.subheader("Generated Schedules")
        num_schedules = len(st.session_state['schedules'])
        
        if num_schedules > 0:
            selected_schedule = st.selectbox(
                "Select a schedule to view details:",
                range(1, num_schedules + 1),
                format_func=lambda x: f"Schedule {x}"
            )
            
            schedule = st.session_state['schedules'][selected_schedule - 1]
            st.session_state['selected_schedule'] = selected_schedule - 1  # Store the selected schedule index
            total_credits = sum(course.credit_hours for course in schedule if course.credit_hours is not None)
            
            st.write(f"**Total Credits:** {total_credits}")
            for course in schedule:
                st.write(f"**{course.subject} {course.course_number}:** {course.title}")
                st.write(f"  Credits: {course.credit_hours}, Days: {course.days}, Time: {course.begin_time}-{course.end_time}")
            
            if st.button("Add to Calendar"):
                try:
                    add_schedule_to_calendar(schedule)
                    st.session_state['step'] = 4
                    st.success("Schedule added to calendar!")
                    st.rerun()
                except Exception as e:
                    st.error(f"An error occurred while adding the schedule to the calendar: {str(e)}")
        else:
            st.warning("No valid schedules could be generated. Please try adjusting your criteria or check your course data.")
            st.write("Debug information:")
            st.write(f"Total available courses: {len(st.session_state['scheduler'].available_courses)}")
            st.write(f"Desired credits: {st.session_state.get('desired_credits', 'Not set')}")
            if st.button("Go Back"):
                st.session_state['step'] = 2
                st.rerun()

# Step 4: Display calendar and stress meter
elif st.session_state['step'] == 4:
    st.header("Step 4: Your Schedule")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        try:
            if 'calendar' in st.session_state and st.session_state['calendar']['events']:
                calendar_component = create_calendar(st.session_state['calendar']['events'])
                if calendar_component is None:
                    st.error("Failed to create calendar component")
        except Exception as e:
            st.error(f"Error displaying calendar: {str(e)}")
    
    with col2:
        selected_schedule = st.session_state['schedules'][st.session_state.get('selected_schedule', 0)]
        display_stress_meter(selected_schedule, 'week')  # Default to week view

# Clean up temporary file
if os.path.exists("temp_degreeworks.pdf"):
    os.remove("temp_degreeworks.pdf")
