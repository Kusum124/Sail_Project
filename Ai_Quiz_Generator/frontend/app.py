import streamlit as st
import requests

API_URL = "http://localhost:5000"

def main():
    st.set_page_config(page_title="20 Question Quiz System", layout="wide")
    st.title("📚 20 Question Document Quiz Generator")
    
    # Initialize session state
    if 'summary' not in st.session_state:
        st.session_state.summary = ""
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'score' not in st.session_state:
        st.session_state.score = 0

    # File upload section
    with st.expander("📤 Upload PDF Document", expanded=True):
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        user_email = st.text_input("Enter your email address for results:")
        
        if uploaded_file and user_email and st.button("🚀 Generate 20 Random Questions"):
            with st.spinner("Generating summary and 20 random questions with Qwen 0.5B..."):
                try:
                    files = {'file': ('document.pdf', uploaded_file.getvalue(), 'application/pdf')}
                    response = requests.post(f"{API_URL}/generate_content", files=files, timeout=180)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.summary = data['summary']
                        st.session_state.questions = data['questions']
                        st.session_state.user_answers = {}
                        st.session_state.submitted = False
                        st.session_state.user_email = user_email
                        st.success(f"✅ Generated summary and {len(data['questions'])} random questions!")
                    else:
                        st.error("❌ Failed to generate content")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # Display summary
    if st.session_state.summary:
        with st.expander("📝 Document Summary", expanded=True):
            st.markdown(st.session_state.summary)

    # Quiz section - 20 questions
    if st.session_state.questions:
        st.subheader(f"🧠 Fill-in-the-Blank Quiz ({len(st.session_state.questions)} Questions)")
        
        # Create tabs for better organization of 20 questions
        tabs = st.tabs([f"Q{i+1}" for i in range(len(st.session_state.questions))])
        
        for i, question in enumerate(st.session_state.questions):
            with tabs[i]:
                st.write(f"**Question {i+1}:**")
                st.write(question['question'])
                
                user_answer = st.text_input(
                    f"Your answer for Question {i+1}",
                    key=f"q_{i}",
                    placeholder="Type your answer here...",
                    label_visibility="collapsed"
                )
                st.session_state.user_answers[str(i)] = user_answer
        
        if st.button("📤 Submit All Answers", type="primary"):
            st.session_state.submitted = True
            try:
                response = requests.post(
                    f"{API_URL}/submit_quiz",
                    json={
                        "questions": st.session_state.questions,
                        "user_answers": st.session_state.user_answers
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.score = data['score']
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Submission error: {str(e)}")

    # Results and email section
    if st.session_state.submitted:
        st.subheader("📊 Quiz Results")
        st.success(f"**Your Score: {st.session_state.score}/{len(st.session_state.questions)}**")
        
        # Show results in expandable sections
        for i, question in enumerate(st.session_state.questions):
            with st.expander(f"Question {i+1}", expanded=False):
                user_answer = st.session_state.user_answers.get(str(i), "Not answered")
                correct_answer = question['answer']
                
                st.write(f"**Question:** {question['question']}")
                
                if user_answer.lower() == correct_answer.lower():
                    st.success(f"✅ **Your answer:** {user_answer}")
                else:
                    st.error(f"❌ **Your answer:** {user_answer}")
                    st.info(f"📋 **Correct answer:** {correct_answer}")
        
        # Email results
        st.divider()
        st.subheader("📧 Email Results")
        
        if st.button("📤 Send Results via Email", type="primary"):
            with st.spinner("Generating and sending report..."):
                try:
                    # Generate PDF report
                    response = requests.post(
                        f"{API_URL}/generate_report",
                        json={
                            "summary": st.session_state.summary,
                            "questions": st.session_state.questions,
                            "user_answers": st.session_state.user_answers,
                            "score": st.session_state.score,
                            "email": st.session_state.user_email
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        # Send email with PDF
                        files = {'file': ('quiz_report.pdf', response.content)}
                        email_response = requests.post(
                            f"{API_URL}/send_email",
                            files=files,
                            data={'email': st.session_state.user_email},
                            timeout=30
                        )
                        
                        if email_response.status_code == 200:
                            st.success("✅ Results sent to your email!")
                        else:
                            st.error("❌ Failed to send email")
                    else:
                        st.error("❌ Failed to generate PDF report")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()