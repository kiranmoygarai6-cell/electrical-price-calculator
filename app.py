import streamlit as st
import fitz  # PyMuPDF
import re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# Page Configuration
st.set_page_config(page_title="Garai Electrical Price Chart Generator", layout="wide")

st.title("⚡ Garai Electrical - Multi-Tier Discount Chart Generator")
st.write("আপনার প্রফেশনাল প্রাইস লিস্ট এবং মাল্টি-টিয়ার ডিসকাউন্ট চার্ট তৈরি করুন।")

# Header & Product Inputs
col1, col2 = st.columns(2)
with col1:
    company_title = st.text_input("Company / Header Name", value="GARAI ELECTRICAL")
with col2:
    product_name = st.text_input("Product Line Name", value="POLYCAB GREEN WIRE+")

# Sidebar - Discount Tiers Setup
st.sidebar.header("Discount Tiers Setup (%)")
discount_input = st.sidebar.text_input("Enter discounts separated by comma", value="34, 34.5, 35, 35.5, 36, 36.5, 37")

# File Uploader
uploaded_file = st.file_uploader("Upload Price List PDF", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    file_size_mb = len(pdf_bytes) / (1024 * 1024)
    st.info(f"Uploaded File Size: {file_size_mb:.2f} MB")

    if st.button("Process & Generate Chart Table"):
        with st.spinner("পিডিএফ থেকে সাইজ এবং এমআরপি এক্সট্রাক্ট করা হচ্ছে..."):
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            extracted_items = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                lines = text.split('\n')
                
                for i in range(len(lines)):
                    line = lines[i].strip()
                    # Match standard wire sizes (0.75, 1, 1.5, 2.5, 4, 6, etc.)
                    if re.match(r'^(0\.75|1(\.0)?|1\.5|2\.5|4|6|10|16|25|35|50)$', line):
                        size_val = line
                        # Look for the MRP in nearby lines
                        for j in range(i+1, min(i+5, len(lines))):
                            potential_price = lines[j].replace(',', '').strip()
                            if re.match(r'^\d{3,6}(\.\d{2})?$', potential_price):
                                mrp_val = float(potential_price)
                                if mrp_val > 50:
                                    extracted_items.append({"size": size_val, "mrp": mrp_val})
                                    break

            # Remove duplicates based on size
            unique_items = []
            seen_sizes = set()
            for item in extracted_items:
                if item['size'] not in seen_sizes:
                    seen_sizes.add(item['size'])
                    unique_items.append(item)
            
            st.session_state['chart_items'] = unique_items
            st.success(f"সফলভাবে {len(unique_items)}টি সাইজ ও প্রাইস ডিটেক্ট করা হয়েছে!")

    # If items are extracted, show multi-tier discount chart preview
    if 'chart_items' in st.session_state and st.session_state['chart_items']:
        items = st.session_state['chart_items']
        
        try:
            discounts = [float(d.strip()) for d in discount_input.split(',')]
        except:
            discounts = [34.0, 35.0, 36.0]

        table_headers = ["SIZE (SQ.MM.)", "MRP (₹)"] + [f"LESS {d}%\nNET RATE (₹)" for d in discounts]
        table_data = [table_headers]

        preview_rows = []
        for item in items:
            row = [item['size'], f"₹{item['mrp']:.2f}"]
            preview_row = {"Size (Sq. Mm.)": item['size'], "MRP (₹)": item['mrp']}
            for d in discounts:
                net = round(item['mrp'] * (1 - d / 100.0), 2)
                row.append(f"₹{net:.2f}")
                preview_row[f"Less {d}%"] = net
            table_data.append(row)
            preview_rows.append(preview_row)

        st.subheader("📊 মাল্টি-টিয়ার ডিসকাউন্ট প্রাইস চার্ট প্রিভিউ")
        st.dataframe(preview_rows, use_container_width=True)

        # Generate Professional PDF Chart Button
        if st.button("Generate Professional PDF Chart"):
            buffer = io.BytesIO()
            # Landscape layout for wide discount charts
            pdf_doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
            elements = []
            
            # Header Box (Garai Electrical Style)
            header_data = [[
                Paragraph(f"<b>{company_title}</b>", ParagraphStyle('H1', textColor=colors.whitesmoke, fontSize=16, fontName='Helvetica-Bold')),
                Paragraph(f"<b>{product_name}</b>", ParagraphStyle('H2', textColor=colors.whitesmoke, fontSize=14, fontName='Helvetica-Bold', alignment=2))
            ]]
            header_table = Table(header_data, colWidths=[380, 380])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1e293b")),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 15),
                ('RIGHTPADDING', (0,0), (-1,-1), 15),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 15))
            
            # Subtitle
            elements.append(Paragraph("<b>MRP / LIST PRICE DISCOUNT CHART - 90 METER BOX</b>", ParagraphStyle('Sub', fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor("#334155"))))
            elements.append(Spacer(1, 10))
            
            # Dynamic Column Widths Calculation
            num_cols = len(table_headers)
            col_w = [90, 80] + [560 / (num_cols - 2)] * (num_cols - 2)
            
            chart_table = Table(table_data, colWidths=col_w)
            chart_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#16a34a")), # Professional Green Header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]))
            
            elements.append(chart_table)
            pdf_doc.build(elements)
            
            pdf_data = buffer.getvalue()
            buffer.close()
            
            st.download_button(
                label="📥 Download Professional Price Chart PDF",
                data=pdf_data,
                file_name="Garai_Electrical_Price_Chart.pdf",
                mime="application/pdf"
            )
