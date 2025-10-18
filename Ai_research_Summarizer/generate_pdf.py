from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Top 5 Scientific Research Summaries", ln=True, align="C")

    def add_paper(self, title, abstract, summary, link):
        self.set_font("Arial", "B", 12)
        self.multi_cell(0, 10, f"Title: {title}")

        self.set_font("Arial", "", 11)
        self.multi_cell(0, 10, f"Abstract: {abstract}")
        self.multi_cell(0, 10, f"Summary: {summary}")
        self.multi_cell(0, 10, f"Link: {link}")
        self.ln(5)

def generate_pdf(papers, output_file="summary.pdf"):
    pdf = PDF()
    pdf.add_page()
    for paper in papers:
        pdf.add_paper(paper['title'], paper['abstract'], paper['summary'], paper['link'])
    pdf.output(output_file)
