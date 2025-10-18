from fpdf import FPDF
from io import BytesIO

class PDFGenerator:
    @staticmethod
    def create(summary, questions, user_answers, score, email):
        """Create comprehensive PDF report"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)  # Smaller font for more content
        
        # Title
        pdf.set_font('', 'B', 16)
        pdf.cell(200, 10, txt="Document Summary & Quiz Results", ln=1, align='C')
        pdf.set_font('', '', 12)
        pdf.cell(200, 10, txt=f"Email: {email}", ln=1, align='C')
        pdf.cell(200, 10, txt=f"Score: {score}/{len(questions)}", ln=1, align='C')
        pdf.ln(10)
        
        # Summary section
        pdf.set_font('', 'B', 12)
        pdf.cell(0, 10, txt="Document Summary:", ln=1)
        pdf.set_font('', '', 10)
        pdf.multi_cell(0, 8, txt=summary)
        pdf.ln(10)
        
        # Questions and answers
        pdf.set_font('', 'B', 12)
        pdf.cell(0, 10, txt="Quiz Questions and Answers:", ln=1)
        pdf.set_font('', '', 10)
        
        for i, question in enumerate(questions):
            pdf.ln(3)
            pdf.set_font('', 'B')
            pdf.multi_cell(0, 8, txt=f"Q{i+1}: {question['question']}")
            pdf.set_font('')
            
            user_answer = user_answers.get(str(i), "Not answered")
            correct_answer = question['answer']
            
            pdf.cell(0, 8, txt=f"Your answer: {user_answer}", ln=1)
            pdf.cell(0, 8, txt=f"Correct answer: {correct_answer}", ln=1)
            
            if user_answer.lower() == correct_answer.lower():
                pdf.cell(0, 8, txt="Status: ✅ Correct", ln=1)
            else:
                pdf.cell(0, 8, txt="Status: ❌ Incorrect", ln=1)
            
            pdf.ln(2)
        
        buffer = BytesIO()
        pdf.output(buffer)
        return buffer.getvalue()