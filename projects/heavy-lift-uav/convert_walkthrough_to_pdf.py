import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

def clean_latex(text):
    # Perform clean replacements of LaTeX equations to readable Unicode text
    replacements = [
        # Block equations $$ ... $$
        (r'\$\$(.*?)\$\$', r'<b>\1</b>'),
        # Inline equations $ ... $
        (r'\$(.*?)\$', r'<b>\1</b>'),
        # LaTeX symbols
        (r'\\sum_{i} m_i', 'Σ m_i'),
        (r'\\sum', 'Σ'),
        (r'\\times', '×'),
        (r'\\frac{(.*?)}{(.*?)}', r'(\1) / (\2)'),
        (r'\\rho', 'ρ'),
        (r'\\pi', 'π'),
        (r'\\omega', 'ω'),
        (r'\\sigma', 'σ'),
        (r'\\eta', 'η'),
        (r'\\theta', 'θ'),
        (r'\\Delta', 'Δ'),
        (r'\\Omega', 'Ω'),
        (r'\\approx', '≈'),
        (r'\\ge', '≥'),
        (r'\\le', '≤'),
        (r'\\text{(.*?)}', r'\1'),
        (r'\\left\(', '('),
        (r'\\right\)', ')'),
        (r'\\left\[', '['),
        (r'\\right\]', ']'),
        (r'\\bar', 'bar'),
        (r'\^2', '²'),
        (r'\^4', '⁴'),
        (r'\^3', '³'),
        (r'_o', '₀'),
        (r'_i', 'ᵢ'),
        (r'_m', 'ₘ'),
        (r'_t', 'ₜ'),
        (r'_0', '₀'),
        (r'_k', 'ₖ'),
        (r'_{k\+1}', 'ₖ₊₁'),
        (r'_{(\w+)}', r'_\1'),
    ]
    
    # Run replacements multiple times for nested fractions or symbols
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
        
    # Clean up empty spaces and formatting
    text = text.replace(r'\ ', ' ')
    text = text.replace(r'\$', '$')
    return text

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header
        self.drawString(54, 11 * 72 - 36, "Heavy-Lift UAV Sizing — Technical Calculation Walkthrough")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 36, page_text)
        self.drawString(54, 36, "CONFIDENTIAL — Engineering Reference Document")
        self.line(54, 48, 8.5 * 72 - 54, 48)
        self.restoreState()

def main():
    md_path = "projects/heavy-lift-uav/CALCULATION_WALKTHROUGH.md"
    pdf_path = "projects/heavy-lift-uav/CALCULATION_WALKTHROUGH.pdf"
    
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return
        
    with open(md_path, "r") as f:
        lines = f.readlines()
        
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#1A365D")   # Deep Navy
    c_secondary = colors.HexColor("#2B6CB0") # Slate Blue
    c_dark = colors.HexColor("#2D3748")      # Charcoal Body Text
    c_light = colors.HexColor("#F7FAFC")     # Soft White Background
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=c_primary, spaceAfter=8)
    h1_style = ParagraphStyle('Heading1_Custom', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=c_primary, spaceBefore=14, spaceAfter=6, keepWithNext=True)
    h2_style = ParagraphStyle('Heading2_Custom', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=13.5, textColor=c_secondary, spaceBefore=10, spaceAfter=5, keepWithNext=True)
    body_style = ParagraphStyle('Body_Custom', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=c_dark, spaceAfter=5)
    bullet_style = ParagraphStyle('Bullet_Custom', parent=body_style, leftIndent=12, bulletIndent=4, spaceAfter=3)
    table_text_style = ParagraphStyle('TableText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=c_dark)
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    
    story = []
    
    in_table = False
    table_rows = []
    
    current_paragraph = []
    
    def flush_paragraph():
        nonlocal current_paragraph
        if current_paragraph:
            text = " ".join(current_paragraph).strip()
            # Determine if bullet or regular paragraph
            if text.startswith(("* ", "- ")):
                bullet_text = clean_latex(text[2:])
                story.append(Paragraph(bullet_text, bullet_style))
            else:
                story.append(Paragraph(clean_latex(text), body_style))
            current_paragraph = []
            
    for line in lines:
        stripped = line.strip()
        
        # Check if inside a table
        if stripped.startswith("|"):
            flush_paragraph()
            in_table = True
            # Parse row
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            # Skip separator line (e.g. | :---: | :---: |)
            if not all(c.startswith(":") or c.endswith(":") or all(ch == '-' for ch in c) for c in cells):
                table_rows.append(cells)
            continue
        elif in_table:
            # End of table
            in_table = False
            if table_rows:
                # Format table
                formatted_data = []
                # Header row
                formatted_data.append([Paragraph(clean_latex(cell), table_header_style) for cell in table_rows[0]])
                # Data rows
                for r in table_rows[1:]:
                    formatted_data.append([Paragraph(clean_latex(cell), table_text_style) for cell in r])
                    
                t = Table(formatted_data, hAlign='LEFT')
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), c_primary),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0")),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
                    ('TOPPADDING', (0,0), (-1,-1), 3),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
                story.append(t)
                story.append(Spacer(1, 5))
                table_rows = []
            
        # Parse titles and sections
        if stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(stripped[2:], title_style))
            story.append(Spacer(1, 6))
        elif stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(stripped[3:], h1_style))
        elif stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(stripped[4:], h2_style))
        elif stripped == "---":
            flush_paragraph()
            # Draw line spacer or page break
            story.append(Spacer(1, 10))
        elif not stripped:
            flush_paragraph()
        else:
            current_paragraph.append(stripped)
            
    flush_paragraph()
    
    # Build the document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built at: {pdf_path}")

if __name__ == "__main__":
    main()
