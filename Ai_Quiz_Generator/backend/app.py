from flask import Flask, request, jsonify, send_file
from pdf_processor import PDFProcessor
from question_generator import QuestionGenerator
from email_service import EmailService
from utils import PDFGenerator
from io import BytesIO

app = Flask(__name__)

# Initialize services
pdf_processor = PDFProcessor()
question_gen = QuestionGenerator("E:\\Models\\Qwen0.5B")
email_service = EmailService(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    email="kusumlatamurmu124@gmail.com",
    password="iuab hcmm rvpr stii"
)

@app.route('/generate_content', methods=['POST'])
def generate_content():
    """Generate both summary and quiz questions"""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        file_bytes = file.read()
        text = pdf_processor.extract_text(file_bytes)
        
        if not text:
            return jsonify({"error": "Could not extract text from PDF"}), 400
        
        # Generate both summary and 20 random questions using Qwen
        summary, questions = question_gen.generate_all(text, num_questions=20)
        
        return jsonify({
            "status": "success",
            "summary": summary,
            "questions": questions,
            "total_questions": len(questions)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    data = request.json
    try:
        questions = data['questions']
        user_answers = data['user_answers']
        
        # Calculate score
        score = 0
        for i, question in enumerate(questions):
            user_answer = user_answers.get(str(i), "").strip().lower()
            correct_answer = question['answer'].strip().lower()
            if user_answer == correct_answer:
                score += 1
        
        return jsonify({
            "status": "success",
            "score": score,
            "total": len(questions)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    try:
        pdf_bytes = PDFGenerator.create(
            summary=data['summary'],
            questions=data['questions'],
            user_answers=data['user_answers'],
            score=data['score'],
            email=data['email']
        )
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='quiz_report.pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        email = request.form['email']
        file = request.files['file']
        
        success = email_service.send(
            to_email=email,
            subject="Your Document Summary and Quiz Results (20 Questions)",
            body="Please find attached the document summary and your quiz results with 20 questions.",
            pdf_bytes=file.read()
        )
        
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"error": "Failed to send email"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)