import streamlit as st
import PyPDF2
import io

# Page configuration
st.set_page_config(
    page_title="Axon Agent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    h1, h2, h3 {
        font-family: 'Sora', sans-serif !important;
        color: #00d4ff !important;
    }
    
    .main-header {
        font-family: 'Sora', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d4ff, #7b2cbf, #ff006e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.6);
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .upload-card {
        background: rgba(255, 255, 255, 0.03);
        border: 2px dashed rgba(0, 212, 255, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        text-align: center;
    }
    
    .content-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .stats-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .stat-badge {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-family: 'JetBrains Mono', monospace;
        color: #00d4ff;
        font-size: 0.9rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #7b2cbf, #00d4ff) !important;
        border: none !important;
        border-radius: 8px !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3) !important;
    }
    
    .extracted-text {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 8px;
        padding: 1.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.9);
        white-space: pre-wrap;
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.02);
        border: 2px dashed rgba(0, 212, 255, 0.3);
        border-radius: 12px;
    }
    
    .stFileUploader > div > div:hover {
        border-color: rgba(0, 212, 255, 0.6);
    }
</style>
""", unsafe_allow_html=True)


def extract_text_from_pdf(pdf_file) -> tuple[str, int]:
    """
    Extract text content from a PDF file without saving it.
    Returns the extracted text and number of pages.
    """
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
    num_pages = len(pdf_reader.pages)
    
    text_content = []
    for page_num, page in enumerate(pdf_reader.pages, 1):
        page_text = page.extract_text()
        if page_text:
            text_content.append(f"--- Page {page_num} ---\n{page_text}")
    
    return "\n\n".join(text_content), num_pages


# Main Header
st.markdown('<h1 class="main-header"> Axon Agent </h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle"> Agent that helps you to summarize your scientific paper /p>', unsafe_allow_html=True)

# Upload Section
st.markdown("### 📤 Upload Document")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    help="Upload a PDF document to extract its text content",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    # Show file info
    file_size_kb = uploaded_file.size / 1024
    file_size_display = f"{file_size_kb:.1f} KB" if file_size_kb < 1024 else f"{file_size_kb/1024:.2f} MB"
    
    st.markdown(f"""
    <div class="content-card">
        <div class="stats-row">
            <span class="stat-badge">📁 {uploaded_file.name}</span>
            <span class="stat-badge">📊 {file_size_display}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Extract button
    if st.button("🔍 Extract Text", use_container_width=True):
        with st.spinner("Extracting text from PDF..."):
            try:
                extracted_text, num_pages = extract_text_from_pdf(uploaded_file)
                
                if extracted_text.strip():
                    # Show extraction stats
                    word_count = len(extracted_text.split())
                    char_count = len(extracted_text)
                    
                    st.markdown("### 📊 Extraction Results")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📄 Pages", num_pages)
                    with col2:
                        st.metric("📝 Words", f"{word_count:,}")
                    with col3:
                        st.metric("🔤 Characters", f"{char_count:,}")
                    
                    st.markdown("### 📜 Extracted Content")
                    
                    # Display extracted text in a scrollable container
                    st.markdown(f'<div class="extracted-text">{extracted_text}</div>', unsafe_allow_html=True)
                    
                    # Download button for extracted text
                    st.download_button(
                        label="💾 Download as Text File",
                        data=extracted_text,
                        file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_extracted.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.warning("⚠️ No text content could be extracted from this PDF. It might be a scanned document or contain only images.")
                    
            except Exception as e:
                st.error(f"❌ Error extracting text: {str(e)}")

else:
    # Empty state
    st.markdown("""
    <div class="upload-card">
        <h3 style="color: rgba(255,255,255,0.7); margin-bottom: 1rem;">👆 Drop your Scientific Paper here</h3>
        <p style="color: rgba(255,255,255,0.5);">Supported format: PDF</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<center><small style='color: rgba(255,255,255,0.4);'>Made with ❤️ by Gorgone </small></center>",
    unsafe_allow_html=True
)
