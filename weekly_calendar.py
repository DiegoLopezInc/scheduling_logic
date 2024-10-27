import streamlit as st
import streamlit_shadcn_ui as ui
from streamlit_calendar import calendar
import randomcolor
from datetime import datetime, timedelta
from collections import defaultdict

def initialize_calendar_state():
    """Initialize all calendar-related session state variables"""
    if 'calendar' not in st.session_state:
        st.session_state['calendar'] = {
            'events': [],
            'options': {
                'initialView': 'timeGridWeek',
                'headerToolbar': {
                    'left': 'prev,next today',
                    'center': 'title',
                    'right': 'dayGridMonth,timeGridWeek,timeGridDay'
                },
                'slotMinTime': '08:00:00',
                'slotMaxTime': '20:00:00',
                'height': 650,
                'initialDate': datetime.now().strftime("%Y-%m-%d"),  # Set to today's date
                'nowIndicator': True,  # Show current time indicator
                'scrollTime': datetime.now().strftime("%H:%M:%S"),  # Scroll to current time
            }
        }
    return st.session_state['calendar']

def format_time(time_str):
    """Format time string to ensure it's in HH:MM:SS format"""
    if not time_str or time_str == "None":
        return None
    try:
        if len(time_str) == 4:  # Format like "1330"
            return f"{time_str[:2]}:{time_str[2:]}:00"
        elif len(time_str.split(':')) == 2:  # Format like "13:30"
            return f"{time_str}:00"
        elif len(time_str.split(':')) == 3:  # Already in HH:MM:SS format
            return time_str
        else:
            return None
    except:
        return None

def normalize_credit_hours(course):
    """Normalize credit hours, setting None or 0 to 3"""
    if not course.credit_hours or course.credit_hours == 0:
        course.credit_hours = 3
    return course

def add_schedule_to_calendar(schedule):
    if 'calendar' not in st.session_state:
        initialize_calendar_state()
    
    # Clear existing events
    st.session_state['calendar']['events'] = []
    
    # Get current date and find the next occurrence of each day
    current_date = datetime.now()
    
    # Normalize credit hours for each course
    schedule = [normalize_credit_hours(course) for course in schedule]
    
    for course in schedule:
        # Skip courses without time information
        if not course.begin_time or not course.end_time or course.begin_time == "None" or course.end_time == "None":
            st.warning(f"⚠️ Course {course.subject} {course.course_number} does not have scheduled times and will not appear on the calendar.")
            continue
            
        try:
            course_color = get_random_color()
            begin_time = format_time(course.begin_time)
            end_time = format_time(course.end_time)
            
            # Validate time format
            if not (begin_time and end_time):
                st.warning(f"⚠️ Invalid time format for {course.subject} {course.course_number}")
                continue
            
            # Create events for each day the course meets
            for day in course.days:
                # Calculate the next occurrence of this day
                day_number = {'M': 0, 'T': 1, 'W': 2, 'R': 3, 'F': 4}[day]
                days_ahead = day_number - current_date.weekday()
                if days_ahead < 0:  # If the day has passed this week
                    days_ahead += 7
                next_date = current_date + timedelta(days=days_ahead)
                
                # Create recurring events for the semester
                semester_end = datetime(2024, 12, 13)  # Adjust end date as needed
                course_date = next_date
                
                while course_date <= semester_end:
                    event = {
                        'title': f"{course.subject} {course.course_number}",
                        'start': course_date.strftime("%Y-%m-%d") + f"T{begin_time}",
                        'end': course_date.strftime("%Y-%m-%d") + f"T{end_time}",
                        'color': course_color,
                        'textColor': 'white',
                        'borderColor': 'rgba(0,0,0,0.2)',
                        'extendedProps': {
                            'credits': course.credit_hours,
                            'description': course.title or "No description available"
                        }
                    }
                    st.session_state['calendar']['events'].append(event)
                    course_date += timedelta(days=7)  # Move to next week
        except Exception as e:
            st.warning(f"⚠️ Could not add {course.subject} {course.course_number} to calendar: {str(e)}")

