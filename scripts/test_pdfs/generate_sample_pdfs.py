import os
import zipfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(filename, title, contacts):
    """
    Creates a sample PDF with contacts layout using ReportLab.
    """
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, title)

    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "Official Organization Directory")
    c.line(100, 710, 500, 710)

    y = 670
    for name, phone in contacts:
        c.drawString(100, y, f"Name: {name}")
        c.drawString(300, y, f"Phone: {phone}")
        y -= 30

    c.save()

def generate_samples():
    output_dir = "/tmp/sample_pdfs_gen"
    os.makedirs(output_dir, exist_ok=True)

    pdf1 = os.path.join(output_dir, "engineering_team.pdf")
    contacts1 = [
        ("Aarav Sharma", "+91 9876543210"),
        ("Priya Patel", "9876543211"),
        ("Rohan Verma", "+919876543212"),
        ("Ananya Sen", "09876543213")
    ]
    create_pdf(pdf1, "Engineering Department Contacts", contacts1)

    pdf2 = os.path.join(output_dir, "marketing_team.pdf")
    contacts2 = [
        ("Vikram Singh", "+91 9876543214"),
        ("Siddharth Rao", "9876543215"),
        ("Kavya Nair", "+919876543216")
    ]
    create_pdf(pdf2, "Marketing Department Contacts", contacts2)

    pdf3 = os.path.join(output_dir, "executives.pdf")
    contacts3 = [
        ("Mohammad Pasha", "+91 9876543217"),
        ("Subhan Pasha", "9876543218"),
        ("Zara Khan", "+919876543219")
    ]
    create_pdf(pdf3, "Executive Management Contacts", contacts3)

    # Build data/sample_contacts.zip
    zip_dir = "data"
    os.makedirs(zip_dir, exist_ok=True)
    zip_path = os.path.join(zip_dir, "sample_contacts.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(pdf1, "engineering_team.pdf")
        zipf.write(pdf2, "marketing_team.pdf")
        zipf.write(pdf3, "executives.pdf")

    print(f"Sample PDFs and ZIP created at {zip_path}")

if __name__ == "__main__":
    generate_samples()
