from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet


def generate_cover_page(pdf_path, name, surname, email, department, date_of_invoice, date_of_payment_requested, payment_made_to, company_name, payment_description, bank_name, acc_number, branch_code, amount):
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph('Invoice Cover Page', styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f'Name: {name}', styles['Normal']))
    story.append(Paragraph(f'Surname: {surname}', styles['Normal']))
    story.append(Paragraph(f'Email: {email}', styles['Normal']))
    story.append(Paragraph(f'Department: {department}', styles['Normal']))
    story.append(Paragraph(f'Date of Invoice: {date_of_invoice}', styles['Normal']))
    story.append(Paragraph(f'Date of Payment Requested: {date_of_payment_requested}', styles['Normal']))
    story.append(Paragraph(f'Payment Made to: {payment_made_to}', styles['Normal']))
    story.append(Paragraph(f'Company Name: {company_name}', styles['Normal']))
    story.append(Paragraph(f'Payment Description: {payment_description}', styles['Normal']))
    story.append(Paragraph(f'Bank Name: {bank_name}', styles['Normal']))
    story.append(Paragraph(f'Account Number: {acc_number}', styles['Normal']))
    story.append(Paragraph(f'Branch Code: {branch_code}', styles['Normal']))
    story.append(Paragraph(f'Amount: {amount}', styles['Normal']))
    doc.build(story)
