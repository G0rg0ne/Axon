import streamlit as st
import os
import requests
from streamlit_agraph import agraph, Node, Edge, Config

# Page configuration
st.set_page_config(
    page_title="Axon",
    page_icon="🌐",
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


# Extract text from PDF
API_URL = os.getenv("API_URL","http://localhost:8000")

# Color mapping for different entity types
NODE_COLORS = {
    "method":      "#3A86FF",  # Strong blue
    "metric":      "#00B4D8",  # Cyan (clearly distinct from blue)
    "dataset":     "#2EC4B6",  # Green-teal
    "concept":     "#8338EC",  # Violet
    "technology":  "#FFBE0B",  # Yellow / gold
    "result":      "#FB5607",  # Bright orange
    "problem":     "#D00000",  # Deep red
}

def extract_knowledge_graph(pdf_file):
    """Extract knowledge graph from PDF via API"""
    file_payload = {"file": (pdf_file.name, pdf_file.read(), "application/pdf")}
    response = requests.post(f"{API_URL}/extract-text", files=file_payload, timeout=300)
    return response.json()

def build_agraph_nodes(nodes_data):
    """Convert API nodes to agraph Node objects"""
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
    """Convert API edges to agraph Edge objects"""
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
    """Configure the graph visualization"""
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

# Main Header
st.markdown('<h1 class="main-header"> Axon </h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle"> Agent that helps you to summarize your scientific paper </p>', unsafe_allow_html=True)

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
    if st.button("🧠 Extract Knowledge Graph", use_container_width=True):
        with st.spinner("Extracting knowledge graph from PDF... This may take a moment."):
            try:
                uploaded_file.seek(0)
                response = extract_knowledge_graph(uploaded_file)
                
                graph_data = response.get("graph", {})
                nodes_data = graph_data.get("nodes", [])
                edges_data = graph_data.get("edges", [])
                chunk_count = response.get("chunk_count", 0)
                
                if nodes_data:
                    # Store in session state for persistence
                    st.session_state["graph_nodes"] = nodes_data
                    st.session_state["graph_edges"] = edges_data
                    st.session_state["chunk_count"] = chunk_count
                else:
                    st.warning("⚠️ No entities could be extracted from this PDF.")
                    
            except Exception as e:
                st.error(f"❌ Error extracting knowledge graph: {str(e)}")

    # Display graph if available in session state
    if "graph_nodes" in st.session_state and st.session_state["graph_nodes"]:
        nodes_data = st.session_state["graph_nodes"]
        edges_data = st.session_state["graph_edges"]
        chunk_count = st.session_state["chunk_count"]
        
        # Show extraction stats
        st.markdown("### 📊 Extraction Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔷 Entities", len(nodes_data))
        with col2:
            st.metric("🔗 Relations", len(edges_data))
        with col3:
            st.metric("📄 Chunks", chunk_count)
        
        # Entity type legend
        st.markdown("### 🎨 Entity Types")
        legend_cols = st.columns(len(NODE_COLORS))
        for i, (entity_type, color) in enumerate(NODE_COLORS.items()):
            with legend_cols[i]:
                st.markdown(
                    f'<span style="color:{color}; font-weight:bold;">●</span> {entity_type.capitalize()}',
                    unsafe_allow_html=True
                )
        
        # Render interactive graph
        st.markdown("### 🕸️ Knowledge Graph")
        
        agraph_nodes = build_agraph_nodes(nodes_data)
        agraph_edges = build_agraph_edges(edges_data)
        config = get_graph_config()
        
        agraph(nodes=agraph_nodes, edges=agraph_edges, config=config)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show entities and relations in expandable sections
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
    "<center><small style='color: rgba(255,255,255,0.4);'> Made by <a href='https://github.com/G0rg0ne' target='_blank' style='color: rgba(255,255,255,0.4); text-decoration: underline;'>Gorgone</a> - 2025 </small></center>",
    unsafe_allow_html=True
)
