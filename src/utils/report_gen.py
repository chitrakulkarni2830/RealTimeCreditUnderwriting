import datetime
import os
import re
import tempfile
from fpdf import FPDF
from src.utils import get_resource_path

class CreditReportPDF(FPDF):
    def header(self):
        # Logo placeholder or Title
        self.set_fill_color(15, 23, 42) # Dark Slate
        self.rect(0, 0, 210, 40, 'F')
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 25, 'CREDIT UNDERWRITING OFFICIAL AUDIT', 0, 1, 'C')
        self.set_font('helvetica', '', 10)
        self.cell(0, -5, f'Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Confidential AI-Generated Assessment', 0, 0, 'C')

def generate_pdf_report(user_id, assessment_text, score_data):
    """Creates a branded PDF report for the credit assessment."""
    pdf = CreditReportPDF()
    pdf.add_page()
    
    # 1. Executive Summary
    pdf.set_font('helvetica', 'B', 16)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, f'Executive Summary: User ID {user_id}', 0, 1)
    pdf.ln(5)
    
    # 2. Risk Score Box
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(10, 55, 190, 30, 'F')
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_xy(15, 60)
    pdf.cell(0, 10, f"ALGORITHMIC RISK SCORE: {score_data['score']}/100", 0, 1)
    pdf.set_font('helvetica', '', 12)
    pdf.set_x(15)
    pdf.cell(0, 10, f"Risk Category: {score_data['category']}", 0, 1)
    
    pdf.ln(15)
    
    # 3. Agent Decision
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, 'Agent Reasoning & Decision', 0, 1)
    pdf.set_font('helvetica', '', 11)
    pdf.set_text_color(50, 50, 50)
    
    # Clean up text for FPDF (strip emojis as Helvetica doesn't support them)
    # We remove all non-ASCII characters to be safe
    clean_text = re.sub(r'[^\x00-\x7f]', r'', assessment_text)
    clean_text = clean_text.replace('### ', '').replace('**', '')
    pdf.multi_cell(0, 7, clean_text)
    
    # 4. Deductions
    if score_data['deductions']:
        pdf.ln(10)
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, 'Risk Factor Deductions', 0, 1)
        pdf.set_font('helvetica', '', 10)
        for d in score_data['deductions']:
            # Strip emojis from deductions too
            clean_d = re.sub(r'[^\x00-\x7f]', r'', d)
            pdf.cell(0, 6, f"- {clean_d}", 0, 1)

    # Save
    # Save to a temporary directory for portability in bundled mode
    temp_dir = os.path.join(tempfile.gettempdir(), 'credit_reports')
    os.makedirs(temp_dir, exist_ok=True)
    report_path = os.path.join(temp_dir, f'Report_User_{user_id}.pdf')
    pdf.output(report_path)
    return report_path

if __name__ == "__main__":
    # Test generation
    test_score = {"score": 85, "category": "Premium", "deductions": ["Emoji Check 📑"]}
    test_text = "### 📑 DECISION SUMMARY: PREMIUM APPROVAL\n\n**Stability**: Reliable payments."
    generate_pdf_report(999, test_text, test_score)
    print("Test report generated at reports/Report_User_999.pdf")
