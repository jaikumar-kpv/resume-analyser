import re
import spacy
from PyPDF2 import PdfReader
from docx import Document
import magic
from typing import Dict, List, Optional


nlp = spacy.load("en_core_web_sm")

class ResumeParser:
    def __init__(self):
        self.skill_pattern_path = "data/skill_patterns.jsonl"
        self._setup_skill_matcher()
        
    def _setup_skill_matcher(self):
        from spacy.matcher import PhraseMatcher
        self.skill_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        
        # Sample skills - in a real app, load from a larger database
        skills = [
            "Python", "JavaScript", "Machine Learning", "Data Analysis",
            "Project Management", "SQL", "Flask", "Django", "React",
            "AWS", "Azure", "Docker", "Kubernetes", "Git", "Agile",
            "Scrum", "TensorFlow", "PyTorch", "Natural Language Processing",
            "Computer Vision", "Big Data", "Hadoop", "Spark", "Tableau",
            "Power BI", "Excel", "R", "Java", "C++", "Linux"
        ]
        
        patterns = [nlp.make_doc(skill) for skill in skills]
        self.skill_matcher.add("SKILLS", patterns)
    
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume and extract information"""
        text = self._extract_text(file_path)
        doc = nlp(text)
        
        data = {
            "name": self._extract_name(doc),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "skills": self._extract_skills(doc),
            "education": self._extract_education(doc),
            "experience": self._extract_experience(doc),
            "raw_text": text
        }
        
        return data
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX files"""
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        
        if file_type == "application/pdf":
            reader = PdfReader(file_path)
            text = " ".join([page.extract_text() for page in reader.pages])
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(file_path)
            text = " ".join([para.text for para in doc.paragraphs])
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        return text
    
    def _extract_name(self, doc) -> Optional[str]:
        """Extract name using NER"""
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email using regex"""
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        match = re.search(email_pattern, text)
        return match.group() if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number using regex"""
        phone_pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        match = re.search(phone_pattern, text)
        return match.group() if match else None
    
    def _extract_skills(self, doc) -> List[str]:
        """Extract skills using phrase matching"""
        matches = self.skill_matcher(doc)
        skills = set()
        
        for match_id, start, end in matches:
            skill = doc[start:end].text
            skills.add(skill)
        
        return list(skills)
    
    def _extract_education(self, doc) -> List[str]:
        """Extract education information"""
        education = []
        
        # Extract using degree keywords
        degree_keywords = ["bachelor", "master", "phd", "doctorate", "bs", "ms", "mba"]
        
        for token in doc:
            if token.text.lower() in degree_keywords:
                # Get the sentence containing the degree
                sent = token.sent.text
                education.append(sent)
        
        return education
    
    def _extract_experience(self, doc) -> List[Dict]:
        """Extract work experience"""
        experience = []
        org_pattern = r"(?i)(?:worked at|employed at|at|in)\s+([A-Za-z0-9\s&,.]+)"
        
        # Simple extraction - in a real app, use more sophisticated parsing
        for ent in doc.ents:
            if ent.label_ == "ORG":
                exp = {"organization": ent.text}
                # Try to find duration in the same sentence
                for token in ent.sent:
                    if token.like_num and ("year" in token.text.lower() or "month" in token.text.lower()):
                        exp["duration"] = token.text
                experience.append(exp)
        
        return experience