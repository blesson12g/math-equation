import streamlit as st
import requests
import time  # Included for demonstration purposes

# Initialize session states
if 'data' not in st.session_state:
    st.session_state.data = None
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

def fetch_data():
    """
    Simulated API call - replace this with your actual API endpoint
    """
    try:
        # Simulate API call with delay
        time.sleep(2)  # Remove this in production
        
        # Replace this with your actual API call
        # response = requests.get('https://api.example.com/data')
        # return response.json()
        
        return [
            "First item from API",
            "Second item from API",
            "Third item from API",
            "Fourth item from API"
        ]
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def main():
    st.title("API Data Iterator")
    
    # Button to fetch data
    if not st.session_state.data:
        if st.button("Fetch Data from API"):
            # Show spinner only during API call
            with st.spinner('Loading data from API...'):
                st.session_state.data = fetch_data()
                st.session_state.current_index = 0
                st.rerun()
    
    # Show data iterator once we have data
    if st.session_state.data:
        st.success("Data loaded successfully!")
        
        # Display current item
        if st.session_state.current_index < len(st.session_state.data):
            # Progress indicator
            progress = (st.session_state.current_index + 1) / len(st.session_state.data)
            st.progress(progress)
            
            st.write("Current item:")
            st.header(st.session_state.data[st.session_state.current_index])
            st.caption(f"Item {st.session_state.current_index + 1} of {len(st.session_state.data)}")
            
            # Navigation buttons in columns
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Next Item"):
                    if st.session_state.current_index < len(st.session_state.data) - 1:
                        st.session_state.current_index += 1
                        st.rerun()
            with col2:
                if st.button("Start Over"):
                    st.session_state.current_index = 0
                    st.rerun()
        else:
            st.warning("You've reached the end!")
            if st.button("Back to Start"):
                st.session_state.current_index = 0
                st.rerun()

if __name__ == "__main__":
    main()