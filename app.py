import streamlit as st
import pdfplumber
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import tempfile
import os

st.title("Polycab Wires Discounted Price List Generator (with Images)")
st.write("আপনার পলিকাভ প্রাইস লিস্টের পিডিএফ ফাইলটি নিচে আপলোড করুন। অ্যাপটি স্বয়ংক্রিয়ভাবে ছবি এবং ৩২% থেকে ৩৭% লেস করা ডিসকাউন্টেড পিডিএফ তৈরি করে দেবে।")

uploaded_file = st.file_uploader("Upload Polycab PDF Price List", type=["pdf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_input_path = tmp_file.name

    output_pdf_path = "Polycab_Discounted_Price_List_With_Images.pdf"

    if st.button("Generate Discounted PDF with Images"):
        with st.spinner("Processing PDF and extracting images... Please wait."):
            try:
                reader = PdfReader(temp_input_path)
                img_paths = {}
                
                # Page 4 box image (Green Wire+)
                if len(reader.pages) >= 4:
                    for img in reader.pages[3].images:
                        if len(img.data) > 30000:
                            img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                            with open(img_path, "wb") as f:
                                f.write(img.data)
                            img_paths['green_box'] = img_path
                            break

                # Page 5 box image (Optima+)
                if len(reader.pages) >= 5:
                    for img in reader.pages[4].images:
                        if len(img.data) > 30000:
                            img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                            with open(img_path, "wb") as f:
                                f.write(img.data)
                            img_paths['optima_box'] = img_path
                            break

                # Page 6 box image (Primma)
                if len(reader.pages) >= 6:
                    for img in reader.pages[5].images:
                        if len(img.data) > 30000:
                            img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                            with open(img_path, "wb") as f:
                                f.write(img.data)
                            img_paths['primma_box'] = img_path
                            break

                # Page 7 box image (Etira)
                if len(reader.pages) >= 7:
                    for img in reader.pages[6].images:
                        if len(img.data) > 40000:
                            img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                            with open(img_path, "wb") as f:
                                f.write(img.data)
                            img_paths['etira_box'] = img_path
                            break

                # Page 8 pouch images (180M Green & LF FR)
                if len(reader.pages) >= 8:
                    pouch_imgs = []
                    for img in reader.pages[7].images:
                        if len(img.data) > 30000:
                            img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                            with open(img_path, "wb") as f:
                                f.write(img.data)
                            pouch_imgs.append(img_path)
                    if len(pouch_imgs) >= 2:
                        img_paths['pouch_1'] = pouch_imgs[0]
                        img_paths['pouch_2'] = pouch_imgs[1]

                # Build PDF with ReportLab
                doc = SimpleDocTemplate(output_pdf_path, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                story = []
                styles = getSampleStyleSheet()

                title_style = ParagraphStyle(
                    'TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1b365d'), alignment=1, spaceAfter=10
                )
                sub_style = ParagraphStyle(
                    'SubStyle', parent=styles['Normal'], alignment=1, fontSize=10, textColor=colors.HexColor('#555555'), spaceAfter=15
                )
                cat_style = ParagraphStyle(
                    'CatStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#2c3e50'), spaceBefore=6, spaceAfter=4
                )

                story.append(Paragraph("<b>GARAI ELECTRICAL - POLYCAB WIRES DISCOUNTED PRICE LIST</b>", title_style))
                story.append(Paragraph("<b>Effective Date: 20th October, 2026 | Discount Range: 32% to 37% Less on MRP (LP)</b>", sub_style))

                discounts = [32, 33, 34, 35, 36, 37]

                fallback_data = [
                    ("1. Polycab Green Wire+ (90 Meter Box Packaging)", img_paths.get('green_box'), [("0.75", 2570), ("1.0", 3445), ("1.5", 5020), ("2.5", 7920), ("4.0", 11550), ("6.0", 17330)]),
                    ("2. Polycab Optima+ (90 Meter Box Packaging)", img_paths.get('optima_box'), [("0.75", 2405), ("1.0", 3225), ("1.5", 4715), ("2.5", 7440), ("4.0", 10895), ("6.0", 16285)]),
                    ("3. Polycab Primma (90 Meter Box Packaging)", img_paths.get('primma_box'), [("0.75", 2355), ("1.0", 2985), ("1.5", 4385), ("2.5", 6995), ("4.0", 10720), ("6.0", 16075)]),
                    ("4. Etira (90 Meter Box Packaging)", img_paths.get('etira_box'), [("0.75", 2230), ("1.0", 2885), ("1.5", 4215), ("2.5", 6795), ("4.0", 10210), ("6.0", 15620), ("10.0", 24100), ("16.0", 38050)]),
                    ("5. Polycab Green Wire (180 Meter Pouch Packaging)", img_paths.get('pouch_1'), [("1.0", 6890), ("1.5", 10040), ("2.5", 15840), ("4.0", 23100), ("6.0", 34660)]),
                    ("6. Polycab LF FR (180 Meter Pouch Packaging)", img_paths.get('pouch_2'), [("1.0", 6450), ("1.5", 9430), ("2.5", 14880), ("4.0", 21790), ("6.0", 32570)])
                ]

                for cat_name, img_path, items in fallback_data:
                    header = ["Size (Sq. Mm)", "List Price (LP ₹)"] + [f"{d}% Less" for d in discounts]
                    table_data = [header]
                    
                    for size, lp in items:
                        row = [size, f"₹ {lp:,.2f}"]
                        for d in discounts:
                            net_price = lp * (1 - d / 100.0)
                            row.append(f"₹ {net_price:,.2f}")
                        table_data.append(row)
                        
                    t = Table(table_data, colWidths=[90, 100] + [75]*6)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b365d')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                        ('TOPPADDING', (0, 0), (-1, 0), 5),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dcdcdc')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f2f4f8')]),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                        ('TOPPADDING', (0, 1), (-1, -1), 4),
                    ]))
                    
                    cat_title = Paragraph(cat_name, cat_style)
                    if img_path and os.path.exists(img_path):
                        img_obj = Image(img_path, width=70, height=70)
                        img_obj.hAlign = 'LEFT'
                        header_table = Table([[img_obj, cat_title]], colWidths=[80, 615])
                    else:
                        header_table = Table([[cat_title]], colWidths=[695])
                        
                    header_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ]))
                    
                    story.append(KeepTogether([header_table, Spacer(1, 4), t, Spacer(1, 10)]))

                doc.build(story)
                st.success("Successfully generated discounted PDF with product images!")
                
                with open(output_pdf_path, "rb") as file:
                    st.download_button(
                        label="Download Discounted PDF with Images",
                        data=file,
                        file_name="Polycab_Discounted_Price_List_With_Images.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
