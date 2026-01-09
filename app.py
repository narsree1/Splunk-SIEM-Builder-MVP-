"""
SIEM Log Source Onboarding Assistant
A Streamlit application to help Security Engineers onboard log sources into Splunk.
Supports multiple AI backends: Groq (free), HuggingFace (free), Claude (paid), Ollama (local).
"""

import streamlit as st
from utils.kb_loader import KBLoader
from utils.ai_client import AIClientFactory, BaseAIClient

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
    .info-box {
        background-color: #e7f3ff;
        border: 1px solid #0066cc;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .provider-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        border: 1px solid #dee2e6;
    }
    .free-badge {
        background-color: #28a745;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-left: 8px;
    }
    .paid-badge {
        background-color: #6c757d;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-left: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_source" not in st.session_state:
    st.session_state.selected_source = None
if "selected_provider" not in st.session_state:
    st.session_state.selected_provider = None
if "ai_client" not in st.session_state:
    st.session_state.ai_client = None

# Initialize KB Loader
kb_loader = KBLoader()

# Helper function to get secrets safely
def get_secrets_dict():
    """Get all available secrets as a dictionary."""
    secrets = {}
    try:
        if hasattr(st, 'secrets'):
            for key in ["ANTHROPIC_API_KEY", "GROQ_API_KEY", "HUGGINGFACE_API_KEY"]:
                try:
                    value = st.secrets.get(key)
                    if value:
                        secrets[key] = value
                except:
                    pass
    except:
        pass
    return secrets

# Helper function to initialize AI client
def initialize_ai_client(provider: str, secrets: dict) -> BaseAIClient:
    """Initialize AI client for the selected provider."""
    provider_info = AIClientFactory.PROVIDERS.get(provider, {})
    key_name = provider_info.get("key_name")
    
    if provider == "ollama":
        return AIClientFactory.create_client("ollama")
    elif key_name and secrets.get(key_name):
        return AIClientFactory.create_client(provider, secrets.get(key_name))
    return None

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/security-checked.png", width=80)
    st.markdown("## 🛡️ SIEM Onboarding")
    st.markdown("---")
    
    # Log source selection
    st.markdown("### 📋 Select Log Source")
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
    
    # AI Provider selection
    st.markdown("### 🤖 AI Assistant")
    
    providers = AIClientFactory.get_available_providers()
    secrets = get_secrets_dict()
    
    # Check which providers are available
    available_providers = []
    for prov_id, prov_info in providers.items():
        key_name = prov_info.get("key_name")
        if prov_id == "ollama":
            available_providers.append(prov_id)
        elif key_name and secrets.get(key_name):
            available_providers.append(prov_id)
    
    if available_providers:
        selected_provider = st.selectbox(
            "AI Provider:",
            options=available_providers,
            format_func=lambda x: providers[x]["name"],
            key="provider_selector"
        )
        
        # Initialize client if provider changed
        if st.session_state.selected_provider != selected_provider:
            st.session_state.selected_provider = selected_provider
            st.session_state.ai_client = initialize_ai_client(selected_provider, secrets)
            st.session_state.chat_history = []
        
        if st.session_state.ai_client:
            st.success(f"✅ {st.session_state.ai_client.get_provider_name()}")
    else:
        st.warning("⚠️ No AI configured")
        st.markdown("Add an API key in Settings → Secrets")
    
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
    
    Built with ❤️ using Streamlit
    """)

# Main content area
st.markdown('<p class="main-header">🛡️ SIEM Log Source Onboarding Assistant</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">Currently viewing: <strong>{log_sources[selected_source]["display_name"]}</strong></p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📘 Integration Guide", "🔗 References", "💬 AI Chat", "⚙️ AI Setup"])

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

# Tab 3: AI Chat
with tab3:
    st.markdown("### 💬 Ask Questions About This Integration")
    
    if st.session_state.ai_client:
        st.markdown(f"*Using **{st.session_state.ai_client.get_provider_name()}** to answer questions about **{log_sources[selected_source]['display_name']}** integration.*")
        
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
                    <strong>🤖 AI:</strong><br>{message["content"]}
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
            
            # Get AI response
            with st.spinner("AI is thinking..."):
                response = st.session_state.ai_client.get_response(
                    question=user_question,
                    kb_content=kb_context,
                    source_name=log_sources[selected_source]["display_name"],
                    chat_history=st.session_state.chat_history[:-1]
                )
            
            if response["success"]:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["response"]
                })
            else:
                st.error(f"Error: {response['message']}")
            
            st.rerun()
    else:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ AI Assistant Not Configured</h4>
            <p>To enable the chat feature, configure an AI provider in the <strong>⚙️ AI Setup</strong> tab.</p>
            <p>We recommend <strong>Groq</strong> (free) for the best experience!</p>
        </div>
        """, unsafe_allow_html=True)

