import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_discounted_pdf(input_pdf_path, output_pdf_path):
    # ৩২% থেকে ৩৭% পর্যন্ত ডিসকাউন্টের পার্সেন্টেজ তালিকা
    discounts = [32, 33, 34, 35, 36, 37]
    categories_data = []
    
    # পিডিএফ থেকে টেবিল ডেটা রিড করা
    with pdfplumber.open(input_pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                # টেবিলগুলোর মধ্যে সাইজ এবং এলপি (LP) কলাম আছে কিনা চেক করা
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
        
        # নতুন টেবিল হেডার তৈরি (মূল হেডার + ডিসকাউন্ট কলামসমূহ)
        header = table[0] + [f"{d}% Less" for d in discounts]
        new_table = [header]
        
        # প্রতিটি রো-তে লিস্ট প্রাইস (LP) খুঁজে বের করে ডিসকাউন্ট হিসাব করা
        for row in table[1:]:
            lp_val = None
            for cell in row:
                if cell:
                    # পরিষ্কার করে সংখ্যা বা প্রাইস খুঁজে বের করা
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
            
        # টেবিল স্টাইলিং ও ফরম্যাটিং
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

    # পিডিএফ ফাইল বিল্ড করা
    doc.build(story)
    print(f"Success! Discounted PDF generated: {output_pdf_path}")

# কোড রান করার জন্য নিচের ফাংশনটি কল করুন:
if __name__ == "__main__":
    input_file = "Polycab 90-180 Mtrs. Wires LP Dtd 20th October 2026.pdf"
    output_file = "Polycab_Discounted_Price_List.pdf"
    generate_discounted_pdf(input_file, output_file)