def create_calendar(events):
    """Create and return a calendar component with the given events"""
    calendar_options = {
        'initialView': 'timeGridWeek',
        'headerToolbar': {
            'left': 'prev,next today',
            'center': 'title',
            'right': 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        'slotMinTime': '08:00:00',
        'slotMaxTime': '20:00:00',
        'height': 650,
        'initialDate': datetime.now().strftime("%Y-%m-%d"),
        'nowIndicator': True,
        'scrollTime': datetime.now().strftime("%H:%M:%S"),
        'events': events
    }
    
    # Create a stable key based on events content
    stable_key = "calendar"
    if events:
        # Use the number of events and first event's title as part of the key
        stable_key = f"calendar_{len(events)}_{events[0].get('title', '')}"
    
    try:
        return calendar(
            events=events,
            options=calendar_options,
            key=stable_key
        )
    except Exception as e:
        st.error(f"Error creating calendar: {str(e)}")
        return None

def day_to_number(day):
    return {'M': 0, 'T': 1, 'W': 2, 'R': 3, 'F': 4}[day]

def get_random_color():
    return randomcolor.RandomColor().generate()[0]

def analyze_schedule_distribution(schedule):
    """Analyze the distribution of classes across days and times"""
    daily_load = defaultdict(int)
    time_blocks = defaultdict(int)
    total_hours = 0
    
    for course in schedule:
        # Skip courses without time information for time-based calculations
        if not course.begin_time or not course.end_time or course.begin_time == "None" or course.end_time == "None":
            # Still count the credits for daily load if days are available
            if course.days:
                for day in course.days:
                    daily_load[day] += course.credit_hours or 3
            continue
            
        # Calculate daily course load
        for day in course.days:
            daily_load[day] += course.credit_hours or 3
        
        try:
            # Calculate time block distribution
            begin_time = format_time(course.begin_time)
            end_time = format_time(course.end_time)
            
            if begin_time and end_time:
                begin_hour = int(begin_time.split(':')[0])
                end_hour = int(end_time.split(':')[0])
                duration = end_hour - begin_hour
                total_hours += duration * len(course.days)
                
                for hour in range(begin_hour, end_hour):
                    time_block = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
                    time_blocks[time_block] += 1
        except:
            continue

    return {
        'daily_load': daily_load,
        'time_blocks': time_blocks,
        'total_hours': total_hours
    }

def calculate_stress_level(schedule, view_type='week'):
    """Calculate stress level based on schedule distribution and view type"""
    analysis = analyze_schedule_distribution(schedule)
    
    # Normalize credit hours
    normalized_schedule = [normalize_credit_hours(course) for course in schedule]
    total_credits = sum(course.credit_hours for course in normalized_schedule)
    
    # Base stress calculations
    credit_stress = (total_credits / 18) * 100  # Credit hours stress
    
    # Daily distribution stress
    max_daily_load = max(analysis['daily_load'].values()) if analysis['daily_load'] else 0
    daily_stress = (max_daily_load / 9) * 100  # Assuming 9 credits per day is maximum
    
    # Time block distribution stress
    time_block_stress = max(analysis['time_blocks'].values()) / 3 * 100  # Stress from concentrated classes
    
    # Calculate view-specific stress
    if view_type == 'day':
        # For day view, emphasize that day's specific load
        today = datetime.now().strftime('%a')
        day_map = {'Mon': 'M', 'Tue': 'T', 'Wed': 'W', 'Thu': 'R', 'Fri': 'F'}
        today_load = analysis['daily_load'].get(day_map.get(today, 'M'), 0)
        stress_level = (today_load / 9) * 100
    elif view_type == 'week':
        # For week view, balance daily distribution and total load
        stress_level = (credit_stress * 0.4 + daily_stress * 0.4 + time_block_stress * 0.2)
    else:  # month view
        # For month view, emphasize total credit load and distribution
        stress_level = (credit_stress * 0.6 + daily_stress * 0.2 + time_block_stress * 0.2)
    
    return min(stress_level, 100)  # Cap at 100%

def display_stress_meter(schedule, view_type='week'):
    """Display stress meter with detailed analysis"""
    analysis = analyze_schedule_distribution(schedule)
    stress_level = calculate_stress_level(schedule, view_type)
    
    st.subheader("Schedule Analysis")
    
    # Display stress meter
    st.write("**Overall Stress Level**")
    # Convert percentage to decimal (0-1 range)
    st.progress(stress_level / 100)
    st.write(f"Stress Level: {stress_level:.1f}%")
    
    # Display daily distribution
    st.write("\n**Daily Course Load**")
    days = {'M': 'Monday', 'T': 'Tuesday', 'W': 'Wednesday', 'R': 'Thursday', 'F': 'Friday'}
    for day, load in analysis['daily_load'].items():
        st.write(f"{days[day]}: {load} credit hours")
    
    # Display time block distribution
    st.write("\n**Time Distribution**")
    for block, count in analysis['time_blocks'].items():
        st.write(f"{block.title()}: {count} classes")
    
    # Display stress level interpretation
    st.write("\n**Schedule Assessment**")
    if stress_level < 33:
        st.write("🟢 Low stress level. This schedule appears well-balanced.")
    elif stress_level < 66:
        st.write("🟡 Moderate stress level. Be prepared for some challenging days.")
    else:
        st.write("🔴 High stress level. Consider redistributing your course load.")

    # View-specific advice
    if view_type == 'day':
        st.write("\n**Daily Tips**")
        st.write("- Plan breaks between classes")
        st.write("- Consider your energy levels throughout the day")
    elif view_type == 'week':
        st.write("\n**Weekly Management Tips**")
        st.write("- Balance study time across the week")
        st.write("- Plan ahead for heavy course load days")
    else:
        st.write("\n**Long-term Planning Tips**")
        st.write("- Consider your semester workload distribution")
        st.write("- Plan for major assignments and exams")
