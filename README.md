# St. Louis Ambush FC - Tryout Check-In System

A Streamlit application for managing player registration, waivers, and data collection at open tryouts.

## Features

- **Player Registration Form**: Comprehensive data collection including:
  - Personal information (name, contact, emergency contact)
  - Soccer background (position, experience, highest level played)
  - Physical details (height, weight, jersey size)
  - Additional info (video links, how they heard about tryout)

- **Electronic Waiver System**: 
  - Full liability waiver and release
  - Photo/video consent
  - Canvas-based signature capture
  - Acknowledgment checkboxes

- **Tryout Number Assignment**: Automatic sequential numbering for player identification during tryout

- **Google Sheets Integration**: All data automatically syncs to a Google Sheet for easy management

- **Admin Dashboard**: View registrations and stats (access via `?admin=true`)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Google Sheets Integration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable the **Google Sheets API** and **Google Drive API**
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Create new service account
   - Grant it "Editor" role
   - Create and download JSON key
5. Create your Google Sheet:
   - Create a new Google Sheet named "Ambush Tryout 2025"
   - Share it with your service account email (found in the JSON key)
   - Add headers in the first row (see below)

### 3. Configure Secrets

Create `.streamlit/secrets.toml` based on the example file:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit the file and paste your service account credentials.

### 4. Google Sheet Headers

Add these headers to Row 1 of your Google Sheet:

```
Tryout Number | Check-In Time | First Name | Last Name | Preferred Name | DOB | Email | Phone | City | State | Emergency Contact | Emergency Phone | Primary Position | Secondary Position | Dominant Foot | Height | Weight | Jersey Size | Outdoor Exp | Indoor Exp | Highest Level | Current Team | College | MASL Experience | Notable Achievements | Video Link | How Heard | Under Contract | US Eligible | Medical Conditions | Waiver Signed | Waiver Time | Fee Paid
```

### 5. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Deployment Options

### Streamlit Cloud (Recommended for quick setup)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add secrets in the Streamlit Cloud dashboard
5. Deploy!

### Local Network (For tryout day)

Run on a laptop connected to your venue's WiFi:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Access from iPads/tablets at: `http://[laptop-ip]:8501`

## Usage on Tryout Day

1. Set up 1-2 tablets/iPads at the check-in table
2. Open the app in each device's browser
3. Players complete the form on the device
4. They sign the waiver with their finger
5. Confirmation page shows their tryout number
6. Data automatically saves to Google Sheets
7. Staff can monitor registrations via the Google Sheet or admin dashboard

## Customization

### Waiver Text
Edit the `WAIVER_TEXT` variable in `app.py` to customize the liability waiver.

### Branding Colors
Modify the CSS in the `st.markdown()` style section:
- Primary dark: `#1a1a2e` (navy blue)
- Accent: `#f4d03f` (gold/yellow)

### Fields
Add or remove fields in the `render_registration_page()` function as needed.

## Troubleshooting

**Signature not saving**: Ensure the player draws on the canvas (not just clicking). The app validates that actual drawing occurred.

**Google Sheets not updating**: 
- Verify service account has edit access to the sheet
- Check that API is enabled in Google Cloud Console
- Verify credentials in secrets.toml

**Canvas not appearing**: The `streamlit-drawable-canvas` package requires a modern browser. Use Chrome or Safari.

## Support

For issues or questions, contact [Your Contact Info]

---

Built for St. Louis Ambush FC 🔵⚽
