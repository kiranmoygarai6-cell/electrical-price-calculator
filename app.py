import streamlit as st
import fitz  # PyMuPDF
import re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# Page Configuration
st.set_page_config(page_title="GARAI ELECTRICAL - Professional Price List", layout="wide")

st.title("⚡ GARAI ELECTRICAL - Professional Discount Calculator & Price List")
st.write("ইলেকট্রিক্যাল প্রাইস লিস্ট পিডিএফ আপলোড করুন এবং এক ক্লিকে Less 30% থেকে Less 39% পর্যন্ত ডিসকাউন্ট চার্ট জেনারেট করুন।")

# Header & Product Inputs
col1, col2 = st.columns(2)
with col1:
    company_title = st.text_input("Company / Header Name", value="GARAI ELECTRICAL")
with col2:
    product_name = st.text_input("Product Line Name / Category", value="POLYCAB / HAVELLS WIRES & CABLES")

# Default discount rates from 30% to 39% as requested
default_discounts = "30, 31, 32, 33, 34, 35, 36, 37, 38, 39"
discount_input = st.sidebar.text_input("Discount Rates (%)", value=default_discounts)

# File Uploader
uploaded_file = st.file_uploader("Upload Price List PDF (Max 10MB+)", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    file_size_mb = len(pdf_bytes) / (1024 * 1024)
    st.info(f"Uploaded File Size: {file_size_mb:.2f} MB")

    # Automatic One-Click Processing
    if st.button("🚀 Process PDF & Generate Discount Chart") or True:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        extracted_items = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            lines = text.split('\n')
            
            for i in range(len(lines)):
                line = lines[i].strip()
                # Match standard wire/cable sizes or item specs
                if re.match(r'^(0\.75|1(\.0)?|1\.5|2\.5|4|6|10|16|25|35|50|[0-9]+(\.[0-9]+)?\s*(sq\.?\s*mm|sqmm|MM|mm)?)$', line, re.IGNORECASE):
                    size_val = line
                    desc = "Standard Wire/Cable"
                    # Look backwards for description if available
                    if i > 0:
                        desc = lines[i-1].strip()
                    
                    # Look forward for MRP
                    for j in range(i+1, min(i+6, len(lines))):
                        potential_price = lines[j].replace(',', '').strip()
                        if re.match(r'^\d{3,6}(\.\d{2})?$', potential_price):
                            mrp_val = float(potential_price)
                            if mrp_val > 50:
                                extracted_items.append({"desc": desc, "size": size_val, "mrp": mrp_val})
                                break

        # Fallback general number extraction if specific sizes aren't matched neatly
        if not extracted_items:
            price_pattern = re.compile(r'\b\d{3,6}(?:\.\d{2})?\b')
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    matches = price_pattern.findall(line)
                    if matches:
                        try:
                            mrp = float(matches[-1].replace(',', ''))
                            if mrp >= 50:
                                desc = line.replace(matches[-1], '').strip()
                                if not desc:
                                    desc = f"Electrical Item (Page {page_num + 1})"
                                extracted_items.append({"desc": desc, "size": "N/A", "mrp": mrp})
                        except ValueError:
                            continue

        # Remove duplicates
        unique_items = []
        seen = set()
        for item in extracted_items:
            identifier = (item['desc'], item['size'], item['mrp'])
            if identifier not in seen:
                seen.add(identifier)
                unique_items.append(item)
        
        st.session_state['garai_items'] = unique_items
        if unique_items:
            st.success(f"সফলভাবে {len(unique_items)}টি প্রডাক্ট আইটেম ও প্রাইস ডিটেক্ট করা হয়েছে!")

    # Display Preview & Download if items exist
    if 'garai_items' in st.session_state and st.session_state['garai_items']:
        items = st.session_state['garai_items']
        
        try:
            discounts = [float(d.strip()) for d in discount_input.split(',')]
        except:
            discounts = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39]

        table_headers = ["Description / Size", "MRP (₹)"] + [f"Less {d}%\n(₹)" for d in discounts]
        table_data = [table_headers]

        preview_rows = []
        for item in items:
            row = [f"{item['desc']} ({item['size']})", f"₹{item['mrp']:.2f}"]
            preview_row = {"Item": f"{item['desc']} ({item['size']})", "MRP (₹)": item['mrp']}
            
            for d in discounts:
                # Formula: MRP * (100 - Discount Percentage) / 100
                net = round(item['mrp'] * (100 - d) / 100.0, 2)
                row.append(f"₹{net:.2f}")
                preview_row[f"Less {d}%"] = net
                
            table_data.append(row)
            preview_rows.append(preview_row)

        st.subheader("📊 GARAI ELECTRICAL - Discount Price Preview")
        st.dataframe(preview_rows, use_container_width=True)

        # Generate Professional PDF
        if st.button("📥 Download Professional PDF Price List"):
            buffer = io.BytesIO()
            # Landscape A4 to fit multiple discount columns cleanly
            pdf_doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=15, leftMargin=15, topMargin=15, bottomMargin=15)
            elements = []
            
            # Header Box
            header_data = [[
                Paragraph(f"<b>{company_title}</b><br/><font size=9>Andalmore, Paschim Bardhaman, West Bengal</font>", ParagraphStyle('H1', textColor=colors.whitesmoke, fontSize=15, fontName='Helvetica-Bold')),
                Paragraph(f"<b>{product_name}</b>", ParagraphStyle('H2', textColor=colors.whitesmoke, fontSize=13, fontName='Helvetica-Bold', alignment=2))
            ]]
            header_table = Table(header_data, colWidths=[400, 440])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 10))
            
            elements.append(Paragraph("<b>WHOLESALE & RETAIL DISCOUNT PRICE LIST (MRP & Net Rates)</b>", ParagraphStyle('Sub', fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor("#334155"))))
            elements.append(Spacer(1, 8))
            
            # Table Column Widths (Adjusted for 12 columns total)
            col_w = [180, 70] + [590 / len(discounts)] * len(discounts)
            
            chart_table = Table(table_data, colWidths=col_w)
            chart_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")), # Professional Blue Header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'), # Left align descriptions
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]))
            
            elements.append(chart_table)
            pdf_doc.build(elements)
            
            pdf_data = buffer.getvalue()
            buffer.close()
            
            st.download_button(
                label="Click here to save Garai Electrical PDF",
                data=pdf_data,
                file_name="Garai_Electrical_Discount_Price_List.pdf",
                mime="application/pdf"
            )
