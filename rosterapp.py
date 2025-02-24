import streamlit as st
import pandas as pd
import os

# ✅ Must be the first Streamlit command!
st.set_page_config(page_title="MILV Physician Roster", page_icon="🏥", layout="wide")

# Set the correct file path
file_path = r"C:\Users\aliso\OneDrive\Desktop\MILV\Dashboard\MILV - Provider Worksheet.xlsx"

# If the file doesn't exist, display a warning
if not os.path.exists(file_path):
    st.warning("⚠️ File not found! Please upload it manually.")
    uploaded_file = st.file_uploader("Upload Provider Worksheet", type=["xlsx"])
    if uploaded_file:
        file_path = uploaded_file  # Use the uploaded file
    else:
        st.stop()  # Stop execution until a file is provided

# Function to load data
@st.cache_data
def load_data(file):
    df = pd.read_excel(file, sheet_name='Providers')

    # Normalize Subspecialties (split multi-subspecialties and create a searchable column)
    df['Subspecialty'] = df['Subspecialty'].fillna('').str.strip()

    # Standardizing subspecialty names
    subspecialty_mapping = {
        'PET/CT': 'PETCT',
        'Interventional / Residency Program': 'Interventional, Residency Program',
        '\xa0Diagnostic': 'Diagnostic',
    }
    df['Subspecialty'] = df['Subspecialty'].replace(subspecialty_mapping, regex=True)

    df['Subspecialty Searchable'] = df['Subspecialty'].str.split(',')
    df['Subspecialty Searchable'] = df['Subspecialty Searchable'].apply(lambda x: [s.strip() for s in x if s.strip()])
    df['Subspecialty Searchable'] = df['Subspecialty Searchable'].apply(lambda x: list(set(x)))  # Remove duplicates

    # Normalize Employment Type (remove dates but retain original in dataset)
    df['Employment Type Clean'] = df['Employment Type'].str.replace(r'\s*\[.*?\]', '', regex=True).str.strip()

    return df

# Load the data
df = load_data(file_path)

# Ensure cleaned categories are correctly reflected in dropdowns
employment_type_options = sorted(df['Employment Type Clean'].dropna().unique())
subspecialty_options = sorted(set(sub for sublist in df['Subspecialty Searchable'] for sub in sublist))

# Load and display the logo
logo_path = "milv.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=300)

# Updated UI Styling for better readability
st.markdown("""
    <style>
        .stApp {
            background-color: #f5f7fa;
            color: #002F6C;
        }
        .stTextInput, .stMultiSelect, .stDownloadButton, .stDataFrame {
            background-color: #ffffff !important;
            color: #002F6C !important;
        }
        h1 {
            color: #002F6C;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.title("MILV Physician Roster")

# Search and Filter Options
search_name = st.text_input("Search by Provider Name", "")
employment_type = st.multiselect("Filter by Employment Type", options=employment_type_options)
subspecialty = st.multiselect("Filter by Subspecialty", options=subspecialty_options)

# Filtering Logic
filtered_df = df.copy()
if search_name:
    filtered_df = filtered_df[filtered_df['MILV Radiologist/Extender'].str.contains(search_name, case=False, na=False)]
if employment_type:
    filtered_df = filtered_df[filtered_df['Employment Type Clean'].isin(employment_type)]
if subspecialty:
    filtered_df = filtered_df[filtered_df['Subspecialty Searchable'].apply(lambda x: any(s in x for s in subspecialty))]

# Display Data
st.write(f"Showing {len(filtered_df)} of {len(df)} providers")
st.dataframe(filtered_df.drop(columns=['Subspecialty Searchable', 'Employment Type Clean']))

# Download Button
csv = filtered_df.drop(columns=['Subspecialty Searchable', 'Employment Type Clean']).to_csv(index=False).encode('utf-8')
st.download_button("Download Filtered Data", csv, "filtered_providers.csv", "text/csv")
