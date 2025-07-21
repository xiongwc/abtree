import xml.etree.ElementTree as ET

import streamlit as st

from abtree.parser.tree_builder import TreeBuilder
from abtree.parser.xml_parser import XMLParser

st.set_page_config(page_title="ABTree XML Visual Editor", layout="wide")
st.title("ABTree XML Visualization and Interactive Editing")

# File upload
uploaded_file = st.file_uploader("Upload behavior tree XML file", type=["xml"])
xml_text = ""
if uploaded_file:
    xml_text = uploaded_file.read().decode("utf-8")
else:
    xml_text = st.text_area("Or paste XML content", height=200)

# Parse XML
tree = None
parser = XMLParser()
if xml_text.strip():
    try:
        tree = parser.parse_string(xml_text)
        st.success("XML parsing successful!")
    except Exception as e:
        st.error(f"XML parsing failed: {e}")


# Visualize tree structure
def render_node(node, parent_key="root"):
    key = f"{parent_key}-{node.name}"
    with st.expander(f"{node.__class__.__name__}: {node.name}", expanded=True):
        # Attribute editing
        for attr in node.__dict__:
            if attr in ["children", "parent", "status", "_last_tick_time"]:
                continue
            value = getattr(node, attr)
            st.text_input(f"{attr}", value=str(value), key=f"{key}-{attr}")
        # Child node recursion
        for i, child in enumerate(getattr(node, "children", [])):
            render_node(child, parent_key=key)


if tree:
    st.subheader("Behavior Tree Structure")
    render_node(tree.root)

# Real-time XML preview and export
if tree:
    builder = TreeBuilder()
    xml_out = builder.export_to_xml(tree)
    st.subheader("Real-time XML Preview")
    st.code(xml_out, language="xml")
    st.download_button("Export XML", xml_out, file_name="abtree.xml", mime="text/xml")
