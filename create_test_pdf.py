from PyPDF2 import PdfWriter

# Create a simple test PDF
writer = PdfWriter()
writer.add_blank_page(width=200, height=200)

with open("test.pdf", "wb") as f:
    writer.write(f)

print("Created test.pdf")
