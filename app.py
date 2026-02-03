"""
St. Louis Ambush FC - Tryout Check-In System
A Streamlit app for managing player registration, waivers, and data collection
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
import pandas as pd
from datetime import datetime, date
import json
import gspread
from google.oauth2.service_account import Credentials
import io
import base64
from PIL import Image
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Ambush Tryout Check-In",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better mobile experience and branding
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .main-header h1 {
        color: #f4d03f;
        margin: 0;
    }
    .main-header p {
        color: #ffffff;
        margin: 5px 0 0 0;
    }
    .section-header {
        background-color: #1a1a2e;
        color: #f4d03f;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 20px 0 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .tryout-number {
        font-size: 72px;
        font-weight: bold;
        color: #1a1a2e;
    }
    .waiver-text {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        height: 300px;
        overflow-y: scroll;
        font-size: 12px;
        border: 1px solid #dee2e6;
    }
    .stButton > button {
        background-color: #1a1a2e;
        color: #f4d03f;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #f4d03f;
        color: #1a1a2e;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'registration'
if 'player_data' not in st.session_state:
    st.session_state.player_data = {}
if 'tryout_number' not in st.session_state:
    st.session_state.tryout_number = None
if 'signature_data' not in st.session_state:
    st.session_state.signature_data = None

# Waiver text
WAIVER_TEXT = """
ST. LOUIS AMBUSH FC - TRYOUT WAIVER AND RELEASE OF LIABILITY

Date: February 28, 2025

PLEASE READ CAREFULLY BEFORE SIGNING

1. ASSUMPTION OF RISK
I understand that participating in the St. Louis Ambush FC tryout involves physical activities that carry inherent risks of injury. These activities include, but are not limited to: running, jumping, kicking, heading the ball, physical contact with other players, and other soccer-related movements. I voluntarily assume all risks associated with my participation, including but not limited to: sprains, strains, fractures, concussions, and other injuries that may result from participation.

2. RELEASE AND WAIVER OF LIABILITY
In consideration of being permitted to participate in the St. Louis Ambush FC tryout, I hereby release, waive, discharge, and covenant not to sue St. Louis Ambush FC, its owners, officers, directors, employees, agents, coaches, volunteers, and affiliates (collectively, the "Released Parties") from any and all liability, claims, demands, actions, or causes of action whatsoever arising out of or related to any loss, damage, or injury, including death, that may be sustained by me while participating in the tryout or while on the premises where the tryout is being conducted.

3. MEDICAL AUTHORIZATION
I authorize the Released Parties to seek and obtain emergency medical treatment for me if necessary during my participation in the tryout. I understand that I am responsible for any medical expenses incurred as a result of such treatment.

4. PHOTO/VIDEO RELEASE
I grant St. Louis Ambush FC and its affiliates the right to use my name, likeness, image, and/or voice in any photographs, video recordings, or other media taken during the tryout for promotional, advertising, or any other lawful purposes without compensation.

5. ELIGIBILITY CONFIRMATION
I confirm that I am not currently under contract with any professional soccer team that would prevent my participation in this tryout. I confirm that all information provided during registration is accurate and complete.

6. PHYSICAL FITNESS
I certify that I am physically fit and have no medical conditions that would prevent my safe participation in the tryout. I have disclosed any relevant medical conditions or injuries in my registration.

7. RULES AND CONDUCT
I agree to abide by all rules and regulations set forth by St. Louis Ambush FC and to conduct myself in a sportsmanlike manner throughout the tryout.

8. ACKNOWLEDGMENT
I HAVE READ THIS WAIVER AND RELEASE OF LIABILITY, FULLY UNDERSTAND ITS TERMS, AND UNDERSTAND THAT I AM GIVING UP SUBSTANTIAL RIGHTS, INCLUDING MY RIGHT TO SUE. I ACKNOWLEDGE THAT I AM SIGNING THIS AGREEMENT FREELY AND VOLUNTARILY, AND INTEND MY SIGNATURE TO BE A COMPLETE AND UNCONDITIONAL RELEASE OF ALL LIABILITY TO THE GREATEST EXTENT ALLOWED BY LAW.

