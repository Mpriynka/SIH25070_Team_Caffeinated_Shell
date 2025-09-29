import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def load_json(json_file):
    """Load JSON data from file"""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def build_table(data_dict):
    """Return a ReportLab Table with bold keys and values, no extra line breaks"""
    table_data = [[f"{k.replace('_',' ').title()}:", v] for k, v in data_dict.items()]
    table = Table(table_data, colWidths=[200, 310])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),  # keys bold
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6)
    ]))
    return table

def generate_pdf(data, filename):
    doc = SimpleDocTemplate(
        filename, pagesize=letter,
        rightMargin=30, leftMargin=30,
        topMargin=30, bottomMargin=120  # extra bottom space for stamp/signature
    )
    elements = []
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    heading = ParagraphStyle('Heading2Bold', parent=styles['Heading2'], fontSize=14, leading=16, spaceAfter=10)

    # --- Title ---
    elements.append(Paragraph("MEDIA SANITIZATION REPORT", styles['Title']))
    elements.append(Spacer(1, 10))

    # --- UUID ---
    report_uuid = data.get("report_uuid", "N/A")
    elements.append(Paragraph(f"<b>Report ID:</b> {report_uuid}", normal))
    elements.append(Spacer(1, 20))

    # --- Section 1: Person Performing Sanitization ---
    elements.append(Paragraph("1. Person Performing Sanitization", heading))
    elements.append(build_table(data.get("personPerformingSanitization", {})))
    elements.append(Spacer(1, 15))

    # --- Section 2: Media Information ---
    elements.append(Paragraph("2. Media Information", heading))
    elements.append(build_table(data.get("mediaInformation", {})))
    elements.append(Spacer(1, 15))

    # --- Section 3: Sanitization Details ---
    elements.append(Paragraph("3. Sanitization Details", heading))
    elements.append(build_table(data.get("sanitizationDetails", {})))
    elements.append(Spacer(1, 15))

    # --- Section 4: Media Destination ---
    elements.append(Paragraph("4. Media Destination", heading))
    elements.append(build_table(data.get("mediaDestination", {})))
    elements.append(Spacer(1, 15))

    # --- Section 5: Validation ---
    elements.append(Paragraph("5. Validation", heading))
    elements.append(build_table(data.get("validation", {})))
    elements.append(Spacer(1, 80))  # Leave extra space for signature/stamp

    # --- Build PDF ---
    doc.build(elements)
    print(f"PDF generated: {filename}")
