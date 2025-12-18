import streamlit as st
import os
import requests
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(
    page_title="Axon",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.02);
        border: 2px dashed rgba(0, 212, 255, 0.3);
        border-radius: 12px;
    }
    
    .stFileUploader > div > div:hover {
        border-color: rgba(0, 212, 255, 0.6);
    }
    
    .phase-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
    }
    
    .phase-active {
        border-color: #00d4ff;
        background: rgba(0, 212, 255, 0.1);
    }
    
    .phase-done {
        border-color: #22c55e;
        background: rgba(34, 197, 94, 0.1);
    }
    
    .phase-pending {
        opacity: 0.5;
    }
    
    .preview-box {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }
    
    .section-tag {
        display: inline-block;
        background: rgba(123, 44, 191, 0.2);
        border: 1px solid rgba(123, 44, 191, 0.4);
        border-radius: 6px;
        padding: 0.3rem 0.6rem;
        margin: 0.2rem;
        font-size: 0.8rem;
        color: #c084fc;
    }
    
    .chunk-preview {
        background: rgba(0, 212, 255, 0.05);
        border-left: 3px solid #00d4ff;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.85rem;
        line-height: 1.5;
        max-height: 120px;
        overflow: hidden;
    }
    
    .preview-label {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

API_URL = os.getenv("API_URL","http://localhost:8000")

NODE_COLORS = {
    "method":      "#3A86FF",
    "metric":      "#00B4D8",
    "dataset":     "#2EC4B6",
    "concept":     "#8338EC",
    "technology":  "#FFBE0B",
    "result":      "#FB5607",
    "problem":     "#D00000",
}

def parse_pdf(pdf_file):
    file_payload = {"file": (pdf_file.name, pdf_file.read(), "application/pdf")}
    response = requests.post(f"{API_URL}/parse-pdf", files=file_payload, timeout=120)
    response.raise_for_status()
    return response.json()

def chunk_sections(sections, filename):
    payload = {"sections": sections, "filename": filename}
    response = requests.post(f"{API_URL}/chunk-sections", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()

def extract_chunk(chunk):
    payload = {"chunk": chunk}
    response = requests.post(f"{API_URL}/extract-chunk", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

def build_agraph_nodes(nodes_data):
    nodes = []
    for node in nodes_data:
        color = NODE_COLORS.get(node.get("type", ""), "#888888")
        nodes.append(Node(
            id=node["id"],
            label=node["label"],
            size=25,
            color=color,
            font={"color": "#ffffff", "size": 14, "strokeWidth": 2, "strokeColor": "#000000"},
            title=f"{node['type'].upper()}\n{node.get('properties', {}).get('description', '') or ''}"
        ))
    return nodes

def build_agraph_edges(edges_data):
    edges = []
    for edge in edges_data:
        edges.append(Edge(
            source=edge["source"],
            target=edge["target"],
            label=edge["relationship"],
            color="#9ca3af",
            font={"color": "#22c55e", "size": 6, "strokeWidth": 1, "strokeColor": "#14532d"}
        ))
    return edges

def get_graph_config():
    return Config(
        width="100%",
        height=700,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#00d4ff",
        collapsible=False,
        node={
            "labelProperty": "label",
            "renderLabel": True,
            "font": {
                "color": "#ffffff",
                "size": 14,
                "strokeWidth": 3,
                "strokeColor": "#000000",
            },
        },
        link={
            "labelProperty": "label",
            "renderLabel": True,
            "font": {
                "color": "#e5e7eb",
                "size": 12,
                "strokeWidth": 3,
                "strokeColor": "#000000",
                "align": "middle",
            },
        }
    )

def get_phase_html(current_phase, phase_results):
    phases = [
        ("📄", "Parsing PDF", "parse"),
        ("✂️", "Chunking Sections", "chunk"),
        ("🧠", "Extracting Knowledge Graph", "extract")
    ]
    
    cards = []
    for icon, name, key in phases:
        if phase_results.get(key):
            cards.append(f'''<div class="phase-card phase-done"><span style="color: #22c55e;">✓</span> {icon} {name}</div>''')
        elif current_phase == key:
            cards.append(f'''<div class="phase-card phase-active"><span style="color: #00d4ff;">●</span> {icon} {name}</div>''')
        else:
            cards.append(f'''<div class="phase-card phase-pending"><span style="color: #6b7280;">○</span> {icon} {name}</div>''')
    
    return f'''<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">{"".join(cards)}</div>'''

def get_sections_preview_html(sections):
    tags = "".join([f'<span class="section-tag">📑 {s["section"]}</span>' for s in sections[:8]])
    more = f'<span class="section-tag">+{len(sections) - 8} more</span>' if len(sections) > 8 else ""
    return f'''<div class="preview-box">
        <div class="preview-label">📄 Detected Sections</div>
        <div>{tags}{more}</div>
    </div>'''

def get_chunks_preview_html(chunks):
    if not chunks:
        return ""
    sample = chunks[0]
    text_preview = sample["text"][:300] + "..." if len(sample["text"]) > 300 else sample["text"]
    section = sample.get("metadata", {}).get("section", "Unknown")
    return f'''<div class="preview-box">
        <div class="preview-label">✂️ Sample Chunk (from "{section}")</div>
        <div class="chunk-preview">{text_preview}</div>
        <div style="color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 0.5rem;">
            Chunk 1 of {len(chunks)} • {sample.get("char_count", 0)} characters
        </div>
    </div>'''

def get_extraction_progress_html(current, total):
    pct = int((current / total) * 100) if total > 0 else 0
    return f'''<div class="preview-box">
        <div class="preview-label">🧠 Extracting entities & relations</div>
        <div style="background: rgba(255,255,255,0.1); border-radius: 4px; height: 8px; margin: 0.5rem 0;">
            <div style="background: linear-gradient(90deg, #7b2cbf, #00d4ff); width: {pct}%; height: 100%; border-radius: 4px; transition: width 0.3s;"></div>
        </div>
        <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Processing chunk {current} of {total}</div>
    </div>'''

st.markdown('<h1 class="main-header"> Axon </h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle"> Agent that extracts knowledge graph from your documents</p>', unsafe_allow_html=True)

st.markdown("### 📤 Upload Document")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    help="Upload a PDF document to extract its text content",
    label_visibility="collapsed"
)

if uploaded_file is not None:
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
    
    if st.button("🧠 Extract Knowledge Graph", use_container_width=True):
        phase_results = {}
        progress_container = st.empty()
        status_container = st.empty()
        preview_container = st.empty()
        
        try:
            # Phase 1: Parse PDF
            progress_container.markdown(get_phase_html("parse", phase_results), unsafe_allow_html=True)
            status_container.info("📄 Parsing PDF and extracting sections...")
            
            uploaded_file.seek(0)
            parse_result = parse_pdf(uploaded_file)
            phase_results["parse"] = parse_result
            
            progress_container.markdown(get_phase_html("chunk", phase_results), unsafe_allow_html=True)
            status_container.success(f"✓ Parsed PDF: {parse_result['section_count']} sections found")
            preview_container.markdown(get_sections_preview_html(parse_result["sections"]), unsafe_allow_html=True)
            
            # Phase 2: Chunk Sections
            status_container.info("✂️ Creating semantic chunks from sections...")
            
            chunk_result = chunk_sections(parse_result["sections"], uploaded_file.name)
            phase_results["chunk"] = chunk_result
            
            progress_container.markdown(get_phase_html("extract", phase_results), unsafe_allow_html=True)
            status_container.success(f"✓ Created {chunk_result['chunk_count']} semantic chunks")
            preview_container.markdown(get_chunks_preview_html(chunk_result["chunks"]), unsafe_allow_html=True)
            
            # Phase 3: Extract Graph (chunk by chunk with progress)
            status_container.info("🧠 Extracting knowledge graph from chunks...")
            
            all_nodes = {}
            all_edges = []
            chunks = chunk_result["chunks"]
            total_chunks = len(chunks)
            
            for i, chunk in enumerate(chunks):
                preview_container.markdown(get_extraction_progress_html(i + 1, total_chunks), unsafe_allow_html=True)
                
                result = extract_chunk(chunk)
                
                for node in result.get("nodes", []):
                    if node["id"] not in all_nodes:
                        all_nodes[node["id"]] = node
                
                for edge in result.get("edges", []):
                    is_duplicate = any(
                        e["source"] == edge["source"] and 
                        e["target"] == edge["target"] and 
                        e["relationship"] == edge["relationship"]
                        for e in all_edges
                    )
                    if not is_duplicate:
                        all_edges.append(edge)
            
            phase_results["extract"] = True
            progress_container.markdown(get_phase_html(None, phase_results), unsafe_allow_html=True)
            status_container.success("✓ Knowledge graph extraction complete!")
            preview_container.empty()
            
            nodes_data = list(all_nodes.values())
            edges_data = all_edges
            chunk_count = total_chunks
            
            if nodes_data:
                st.session_state["graph_nodes"] = nodes_data
                st.session_state["graph_edges"] = edges_data
                st.session_state["chunk_count"] = chunk_count
                st.session_state["section_count"] = parse_result['section_count']
            else:
                st.warning("⚠️ No entities could be extracted from this PDF.")
                
        except Exception as e:
            status_container.error(f"❌ Error: {str(e)}")

    if "graph_nodes" in st.session_state and st.session_state["graph_nodes"]:
        nodes_data = st.session_state["graph_nodes"]
        edges_data = st.session_state["graph_edges"]
        chunk_count = st.session_state["chunk_count"]
        section_count = st.session_state.get("section_count", 0)
        
        st.markdown("### 📊 Extraction Results")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📑 Sections", section_count)
        with col2:
            st.metric("📄 Chunks", chunk_count)
        with col3:
            st.metric("🔷 Entities", len(nodes_data))
        with col4:
            st.metric("🔗 Relations", len(edges_data))
        
        st.markdown("### 🎨 Entity Types")
        legend_cols = st.columns(len(NODE_COLORS))
        for i, (entity_type, color) in enumerate(NODE_COLORS.items()):
            with legend_cols[i]:
                st.markdown(
                    f'<span style="color:{color}; font-weight:bold;">●</span> {entity_type.capitalize()}',
                    unsafe_allow_html=True
                )
        
        st.markdown("### 🕸️ Knowledge Graph")
        
        agraph_nodes = build_agraph_nodes(nodes_data)
        agraph_edges = build_agraph_edges(edges_data)
        config = get_graph_config()
        
        agraph(nodes=agraph_nodes, edges=agraph_edges, config=config)
        
        with st.expander("📋 View All Entities"):
            for node in nodes_data:
                color = NODE_COLORS.get(node.get("type", ""), "#888888")
                st.markdown(
                    f'<span style="color:{color};">●</span> **{node["label"]}** ({node["type"]})',
                    unsafe_allow_html=True
                )
                if node.get("properties", {}).get("description"):
                    st.caption(node["properties"]["description"])
        
        with st.expander("🔗 View All Relations"):
            for edge in edges_data:
                st.markdown(f'`{edge["source"]}` → **{edge["relationship"]}** → `{edge["target"]}`')

else:
    st.markdown("""
    <div class="upload-card">
        <h3 style="color: rgba(255,255,255,0.7); margin-bottom: 1rem;">👆 Drop your Scientific Paper here</h3>
        <p style="color: rgba(255,255,255,0.5);">Supported format: PDF</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    """
    <center>
        <small style='color: rgba(255,255,255,0.4);'>
            <a href='https://status.axon-agent.online/status/axon' target='_blank' style='color: #22c55e; text-decoration: none;'>
                🟢 System Status
            </a>
            &nbsp;•&nbsp;
            Made by <a href='https://github.com/G0rg0ne' target='_blank' style='color: rgba(255,255,255,0.4); text-decoration: underline;'>Gorgone</a> - 2025
        </small>
    </center>
    """,
    unsafe_allow_html=True
)