By signing below, I acknowledge that I have read, understand, and agree to the terms of this waiver.
"""

def get_next_tryout_number():
    """Get the next available tryout number (would integrate with Google Sheets in production)"""
    # In production, this would query the Google Sheet to find the next number
    # For now, using session state or a simple counter
    if 'current_tryout_counter' not in st.session_state:
        st.session_state.current_tryout_counter = 1
    
    number = st.session_state.current_tryout_counter
    st.session_state.current_tryout_counter += 1
    return number

def save_signature_as_base64(canvas_result):
    """Convert canvas signature to base64 string for storage"""
    if canvas_result.image_data is not None:
        img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    return None

def connect_to_google_sheets(credentials_dict):
    """Connect to Google Sheets using service account credentials"""
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
    client = gspread.authorize(credentials)
    return client

def save_to_google_sheets(player_data, signature_base64, sheet_url=None):
    """Save player data to Google Sheets"""
    # Check if credentials are configured
    if 'gcp_credentials' not in st.secrets:
        st.warning("Google Sheets integration not configured. Data saved locally only.")
        return False
    
    try:
        client = connect_to_google_sheets(st.secrets['gcp_credentials'])
        
        # Open the spreadsheet (you'd set this in secrets or config)
        if sheet_url:
            sheet = client.open_by_url(sheet_url)
        else:
            sheet = client.open(st.secrets.get('sheet_name', 'Ambush Tryout 2025'))
        
        worksheet = sheet.sheet1
        
        # Prepare row data
        row = [
            player_data.get('tryout_number', ''),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            player_data.get('first_name', ''),
            player_data.get('last_name', ''),
            player_data.get('preferred_name', ''),
            player_data.get('dob', ''),
            player_data.get('email', ''),
            player_data.get('phone', ''),
            player_data.get('city', ''),
            player_data.get('state', ''),
            player_data.get('emergency_contact_name', ''),
            player_data.get('emergency_contact_phone', ''),
            player_data.get('primary_position', ''),
            player_data.get('secondary_position', ''),
            player_data.get('dominant_foot', ''),
            player_data.get('height', ''),
            player_data.get('weight', ''),
            player_data.get('jersey_size', ''),
            player_data.get('outdoor_experience', ''),
            player_data.get('indoor_experience', ''),
            player_data.get('highest_level', ''),
            player_data.get('current_team', ''),
            player_data.get('college', ''),
            player_data.get('masl_experience', ''),
            player_data.get('notable_achievements', ''),
            player_data.get('video_link', ''),
            player_data.get('how_heard', ''),
            player_data.get('under_contract', ''),
            player_data.get('us_work_eligible', ''),
            player_data.get('medical_conditions', ''),
            'Yes' if signature_base64 else 'No',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            player_data.get('fee_paid', 'No'),
        ]
        
        worksheet.append_row(row)
        return True
        
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {str(e)}")
        return False

def render_header():
    """Render the app header"""
    st.markdown("""
    <div class="main-header">
        <h1>⚽ ST. LOUIS AMBUSH FC</h1>
        <p>2025 Open Tryout Registration</p>
        <p style="font-size: 14px;">February 28, 2025</p>
    </div>
    """, unsafe_allow_html=True)

def render_registration_page():
    """Render the player registration form"""
    render_header()
    
    st.markdown('<div class="section-header"><h3>📋 Player Information</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        first_name = st.text_input("First Name *", key="first_name")
        preferred_name = st.text_input("Preferred Name/Nickname", key="preferred_name", 
                                       help="Name for jersey or announcements")
        email = st.text_input("Email Address *", key="email")
        city = st.text_input("City *", key="city")
        
    with col2:
        last_name = st.text_input("Last Name *", key="last_name")
        dob = st.date_input("Date of Birth *", 
                           min_value=date(1970, 1, 1),
                           max_value=date(2010, 1, 1),
                           value=date(1995, 1, 1),
                           key="dob")
        phone = st.text_input("Phone Number *", key="phone")
        state = st.selectbox("State *", 
                            ["", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                             "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                             "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                             "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                             "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
                            key="state")
    
    st.markdown('<div class="section-header"><h3>🚨 Emergency Contact</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        emergency_name = st.text_input("Emergency Contact Name *", key="emergency_name")
    with col2:
        emergency_phone = st.text_input("Emergency Contact Phone *", key="emergency_phone")
    
    st.markdown('<div class="section-header"><h3>⚽ Soccer Background</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        primary_position = st.selectbox("Primary Position *",
                                        ["", "Goalkeeper", "Defender", "Midfielder", "Forward/Striker"],
                                        key="primary_position")
        dominant_foot = st.selectbox("Dominant Foot *",
                                     ["", "Right", "Left", "Both"],
                                     key="dominant_foot")
        outdoor_exp = st.selectbox("Years Outdoor Experience *",
                                   ["", "0-2", "3-5", "6-10", "10+"],
                                   key="outdoor_exp")
    
    with col2:
        secondary_position = st.selectbox("Secondary Position",
                                          ["", "Goalkeeper", "Defender", "Midfielder", "Forward/Striker", "N/A"],
                                          key="secondary_position")
        height = st.text_input("Height (e.g., 5'10\")", key="height")
        indoor_exp = st.selectbox("Years Indoor/Arena Experience *",
                                  ["", "None", "0-2", "3-5", "6-10", "10+"],
                                  key="indoor_exp")
    
    with col3:
        jersey_size = st.selectbox("Jersey Size",
                                   ["", "S", "M", "L", "XL", "2XL", "3XL"],
                                   key="jersey_size")
        weight = st.text_input("Weight (lbs)", key="weight")
        highest_level = st.selectbox("Highest Level Played *",
                                     ["", "Recreational", "High School", "Club/Academy", 
                                      "College (D3/NAIA)", "College (D2)", "College (D1)",
                                      "Semi-Pro/Amateur", "Professional"],
                                     key="highest_level")
    
    col1, col2 = st.columns(2)
    with col1:
        current_team = st.text_input("Current Team/Club (if any)", key="current_team")
        college = st.text_input("College/University (if applicable)", key="college")
    with col2:
        masl_experience = st.text_input("Previous MASL/Arena Soccer Teams", key="masl_experience",
                                        help="List any previous MASL or arena soccer teams")
        notable = st.text_area("Notable Achievements/Teams", key="notable", height=68,
                              help="Awards, championships, notable teams played for")
    
    video_link = st.text_input("Video/Highlight Link", key="video_link",
                               help="YouTube, Vimeo, Hudl, or other video platform link")
    
    st.markdown('<div class="section-header"><h3>📝 Additional Information</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        how_heard = st.selectbox("How did you hear about this tryout? *",
                                 ["", "Social Media", "Team Website", "Friend/Player Referral",
                                  "Coach Referral", "News/Media", "Previous Tryout", "Other"],
                                 key="how_heard")
        under_contract = st.radio("Are you currently under contract with any team?",
                                  ["No", "Yes"],
                                  key="under_contract",
                                  horizontal=True)
    
    with col2:
        us_eligible = st.radio("Are you eligible to work in the US?",
                               ["Yes", "No"],
                               key="us_eligible",
                               horizontal=True)
        fee_paid = st.radio("Tryout fee paid?",
                           ["Yes", "No", "Waived"],
                           key="fee_paid",
                           horizontal=True)
    
    medical = st.text_area("Medical Conditions/Current Injuries (if any)", key="medical", height=80,
                          help="Please disclose any conditions staff should be aware of")
    
    st.markdown("---")
    
    # Validation and navigation
    if st.button("Continue to Waiver →", type="primary", use_container_width=True):
        # Basic validation
        required_fields = {
            'First Name': first_name,
            'Last Name': last_name,
            'Email': email,
            'Phone': phone,
            'City': city,
            'State': state,
            'Emergency Contact Name': emergency_name,
            'Emergency Contact Phone': emergency_phone,
            'Primary Position': primary_position,
            'Dominant Foot': dominant_foot,
            'Outdoor Experience': outdoor_exp,
            'Indoor Experience': indoor_exp,
            'Highest Level': highest_level,
            'How Heard': how_heard
        }
        
        missing = [k for k, v in required_fields.items() if not v]
        
        if missing:
            st.error(f"Please complete required fields: {', '.join(missing)}")
        else:
            # Store data in session state
            st.session_state.player_data = {
                'first_name': first_name,
                'last_name': last_name,
                'preferred_name': preferred_name,
                'dob': str(dob),
                'email': email,
                'phone': phone,
                'city': city,
                'state': state,
                'emergency_contact_name': emergency_name,
                'emergency_contact_phone': emergency_phone,
                'primary_position': primary_position,
                'secondary_position': secondary_position,
                'dominant_foot': dominant_foot,
                'height': height,
                'weight': weight,
                'jersey_size': jersey_size,
                'outdoor_experience': outdoor_exp,
                'indoor_experience': indoor_exp,
                'highest_level': highest_level,
                'current_team': current_team,
                'college': college,
                'masl_experience': masl_experience,
                'notable_achievements': notable,
                'video_link': video_link,
                'how_heard': how_heard,
                'under_contract': under_contract,
                'us_work_eligible': us_eligible,
                'medical_conditions': medical,
                'fee_paid': fee_paid
            }
            st.session_state.page = 'waiver'
            st.rerun()

def render_waiver_page():
    """Render the waiver and signature page"""
    render_header()
    
    player = st.session_state.player_data
    st.markdown(f"**Registering:** {player.get('first_name', '')} {player.get('last_name', '')}")
    
    st.markdown('<div class="section-header"><h3>📜 Waiver and Release of Liability</h3></div>', unsafe_allow_html=True)
    
    st.markdown("Please read the following waiver carefully before signing:")
    
    # Waiver text in scrollable container
    st.markdown(f'<div class="waiver-text">{WAIVER_TEXT.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Acknowledgment checkboxes
    st.markdown("**Please confirm the following:**")
    
    ack1 = st.checkbox("I have read and understand the waiver and release of liability", key="ack1")
    ack2 = st.checkbox("I confirm that all information provided in my registration is accurate", key="ack2")
    ack3 = st.checkbox("I consent to photo/video recording during the tryout", key="ack3")
    ack4 = st.checkbox("I am physically fit to participate in this tryout", key="ack4")
    
    st.markdown("---")
    
    st.markdown('<div class="section-header"><h3>✍️ Electronic Signature</h3></div>', unsafe_allow_html=True)
    
    st.markdown("Please sign in the box below using your finger or stylus:")
    
    # Signature canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 1)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=600,
        drawing_mode="freedraw",
        key="signature_canvas",
    )
    
    col1, col2 = st.columns(2)
    with col1:
        typed_name = st.text_input("Type your full legal name to confirm signature *", key="typed_name")
    with col2:
        signature_date = st.date_input("Date", value=date.today(), disabled=True, key="sig_date")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Registration", use_container_width=True):
            st.session_state.page = 'registration'
            st.rerun()
    
    with col2:
        if st.button("Complete Registration ✓", type="primary", use_container_width=True):
            # Validate
            if not all([ack1, ack2, ack3, ack4]):
                st.error("Please confirm all acknowledgment checkboxes.")
            elif not typed_name:
                st.error("Please type your full legal name to confirm your signature.")
            elif typed_name.lower() != f"{player.get('first_name', '')} {player.get('last_name', '')}".lower():
                st.error("Typed name must match your registration name.")
            elif canvas_result.image_data is None or np.sum(canvas_result.image_data) == np.sum(np.full_like(canvas_result.image_data, 255)):
                st.error("Please provide your signature in the box above.")
            else:
                # Process signature
                signature_base64 = save_signature_as_base64(canvas_result)
                
                # Assign tryout number
                tryout_number = get_next_tryout_number()
                st.session_state.player_data['tryout_number'] = tryout_number
                st.session_state.tryout_number = tryout_number
                st.session_state.signature_data = signature_base64
                
                # Save to Google Sheets
                save_to_google_sheets(st.session_state.player_data, signature_base64)
                
                # Move to confirmation
                st.session_state.page = 'confirmation'
                st.rerun()

def render_confirmation_page():
    """Render the confirmation page with tryout number"""
    render_header()
    
    player = st.session_state.player_data
    
    st.markdown("""
    <div class="success-box">
        <h2>✅ Registration Complete!</h2>
        <p>Your tryout number is:</p>
        <div class="tryout-number">{}</div>
        <p style="font-size: 18px; margin-top: 20px;">
            <strong>{} {}</strong>
        </p>
        <p>Please remember this number - you'll need it during the tryout.</p>
    </div>
    """.format(
        st.session_state.tryout_number,
        player.get('first_name', ''),
        player.get('last_name', '')
    ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### Registration Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Personal Information**")
        st.write(f"- Name: {player.get('first_name', '')} {player.get('last_name', '')}")
        st.write(f"- Email: {player.get('email', '')}")
        st.write(f"- Phone: {player.get('phone', '')}")
        st.write(f"- Location: {player.get('city', '')}, {player.get('state', '')}")
        
    with col2:
        st.markdown("**Soccer Information**")
        st.write(f"- Position: {player.get('primary_position', '')}")
        st.write(f"- Dominant Foot: {player.get('dominant_foot', '')}")
        st.write(f"- Indoor Experience: {player.get('indoor_experience', '')}")
        st.write(f"- Highest Level: {player.get('highest_level', '')}")
    
    st.markdown("---")
    
    st.info("📸 Please proceed to the photo station, then report to the field for warm-ups.")
    
    if st.button("Register Another Player", type="primary", use_container_width=True):
        # Reset session state for next player
        st.session_state.page = 'registration'
        st.session_state.player_data = {}
        st.session_state.tryout_number = None
        st.session_state.signature_data = None
        st.rerun()

def render_admin_page():
    """Render admin dashboard (accessible via URL parameter)"""
    render_header()
    
    st.markdown("## 🔐 Admin Dashboard")
    
    st.warning("Admin functionality requires Google Sheets integration to be configured.")
    
    # Show current session registrations
    st.markdown("### Current Session Stats")
    st.metric("Players Registered This Session", 
              st.session_state.get('current_tryout_counter', 1) - 1)
    
    # Would show data from Google Sheets in production
    st.markdown("### Recent Registrations")
    st.info("Connect Google Sheets to view all registrations.")

# Main app routing
def main():
    # Check for admin access
    query_params = st.query_params
    if query_params.get('admin') == 'true':
        render_admin_page()
    else:
        if st.session_state.page == 'registration':
            render_registration_page()
        elif st.session_state.page == 'waiver':
            render_waiver_page()
        elif st.session_state.page == 'confirmation':
            render_confirmation_page()

if __name__ == "__main__":
    main()
