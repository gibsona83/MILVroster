import streamlit as st
import pandas as pd
import os

# ✅ Must be the first Streamlit command!
st.set_page_config(page_title="MILV Physician Roster", page_icon="🏥", layout="wide")

# Load Excel file from GitHub raw URL
GITHUB_FILE_URL = "https://raw.githubusercontent.com/gibsona83/MILVroster/main/MILV%20-%20Provider%20Worksheet.xlsx"

# Function to load data
@st.cache_data(ttl=600)  # Cache expires every 10 minutes
def load_data():
    try:
        df = pd.read_excel(GITHUB_FILE_URL, sheet_name='Providers', engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Error loading data from GitHub: {e}")
        return None

# File upload as a fallback
uploaded_file = st.file_uploader("Upload Provider Data (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Providers", engine="openpyxl")
else:
    df = load_data()

# Validate data
if df is None or df.empty:
    st.error("Failed to load data. Please upload a valid file or check the GitHub source.")
    st.stop()

# Ensure required columns exist
required_columns = ['MILV Radiologist/Extender', 'Employment Type', 'Subspecialty']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()

# Get unique values for dropdowns
employment_type_options = sorted(df['Employment Type'].dropna().unique())
subspecialty_options = sorted(df['Subspecialty'].dropna().unique())

# Load and display the logo if available
logo_path = "milv.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=300)

# UI Styling
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f5f7fa;
            color: #002F6C;
        }
        .stTextInput, .stMultiSelect, .stDownloadButton {
            background-color: #ffffff !important;
            color: #002F6C !important;
        }
        h1 {
            color: #002F6C;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("MILV Physician Roster")

# Search & Filter Options
search_name = st.text_input("Search by Provider Name", "")
employment_type = st.multiselect("Filter by Employment Type", options=employment_type_options)
subspecialty = st.multiselect("Filter by Subspecialty", options=subspecialty_options)

# Apply Filters
filtered_df = df.copy()

if search_name:
    filtered_df = filtered_df[
        filtered_df['MILV Radiologist/Extender'].str.contains(search_name, case=False, na=False)
    ]

if employment_type:
    filtered_df = filtered_df[filtered_df['Employment Type'].isin(employment_type)]

if subspecialty:
    filtered_df = filtered_df[filtered_df['Subspecialty'].isin(subspecialty)]

# Display Data with Pagination Support
st.write(f"Showing {len(filtered_df)} of {len(df)} providers")

if len(filtered_df) > 0:
    st.data_editor(filtered_df, use_container_width=True, height=500)
else:
    st.warning("No matching providers found.")

# Download Button
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Filtered Data", csv, "filtered_providers.csv", "text/csv")
