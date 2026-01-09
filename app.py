"""
SIEM Log Source Onboarding Assistant
A Streamlit application to help Security Engineers onboard log sources into Splunk.
"""

import streamlit as st
from utils.kb_loader import KBLoader
from utils.claude_client import ClaudeClient

# Page configuration
st.set_page_config(
    page_title="SIEM Onboarding Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #5A6C7D;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .reference-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #1E3A5F;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_source" not in st.session_state:
    st.session_state.selected_source = None

# Initialize KB Loader
kb_loader = KBLoader()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-checked.png", width=80)
    st.markdown("## 🛡️ SIEM Onboarding")
    st.markdown("---")
    
    # Log source selection
    st.markdown("### Select Log Source")
    log_sources = kb_loader.get_available_sources()
    
    selected_source = st.selectbox(
        "Choose a log source to onboard:",
        options=list(log_sources.keys()),
        format_func=lambda x: log_sources[x]["display_name"],
        key="source_selector"
    )
    
    # Update session state when source changes
    if st.session_state.selected_source != selected_source:
        st.session_state.selected_source = selected_source
        st.session_state.chat_history = []  # Clear chat when source changes
    
    st.markdown("---")
    
    # Quick navigation
    st.markdown("### 📑 Quick Navigation")
    st.markdown("""
    - [Overview](#overview)
    - [Pre-requisites](#pre-requisites)
    - [Network Requirements](#network-connectivity-requirements)
    - [Logging Standard](#logging-standard)
    - [Log Collection](#log-collection-standard)
    - [Validation](#validation-troubleshooting)
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    This tool helps Security Engineers 
    onboard log sources into Splunk SIEM.
    
    Built with ❤️ using Streamlit & Claude AI
    """)

# Main content area
st.markdown('<p class="main-header">🛡️ SIEM Log Source Onboarding Assistant</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">Currently viewing: <strong>{log_sources[selected_source]["display_name"]}</strong></p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["📘 Integration Guide", "🔗 References", "💬 Chat with Claude"])

# Tab 1: Integration Guide
with tab1:
    kb_content = kb_loader.load_kb_content(selected_source)
    
    if kb_content["success"]:
        st.markdown(kb_content["content"])
    else:
        st.markdown(f"""
        <div class="warning-box">
            <h4>⚠️ Knowledge Base Not Found</h4>
            <p>{kb_content["message"]}</p>
            <p><strong>To add this log source:</strong></p>
            <ol>
                <li>Create a file named <code>kb/{selected_source}.md</code></li>
                <li>Follow the KB template structure (see README.md)</li>
                <li>Add references in <code>kb/references.json</code></li>
                <li>Restart the application</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

# Tab 2: References
with tab2:
    references = kb_loader.get_references(selected_source)
    
    st.markdown(f"### 📚 Resources for {log_sources[selected_source]['display_name']}")
    
    if references["success"]:
        ref_data = references["data"]
        
        # Official Documentation
        st.markdown("#### 📄 Official Documentation")
        if ref_data.get("official_docs"):
            for doc in ref_data["official_docs"]:
                st.markdown(f"""
                <div class="reference-card">
                    <a href="{doc['url']}" target="_blank">📌 {doc['title']}</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No official documentation links available yet.")
        
        st.markdown("---")
        
        # YouTube Videos
        st.markdown("#### 🎥 YouTube Videos")
        if ref_data.get("youtube"):
            cols = st.columns(2)
            for idx, video in enumerate(ref_data["youtube"]):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="reference-card">
                        <a href="{video['url']}" target="_blank">▶️ {video['title']}</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No YouTube video links available yet.")
        
        st.markdown("---")
        
        # Blogs/Community (Optional)
        if ref_data.get("blogs_optional"):
            st.markdown("#### 📝 Blogs & Community Resources")
            for blog in ref_data["blogs_optional"]:
                st.markdown(f"""
                <div class="reference-card">
                    <a href="{blog['url']}" target="_blank">📖 {blog['title']}</a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="warning-box">
            <h4>⚠️ References Not Found</h4>
            <p>{references["message"]}</p>
            <p>Add an entry for <code>{selected_source}</code> in <code>kb/references.json</code></p>
        </div>
        """, unsafe_allow_html=True)

# Tab 3: Chat with Claude
with tab3:
    st.markdown("### 💬 Ask Questions About This Integration")
    st.markdown(f"*Claude is ready to help you with **{log_sources[selected_source]['display_name']}** integration.*")
    
    # Check for API key
    api_key_available = False
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY")
        if api_key:
            api_key_available = True
            claude_client = ClaudeClient(api_key)
    except Exception:
        api_key_available = False
    
    if not api_key_available:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ Claude API Key Not Configured</h4>
            <p>To enable the chat feature, add your Anthropic API key to Streamlit secrets:</p>
            <ol>
                <li>Go to your Streamlit Cloud app settings</li>
                <li>Navigate to "Secrets" section</li>
                <li>Add: <code>ANTHROPIC_API_KEY = "your-api-key-here"</code></li>
            </ol>
            <p>For local development, create a <code>.streamlit/secrets.toml</code> file.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>🧑 You:</strong><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Claude:</strong><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        with st.form(key="chat_form", clear_on_submit=True):
            user_question = st.text_area(
                "Your question:",
                placeholder="e.g., What ports need to be open for this integration?",
                height=100
            )
            
            col1, col2 = st.columns([1, 5])
            with col1:
                submit_button = st.form_submit_button("Send 📤")
            with col2:
                if st.form_submit_button("Clear Chat 🗑️"):
                    st.session_state.chat_history = []
                    st.rerun()
        
        if submit_button and user_question.strip():
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_question
            })
            
            # Get KB content for context
            kb_data = kb_loader.load_kb_content(selected_source)
            kb_context = kb_data["content"] if kb_data["success"] else "No KB content available for this source."
            
            # Get Claude's response
            with st.spinner("Claude is thinking..."):
                response = claude_client.get_response(
                    question=user_question,
                    kb_content=kb_context,
                    source_name=log_sources[selected_source]["display_name"],
                    chat_history=st.session_state.chat_history[:-1]  # Exclude current question
                )
            
            if response["success"]:
                # Add assistant response to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["response"]
                })
            else:
                st.error(f"Error: {response['message']}")
            
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <p>SIEM Onboarding Assistant v1.0 | Built with Streamlit & Claude AI</p>
    <p>📖 <a href="https://github.com/your-repo/siem-onboarding-app" target="_blank">Documentation</a> | 
    🐛 <a href="https://github.com/your-repo/siem-onboarding-app/issues" target="_blank">Report Issues</a></p>
</div>
""", unsafe_allow_html=True)