# Tab 4: AI Setup
with tab4:
    st.markdown("### ⚙️ AI Provider Configuration")
    st.markdown("Configure an AI provider to enable the chat assistant. **Free options available!**")
    
    st.markdown("---")
    
    # Show all providers with setup instructions
    providers = AIClientFactory.get_available_providers()
    secrets = get_secrets_dict()
    
    for prov_id, prov_info in providers.items():
        is_free = prov_info.get("free", False)
        badge = '<span class="free-badge">FREE</span>' if is_free else '<span class="paid-badge">PAID</span>'
        key_name = prov_info.get("key_name")
        
        # Check if configured
        is_configured = False
        if prov_id == "ollama":
            # Check Ollama availability
            try:
                from utils.ai_client import OllamaClient
                client = OllamaClient()
                is_configured = client.available
            except:
                is_configured = False
        elif key_name:
            is_configured = bool(secrets.get(key_name))
        
        status = "✅ Configured" if is_configured else "❌ Not configured"
        
        st.markdown(f"""
        <div class="provider-card">
            <strong>{prov_info['name']}</strong> {badge}<br>
            <small>{prov_info['description']}</small><br>
            <small><strong>Status:</strong> {status}</small>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"Setup instructions for {prov_info['name']}"):
            if prov_id == "groq":
                st.markdown("""
                **Groq** offers **free** access to Llama 3.3 70B with very fast inference!
                
                **Steps:**
                1. Go to [console.groq.com/keys](https://console.groq.com/keys)
                2. Sign up (free) and create an API key
                3. Add to Streamlit secrets:
                ```toml
                GROQ_API_KEY = "gsk_your_key_here"
                ```
                
                **Free Tier Limits:** ~30 requests/minute, 14,400 requests/day
                """)
            
            elif prov_id == "huggingface":
                st.markdown("""
                **HuggingFace** offers **free** access to Mixtral 8x7B.
                
                **Steps:**
                1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
                2. Sign up (free) and create an access token
                3. Add to Streamlit secrets:
                ```toml
                HUGGINGFACE_API_KEY = "hf_your_token_here"
                ```
                
                **Note:** Model may need ~30 seconds to load on first request.
                """)
            
            elif prov_id == "claude":
                st.markdown("""
                **Claude** is the most capable but requires a **paid** API subscription.
                
                **Steps:**
                1. Go to [console.anthropic.com](https://console.anthropic.com/)
                2. Sign up and add payment method
                3. Create an API key
                4. Add to Streamlit secrets:
                ```toml
                ANTHROPIC_API_KEY = "sk-ant-your_key_here"
                ```
                
                **Pricing:** Pay-per-use (see Anthropic pricing page)
                """)
            
            elif prov_id == "ollama":
                st.markdown("""
                **Ollama** runs **100% locally** on your machine - completely free and private!
                
                **Steps:**
                1. Download from [ollama.ai/download](https://ollama.ai/download)
                2. Install and start Ollama
                3. Pull a model: `ollama pull llama3.2`
                4. Ollama will be auto-detected (no API key needed)
                
                **Note:** Only works for local development, not on Streamlit Cloud.
                """)
    
    st.markdown("---")
    st.markdown("### 🔐 How to Add Secrets")
    
    st.markdown("""
    **For Streamlit Cloud:**
    1. Go to your app dashboard on [share.streamlit.io](https://share.streamlit.io)
    2. Click on your app → ⚙️ Settings → Secrets
    3. Add your API keys in TOML format:
    ```toml
    GROQ_API_KEY = "gsk_..."
    # or
    HUGGINGFACE_API_KEY = "hf_..."
    # or
    ANTHROPIC_API_KEY = "sk-ant-..."
    ```
    4. Click Save and reboot the app
    
    **For Local Development:**
    1. Create `.streamlit/secrets.toml` in your project
    2. Add your API keys
    3. Restart the app
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <p>SIEM Onboarding Assistant v1.1 | Built with Streamlit | Supports Free AI (Groq, HuggingFace)</p>
    <p>📖 <a href="https://github.com/your-repo/siem-onboarding-app" target="_blank">Documentation</a> | 
    🐛 <a href="https://github.com/your-repo/siem-onboarding-app/issues" target="_blank">Report Issues</a></p>
</div>
""", unsafe_allow_html=True)
