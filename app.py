import streamlit as st
import fitz  # PyMuPDF
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# Page Configuration
st.set_page_config(page_title="Price List Discount Calculator", layout="wide")

st.title("⚡ Electrical Price List Discount & PDF Modifier")
st.write("উচ্চ সাইজের পিডিএফ প্রাইস লিস্ট আপলোড করুন এবং সিক্যুয়েন্শাল ডিসকাউন্ট প্রয়োগ করে নতুন পিডিএফ জেনারেট করুন।")

# Sidebar - Multi-tier Discount Inputs
st.sidebar.header("Discount Settings (%)")
d1 = st.sidebar.number_input("Discount 1 (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
d2 = st.sidebar.number_input("Discount 2 (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
d3 = st.sidebar.number_input("Discount 3 (%) [Optional]", min_value=0.0, max_value=100.0, value=0.0, step=0.5)

# File Uploader (Supports up to 10MB or more)
uploaded_file = st.file_uploader("Upload Price List PDF (Max 10MB+)", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    file_size_mb = len(pdf_bytes) / (1024 * 1024)
    st.info(f"Uploaded File Size: {file_size_mb:.2f} MB")

    if st.button("Process PDF & Extract Prices"):
        with st.spinner("পিডিএফ প্রসেস করা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন..."):
            # Open PDF with PyMuPDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            extracted_items = []

            # Regex to detect prices (e.g., 150, 1,250.00)
            price_pattern = re.compile(r'\\b\\d{1,3}(?:,\\d{3})*(?:\\.\\d{2})?\\b')

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                lines = text.split('\\n')

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    matches = price_pattern.findall(line)
                    if matches:
                        try:
                            # Taking the last matched number in the line as MRP/Price
                            price_str = matches[-1].replace(',', '')
                            mrp = float(price_str)

                            # Filter out very small numbers (like page numbers or item codes)
                            if mrp > 10:
                                desc = line.replace(matches[-1], '').strip()
                                if not desc:
                                    desc = f"Product Item (Page {page_num + 1})"
                                extracted_items.append({"desc": desc, "mrp": mrp})
                        except ValueError:
                            continue

            # Store in session state for later use
            st.session_state['extracted_items'] = extracted_items
            st.success(f"সফলভাবে {len(extracted_items)}টি আইটেমের প্রাইস ডিটেক্ট করা হয়েছে!")

    # If items are extracted, show preview and download option
    if 'extracted_items' in st.session_state and st.session_state['extracted_items']:
        items = st.session_state['extracted_items']

        # Multi-tier discount calculation formula
        def calculate_net(mrp):
            net = mrp
            if d1 > 0:
                net *= (1 - d1 / 100.0)
            if d2 > 0:
                net *= (1 - d2 / 100.0)
            if d3 > 0:
                net *= (1 - d3 / 100.0)
            return round(net, 2)

        preview_data = []
        table_data = [["Product Description", "MRP (₹)", "Net Discounted Price (₹)"]]

        for item in items:
            net_price = calculate_net(item['mrp'])
            preview_data.append({
                "Description": item['desc'],
                "MRP (₹)": item['mrp'],
                "Net Price (₹)": net_price
            })
            table_data.append([item['desc'], f"₹{item['mrp']:.2f}", f"₹{net_price:.2f}"])

        st.subheader("প্রাইস প্রিভিউ এবং ক্যালকুলেশন টেবিল")
        st.dataframe(preview_data, use_container_width=True)

        # Generate Modified PDF Button
        if st.button("Generate Revised PDF Price List"):
            buffer = io.BytesIO()
            pdf_doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=14,
                alignment=1,
                spaceAfter=15
            )

            elements.append(Paragraph("<b>Revised Price List - Discounted Version</b>", title_style))
            elements.append(Paragraph(f"Applied Discounts -> D1: {d1}% | D2: {d2}% | D3: {d3}%", styles['Normal']))
            elements.append(Spacer(1, 10))

            # Create Table for ReportLab PDF
            t = Table(table_data, colWidths=[260, 110, 110])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0284c7")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]))

            elements.append(t)
            pdf_doc.build(elements)

            pdf_data = buffer.getvalue()
            buffer.close()

            st.download_button(
                label="📥 Download Modified Price List PDF",
                data=pdf_data,
                file_name="Modified_Price_List.pdf",
                mime="application/pdf"
            )
