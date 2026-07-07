import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* General Theme Adjustments */
        
        /* Headers styling */
        h1, h2, h3 {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 600;
        }

        /* Metric styling for Dashboards */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            color: var(--primary-color);
            font-weight: 700;
        }

        /* Card-like styling for form and other sections */
        .stForm {
            background-color: var(--secondary-background-color);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid var(--faded-text60);
        }

        /* Submit Button Styling */
        div[data-testid="stFormSubmitButton"] > button {
            background-color: var(--primary-color);
            color: white;
            font-weight: 600;
            border-radius: 8px;
            border: none;
            width: 100%;
            padding: 10px;
            transition: opacity 0.3s;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            opacity: 0.8;
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
            border-radius: 8px;
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
