import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* General Theme Adjustments */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* Headers styling */
        h1, h2, h3 {
            color: #1e1e1e;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 600;
        }

        /* Metric styling for Dashboards */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            color: #3b82f6;
            font-weight: 700;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1rem;
            color: #6b7280;
            font-weight: 500;
        }

        /* Card-like styling for form and other sections */
        .stForm {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #e5e7eb;
        }

        /* Submit Button Styling */
        div[data-testid="stFormSubmitButton"] > button {
            background-color: #3b82f6;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            border: none;
            width: 100%;
            padding: 10px;
            transition: background-color 0.3s;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #2563eb;
            color: white;
            border: none;
        }
        
        /* Secondary buttons */
        div.stButton > button {
            border-radius: 8px;
            font-weight: 500;
        }
        
        /* Expanders (Acordeones) */
        .streamlit-expanderHeader {
            font-weight: 600;
            color: #374151;
            background-color: white;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }

        /* Dataframe styling */
        div[data-testid="stDataFrame"] {
            background-color: white;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
        }

        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Title styling for the 6to Basico app */
        .main-title {
            text-align: center;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
            margin-bottom: 20px;
            font-weight: 800;
        }
        </style>
    """, unsafe_allow_html=True)

def header(title):
    st.markdown(f"<h1 class='main-title'>{title}</h1>", unsafe_allow_html=True)
