import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image




def generate_pdf(payment_id, supplier_name, date_of_invoice, date_of_payment_requested, payment_description, amount, status):
    buffer = io.BytesIO()

    # Create the PDF document and set the document properties
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    doc.title = f'Payment Request for {supplier_name}'

    # Create a table to hold the payment information
    data = [
        ['Payment ID', payment_id],
        ['Supplier Name', supplier_name],
        ['Date of Invoice', date_of_invoice],
        ['Date of Payment Requested', date_of_payment_requested],
        ['Payment Description', payment_description],
        ['Amount', amount],
        ['Status', status],
    ]
    table = Table(data)

    # Set the table style
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    # Add the table to the PDF document and build the document
    elements = []
    elements.append(table)
    doc.build(elements)

    # Save the canvas to a PDF file

    # Close the canvas and the buffer
    buffer.seek(0)

    return buffer.read()


def generate_payment_pdf(db, payment_id, supplier_name, amount, status, signature):
    # Create a buffer for the PDF document
    buffer = io.BytesIO()

    # Create the canvas and set the document properties
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle(f'Payment request for: {supplier_name}')

    # Get payment details from the database
    try:
        cur = db.execute('SELECT payment_description, company_name FROM payments INNER JOIN suppliers ON payments.supplier_id = suppliers.id WHERE payments.id=?', [payment_id])
        payment = cur.fetchone()
    except Exception as e:
        # Handle database query error
        return None

    # Create a table to display payment details
    table = [
        ['Payment ID:', payment_id],
        ['Supplier Name:', payment['company_name']],
        ['Amount:', amount],
        ['Status:', status]
    ]
    t = Table(table)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    t.wrapOn(p, inch, 2 * inch)
    t.drawOn(p, inch, 7.5 * inch)

    # Draw the manager's signature on the PDF document
    if signature:
        img = Image.open(signature)
        img_width, img_height = img.size
        aspect_ratio = img_height / img_width
        signature_width = 2.5 * inch
        signature_height = signature_width * aspect_ratio
        p.drawImage(signature, 400, 2 * inch, width=signature_width, height=signature_height)

    # Save the PDF document and close the canvas
    p.showPage()
    p.save()

    # Return the bytes of the PDF document
    buffer.seek(0)
    return buffer.read()


