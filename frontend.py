import streamlit as st
import requests

st.set_page_config(page_title="AI Shopping Assistant", layout="wide")
API_URL = "http://127.0.0.1:8000"

st.title("🛒 AI Shopping Assistant")

# --- INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Add a state variable to track if the user is viewing a past search
if "selected_history" not in st.session_state:
    st.session_state.selected_history = None

# --- SIDEBAR: FETCH HISTORY FROM FASTAPI ---
with st.sidebar:
    st.header("Search History")
    try:
        history_res = requests.get(f"{API_URL}/history")
        if history_res.status_code == 200:
            for idx, item in enumerate(history_res.json()):
                # Use a button instead of an expander
                if st.button(f"🔍 {item['query'][:30]}...", key=f"hist_{idx}"):
                    st.session_state.selected_history = item
                    st.rerun() # Instantly refresh the page to show the main screen
    except requests.exceptions.ConnectionError:
        st.error("Backend is offline. Please start FastAPI.")

# --- MAIN SCREEN LOGIC ---

# View 1: A past search is selected from the sidebar
if st.session_state.selected_history:
    st.subheader("Saved Search Result")
    st.info(f"**Query:** {st.session_state.selected_history['query']}")
    
    st.markdown(st.session_state.selected_history["recommendation"])
    
    st.divider()
    if st.button("← Back to New Search"):
        st.session_state.selected_history = None
        st.rerun()

# View 2: Normal Chat Interface
else:
    st.write("Ask me to find and compare products! e.g., *'Find the best laptop for AI development under ₹70,000.'*")
    
    # Render existing chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle new chat input
    if prompt := st.chat_input("What are you looking to buy?"):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching the web and comparing products..."):
                try:
                    response = requests.post(
                        f"{API_URL}/search",
                        json={"query": prompt}
                    )
                    
                    if response.status_code == 200:
                        bot_reply = response.json()["response"]
                        st.markdown(bot_reply)
                        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    else:
                        st.error(f"Error from backend: {response.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")