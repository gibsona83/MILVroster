import streamlit as st
import pandas as pd
import os
import re
import requests
from io import BytesIO

# ✅ Must be the first Streamlit command!
st.set_page_config(page_title="MILV Physician Roster", page_icon="🏥", layout="wide")

# Load Excel file from GitHub raw URL
GITHUB_FILE_URL = "https://raw.githubusercontent.com/gibsona83/MILVroster/main/MILV%20-%20Provider%20Worksheet.xlsx"

# ✅ Load Data Function (Ensures Data Loads Properly)
@st.cache_data(ttl=600)
def load_data():
    try:
        st.write("Downloading data from GitHub...")
        response = requests.get(GITHUB_FILE_URL, timeout=30)  # Increased timeout
        response.raise_for_status()  # Check for request errors
        df = pd.read_excel(BytesIO(response.content), sheet_name='Providers', engine='openpyxl')
        st.write("Data loaded successfully!")
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# ✅ Load data directly from GitHub
df = load_data()

# ✅ Ensure Data Is Loaded Correctly
if df is None or df.empty:
    st.error("Failed to load data. Please check the GitHub source.")
    st.stop()

# ✅ Debug: Show Column Names
st.write("Column Names in DataFrame:", df.columns.tolist())

# ✅ Fix NaN Values
df = df.fillna("")

# ✅ Ensure Required Columns Exist
required_columns = ['MILV Radiologist/Extender', 'Employment Type', 'Subspecialty']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()

# ✅ Clean "Employment Type" by removing brackets `[]`
df['Employment Type'] = df['Employment Type'].astype(str).apply(lambda x: re.sub(r"\[.*?\]", "", x).strip())

# ✅ Get Unique Filter Options
employment_type_options = sorted(df['Employment Type'].dropna().unique())

# ✅ Fix Subspecialties (Splitting by `,` or `/`)
df['Subspecialty'] = df['Subspecialty'].astype(str)
all_subspecialties = set()
for subspecialties in df['Subspecialty']:
    all_subspecialties.update(map(str.strip, re.split(r'[,/]', subspecialties)))  # Split by comma or slash & strip spaces
subspecialty_options = sorted(all_subspecialties)

# ✅ Load and display the logo if available
logo_path = "milv.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=300)

# ✅ UI Styling
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

# ✅ Search & Filter Options
search_name = st.text_input("Search by Provider Name", "")

# ✅ Employment Type Filter (Uses Cleaned Data)
employment_type = st.multiselect("Filter by Employment Type", options=employment_type_options)

# ✅ Subspecialty Search (Supports Individual Filtering)
subspecialty = st.multiselect("Filter by Subspecialty", options=subspecialty_options)

# ✅ Apply Filters
filtered_df = df.copy()

# ✅ Debug: Show First Few Rows Before Filtering
st.write("Data Preview Before Filtering:")
st.write(df.head())

# ✅ Name Filtering
if search_name:
    filtered_df = filtered_df[
        filtered_df['MILV Radiologist/Extender'].str.contains(search_name, case=False, na=False)
    ]

# ✅ Employment Type Filtering
if employment_type:
    filtered_df = filtered_df[filtered_df['Employment Type'].isin(employment_type)]

# ✅ Subspecialty Filtering
if subspecialty:
    filtered_df = filtered_df[
        filtered_df['Subspecialty'].apply(lambda x: any(sub in x for sub in subspecialty))
    ]

# ✅ Debug: Show First Few Rows After Filtering
st.write("Dat
