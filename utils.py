import base64
import streamlit as st

def display_icon(icon_path, width=50):
    try:
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'<img src="data:image/png;base64,{encoded_string}" width="{width}">', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Icon not found at: {icon_path}")

def calculate_fear_index(polarity, subjectivity):
    if polarity < -0.3 and subjectivity > 0.5:
        return 10  # High fear
    elif polarity < -0.2:
        return 7  # Moderate fear
    elif polarity < -0.1:
        return 4  # Low fear
    else:
        return 1  # No fear
