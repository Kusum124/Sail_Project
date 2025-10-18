import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import re
import random

class QuestionGenerator:
    def __init__(self, model_path="E:\\Models\\Qwen0.5B"):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Qwen model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            print("Qwen model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def generate_summary(self, text, max_length=200):
        """Generate summary using Qwen model"""
        if self.model is None:
            return self._fallback_summary(text)
        
        try:
            prompt = f"""Please provide a comprehensive summary of the following text in 5-7 bullet points:

            {text[:2000]}

            Summary:
            • """
            
            inputs = self.tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            summary = generated_text[len(prompt):].strip()
            
            # Format as bullet points
            if '•' not in summary:
                points = [f"• {point.strip()}" for point in summary.split('.') if point.strip()]
                summary = "\n".join(points[:7])
            
            return summary
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return self._fallback_summary(text)
    
    def generate_questions(self, text, num_questions=20, max_length=500):
        """Generate multiple questions using Qwen model"""
        if self.model is None:
            return self._fallback_questions(text, num_questions)
        
        try:
            prompt = f"""Based on the following text, generate {num_questions} diverse fill-in-the-blank questions. 
            Each question should have a blank (_____) and provide the answer on the next line.

            Text: {text[:1500]}

            Questions:
            1. """
            
            inputs = self.tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.8,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            questions_text = generated_text[len(prompt):]
            
            # Parse the generated questions
            questions = self.parse_questions(questions_text)
            
            # If we didn't get enough questions, generate more
            if len(questions) < num_questions:
                additional_questions = self._generate_additional_questions(text, num_questions - len(questions))
                questions.extend(additional_questions)
            
            # Randomize the order of questions
            random.shuffle(questions)
            
            return questions[:num_questions]
            
        except Exception as e:
            print(f"Question generation error: {e}")
            return self._fallback_questions(text, num_questions)
    
    def _generate_additional_questions(self, text, count):
        """Generate additional questions if needed"""
        additional_questions = []
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 15]
        
        for i in range(min(count * 2, len(sentences))):  # Generate extra to have variety
            if len(sentences[i].split()) > 5:
                words = sentences[i].split()
                if len(words) > 3:
                    # Choose random position for blank
                    blank_pos = random.randint(1, len(words) - 2)
                    answer = words[blank_pos]
                    words[blank_pos] = "_____"
                    question = " ".join(words)
                    
                    additional_questions.append({
                        "type": "fill_blank",
                        "question": question + ("?" if not question.endswith('?') else ""),
                        "answer": answer
                    })
        
        # Remove duplicates and shuffle
        unique_questions = []
        seen_questions = set()
        for q in additional_questions:
            q_hash = hash(q['question'].lower())
            if q_hash not in seen_questions:
                seen_questions.add(q_hash)
                unique_questions.append(q)
        
        random.shuffle(unique_questions)
        return unique_questions[:count]
    
    def _fallback_summary(self, text):
        """Fallback summary generation"""
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        return "• " + "\n• ".join(sentences[:5])
    
    def _fallback_questions(self, text, num_questions=20):
        """Fallback question generation"""
        questions = []
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 15]
        
        # Generate more questions than needed for variety
        for i in range(min(num_questions * 3, len(sentences))):
            if len(sentences[i].split()) > 5:
                words = sentences[i].split()
                if len(words) > 3:
                    # Random blank position for variety
                    blank_pos = random.randint(1, len(words) - 2)
                    answer = words[blank_pos]
                    words[blank_pos] = "_____"
                    question = " ".join(words)
                    
                    questions.append({
                        "type": "fill_blank",
                        "question": question + ("?" if not question.endswith('?') else ""),
                        "answer": answer
                    })
        
        # Remove duplicates
        unique_questions = []
        seen_questions = set()
        for q in questions:
            q_hash = hash(q['question'].lower())
            if q_hash not in seen_questions:
                seen_questions.add(q_hash)
                unique_questions.append(q)
        
        # Shuffle and return requested number
        random.shuffle(unique_questions)
        return unique_questions[:num_questions]
    
    def parse_questions(self, generated_text):
        """Parse generated questions into structured format"""
        questions = []
        lines = [line.strip() for line in generated_text.split('\n') if line.strip()]
        i = 0
        
        while i < len(lines) and len(questions) < 20:
            line = lines[i]
            
            # Look for question lines (numbered or with blank)
            if (re.match(r'^\d+\.', line) and '_____' in line) or ('_____' in line and len(line.split()) > 3):
                # Extract question text
                if re.match(r'^\d+\.', line):
                    question_text = line.split('.', 1)[1].strip()
                else:
                    question_text = line
                
                # Look for answer in next lines
                answer = None
                for j in range(i+1, min(i+5, len(lines))):
                    if 'answer:' in lines[j].lower() or 'ans:' in lines[j].lower() or lines[j].lower().startswith('answer '):
                        answer = lines[j].split(':')[-1].strip() if ':' in lines[j] else lines[j].replace('answer', '').replace('Answer', '').strip()
                        break
                
                if answer and len(answer) > 0:
                    questions.append({
                        "type": "fill_blank",
                        "question": question_text,
                        "answer": answer
                    })
                    i = j
                else:
                    i += 1
            else:
                i += 1
        
        return questions
    
    def generate_all(self, text, num_questions=20):
        """Generate both summary and questions"""
        summary = self.generate_summary(text)
        questions = self.generate_questions(text, num_questions)
        
        return summary, questions