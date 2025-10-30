import pandas as pd
from reportlab.lib.pagesizes import letter, A1, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import PIL.Image
from reportlab.platypus import Image as PlatypusImage


from reportlab.graphics.shapes import *


def create_report(proj_details, report_title, report_sub_title, project_ga, project_sat):

    # Define Colors 
    prevalon_lavendar = colors.Color(220/256,207/256,235/256)
    prevalon_purple = colors.Color(127/256,81/256,185/256)
    # Create a list to hold the contents of the PDF
    content = []

    # Define styles
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]

    # Define header and footer function with image from URL
    def header(canvas, doc):
        
        canvas.saveState()
        img = PIL.Image.open('Prevalon Logo.png')
        img_reader = ImageReader(img)
        
        header_left_size = 1*inch
        canvas.drawImage(img_reader, 25, doc.bottomMargin + doc.height + doc.topMargin - header_left_size, width=header_left_size*1.827852998065764, height=header_left_size)  # Adjust image dimensions and position as needed

        # Define the text to be wrapped
        text = "400 International Parkway, Suite 200, Heathrow, FL 32746"

        # Set the position and dimensions for drawing the text
        width = 150
        x = doc.leftMargin + doc.width + doc.rightMargin - width - 25
        y = doc.bottomMargin + doc.height + doc.topMargin - 25
        
        line_spacing = 12

        # Set font size and color
        canvas.setFont("Helvetica", 8)  # Set font to Helvetica with size 12
        canvas.setFillColorRGB(0, 0, 0)  # Set fill color to red (RGB: 1, 0, 0)

        # Split the text into lines based on the width
        lines = []
        current_line = ''
        for word in text.split():
            
            if canvas.stringWidth(current_line + ' ' + word) < width:
                current_line += ' ' + word
            else:
                lines.append(current_line.strip())
                current_line = word
        lines.append(current_line.strip())

        # Draw each line individually
        for line in lines:
            text_width = canvas.stringWidth(line)
            x_adjusted = x + (width - text_width)  # Adjust x position for right indentation
            canvas.drawString(x_adjusted, y, line)
            y -= line_spacing

        # Set font size and color
        canvas.setFont("Helvetica", 8)  # Set font to Helvetica with size 12
        canvas.setFillColorRGB(84/256, 50/256, 122/256)  # Set fill color to red (RGB: 1, 0, 0)

        y -= line_spacing

        canvas.drawString(x_adjusted, y, "PrevalonEnergy.com")
        canvas.restoreState()

        # Footer

        canvas.saveState()

        footer_x = 0
        footer_y = 25
        canvas.setFillColorRGB(252/256, 215/256, 87/256)

        # Set border color to transparent
        canvas.setStrokeColorRGB(1, 1, 1, 0)  # Set border color to transparent (RGB: 1, 1, 1) and alpha (opacity) to 0
        canvas.setFont("Helvetica", 12)

        canvas.rect(footer_x, footer_y, 25, 25, fill=1)

        page_num = canvas.getPageNumber()

        canvas.setFillColorRGB(0, 0, 0)
        canvas.drawString(25, 25+6, " %d" % page_num)

        canvas.restoreState()


    cost_memo_pdf = "Report.pdf"

    # Create a PDF document
    doc = SimpleDocTemplate(
        cost_memo_pdf,
        pagesize=letter,
    )


    proj_details = pd.DataFrame.from_dict(proj_details)

    proj_details_data = []
    proj_details_data.append(proj_details.columns.tolist())
    for i in proj_details.values.tolist():
        proj_details_data.append(i)


    # Add content to Technical Proposal
    # Add title
    title_text = report_title
    sub_title_text = report_sub_title
    
    title_paragraph_style = ParagraphStyle("title", fontSize = 14, fontName = "Helvetica-Bold", leading = 15)
    sub_title_paragraph_style = ParagraphStyle("sub_title", fontSize = 11, fontName = "Helvetica-Oblique", leading = 15)
    section_paragraph_style = ParagraphStyle("section", fontSize = 12, fontName = "Helvetica-Bold")
    hyperlink_style = ParagraphStyle("hyperlink", fontSize = 10, fontName = "Helvetica-Oblique")

    # Define styles

    def table_styles(table): 
        table_style = [ ('BACKGROUND', (0, 0), (-1, 0), prevalon_lavendar), # Header Background
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black), # Header Text Color
                        ('ALIGN', (0, 0), (-1, 0), 'LEFT'), # Allign Header Text 
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'), # Header Text 
                        ("FONTSIZE", (0, 0), (-1, 0), 8),  # Header Font Size
                        
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'), # Table Font
                        ("FONTSIZE", (0, 1), (-1, -1), 8),   # Table Font Size
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black), # Table Text Color
                        ('ALIGN', (1, 1), (-1, -1), 'LEFT'), # Allign Table Text Center
                    
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # Table Text Color
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('WORDWRAP', (0, 0), (-1, -1)), 
                        ]
        
        # Set different background colors for odd and even rows
        for i in range(1, len(table)):
            if i % 2 == 0:
                table_style.append(("BACKGROUND", (0, i), (-1, i), prevalon_lavendar))  # Light blue background color for even rows
            else:
                table_style.append(("BACKGROUND", (0, i), (-1, i), colors.white))  # Light cyan background color for odd rows
        
        # Set BOX for columns
        for i in range(len(table[0])):
            table_style.append(("BOX", (i, 0), (i, -1), 0.1, colors.black))  # Light cyan background color for odd rows
        
        return table_style

    title_paragraph = Paragraph(title_text, title_paragraph_style)
    content.append(title_paragraph)

    sub_title_paragraph = Paragraph(sub_title_text, sub_title_paragraph_style)
    content.append(sub_title_paragraph)

    content.append(Paragraph("<br/><br/>", style_normal))

    content.append(Paragraph("1. Project Details", section_paragraph_style))

    content.append(Paragraph("<br/><br/>", style_normal))

    content.append(Paragraph("The table below describes some details about the project", style_normal))
    
    content.append(Paragraph("<br/><br/>", style_normal))

    table = Table(proj_details_data)
    table_style = table_styles(proj_details_data)
    table.setStyle(TableStyle(table_style))
    content.append(table)

    content.append(Paragraph("<br/><br/>", style_normal))

    content.append(Paragraph("Drawings/Reports - ", style_normal))

    # Using HTML <a> tag
    hyperlink_text = f'<a href={project_ga} color="blue">General Arranagment Drawing</a>'
    content.append(Paragraph(hyperlink_text, hyperlink_style))
        
    # Using HTML <a> tag
    hyperlink_text = f'<a href={project_sat} color="blue">Site Acceptance Test Report</a>'
    content.append(Paragraph(hyperlink_text, hyperlink_style))

    for _ in range(10):
        content.append(Paragraph("<br/><br/>", style_normal))
            
    content.append(Paragraph("2. KPIs", section_paragraph_style))
    content.append(Spacer(1, 8))
    content.append(Paragraph("The figures below show trends over the selected time period", style_normal))
    content.append(Spacer(1, 10))

    # Build the Image flowables
    paths = [
        'avail_plot.png', 'throughput.png', 'rte.png',
        'soc_plot.png', 'fuel_mix.png'
    ]

    # Target size per image (fit box); use _restrictSize to preserve aspect ratio
    img_w, img_h = 3.2*inch, 3.2*inch
    imgs = []
    for p in paths:
        im = PlatypusImage(p)
        im._restrictSize(img_w, img_h)   # keep aspect ratio within this box
        imgs.append(im)

    # Arrange into rows (2 per row here)
    cols = 2
    rows = [imgs[i:i+cols] for i in range(0, len(imgs), cols)]
    # If last row has fewer than 'cols', pad with empty strings (optional)
    rows[-1] += [""] * (cols - len(rows[-1]))

    # Create the table
    t = Table(
        rows,
        colWidths=[(img_w + 0.08*inch)] * cols,  # slight extra for padding
        hAlign='LEFT',
    )
    t.setStyle(TableStyle([
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING',(0,0), (-1,-1), 2),
        ('TOPPADDING',  (0,0), (-1,-1), 2),
        ('BOTTOMPADDING',(0,0),(-1,-1), 15),
        # Optional grid while tuning layout:
        ('GRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
    ]))

    content.append(t)

    doc.build(content, header, header)
    # Return the URL for the download link
    return cost_memo_pdf
