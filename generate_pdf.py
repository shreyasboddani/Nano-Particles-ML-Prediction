import weasyprint
from pathlib import Path

# Convert HTML to PDF
html_file = Path('results.html')
pdf_file = Path('Silver_Nanoparticle_ML_Analysis.pdf')

# Read HTML content
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Convert to PDF
html_doc = weasyprint.HTML(string=html_content, base_url=str(html_file.parent))
html_doc.write_pdf(str(pdf_file))

print(f"PDF generated successfully: {pdf_file}")
print(f"File size: {pdf_file.stat().st_size / 1024:.1f} KB")
