import streamlit as st
import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import tempfile
import os

st.title("Polycab Wires Discounted Price List Generator")
st.write("আপনার পলিকাভ প্রাইস লিস্টের পিডিএফ ফাইলটি নিচে আপলোড করুন (৩২% থেকে ৩৭% লেস সহ নতুন পিডিএফ তৈরি করার জন্য)।")

# ওয়েবসাইট থেকে ফাইল আপলোড করার উইজেট
uploaded_file = st.file_uploader("Upload Polycab PDF Price List", type=["pdf"])

if uploaded_file is not None:
    # আপলোড করা ফাইলটিকে টেম্পোরারি ফাইলে রূপান্তর করা
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_input_path = tmp_file.name

    output_pdf_path = "Polycab_Discounted_Price_List.pdf"
    
    if st.button("Generate Discounted PDF"):
        with st.spinner("Processing PDF... Please wait."):
            try:
                discounts = [32, 33, 34, 35, 36, 37]
                categories_data = []
                
                # পিডিএফ থেকে ডেটা রিড করা
                with pdfplumber.open(temp_input_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        tables = page.extract_tables()
                        for table in tables:
                            is_valid_table = any(
                                any(keyword in str(cell).upper() for keyword in ['SIZE', 'LP', 'SQ.MM']) 
                                for row in table for cell in row
                            )
                            if is_valid_table and len(table) > 1:
                                categories_data.append((f"Page {page_num + 1} Table", table))

                # নতুন পিডিএফ তৈরি করা
                doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
                story = []
                styles = getSampleStyleSheet()
                
                title_style = ParagraphStyle(
                    'TitleStyle',
                    parent=styles['Heading1'],
                    fontSize=16,
                    spaceAfter=12
                )
                
                story.append(Paragraph("Polycab Wires Discounted Price List (32% to 37% Less)", title_style))
                story.append(Spacer(1, 10))

                for cat_name, table in categories_data:
                    story.append(Paragraph(cat_name, styles['Heading2']))
                    header = table[0] + [f"{d}% Less" for d in discounts]
                    new_table = [header]
                    
                    for row in table[1:]:
                        lp_val = None
                        for cell in row:
                            if cell:
                                cleaned_cell = str(cell).replace(',', '').strip()
                                if cleaned_cell.replace('.', '', 1).isdigit():
                                    lp_val = float(cleaned_cell)
                                    break
                        
                        new_row = list(row)
                        if lp_val is not None:
                            for d in discounts:
                                discounted_price = lp_val * (1 - d / 100.0)
                                new_row.append(f"{discounted_price:.2f}")
                        else:
                            for d in discounts:
                                new_row.append("")
                        new_table.append(new_row)
                        
                    t = Table(new_table)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9f9')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7'))
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 15))

                doc.build(story)
                
                st.success("Successfully generated discounted PDF!")
                
                # ডাউনলোড বাটন তৈরি
                with open(output_pdf_path, "rb") as file:
                    st.download_button(
                        label="Download Discounted PDF",
                        data=file,
                        file_name="Polycab_Discounted_Price_List.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
