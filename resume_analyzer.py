import PyPDF2
import docx
import re
from pathlib import Path

class ResumeAnalyzer:
    def __init__(self):
        self.resume_path = "resume.pdf"
        self.skills_keywords = [
            "Python", "Java", "JavaScript", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
            "Jenkins", "GitLab", "CI/CD", "DevOps", "Linux", "Windows", "Terraform",
            "Ansible", "Chef", "Puppet", "Monitoring", "Prometheus", "Grafana",
            "ELK Stack", "Splunk", "MySQL", "PostgreSQL", "MongoDB", "Redis",
            "Microservices", "REST API", "GraphQL", "React", "Angular", "Vue",
            "Node.js", "Django", "Flask", "Spring", "Git", "SVN", "Agile", "Scrum"
        ]
    
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF resume"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX resume"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"❌ Error reading DOCX: {e}")
            return ""
    
    def extract_skills(self, text):
        """Extract skills from resume text"""
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def extract_contact_info(self, text):
        """Extract contact information from resume"""
        contact_info = {}
        
        # Email regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone regex
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        
        # LinkedIn regex
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        if linkedin:
            contact_info['linkedin'] = f"https://{linkedin[0]}"
        
        return contact_info
    
    def analyze_resume(self, resume_path=None):
        """Main function to analyze resume"""
        if resume_path:
            self.resume_path = resume_path
        
        if not Path(self.resume_path).exists():
            print(f"❌ Resume not found: {self.resume_path}")
            return None
        
        print(f"📄 Analyzing resume: {self.resume_path}")
        
        # Determine file type and extract text
        file_extension = Path(self.resume_path).suffix.lower()
        
        if file_extension == '.pdf':
            text = self.extract_text_from_pdf(self.resume_path)
        elif file_extension in ['.docx', '.doc']:
            text = self.extract_text_from_docx(self.resume_path)
        else:
            print(f"❌ Unsupported file format: {file_extension}")
            return None
        
        if not text:
            print("❌ Could not extract text from resume")
            return None
        
        # Extract information
        skills = self.extract_skills(text)
        contact_info = self.extract_contact_info(text)
        
        analysis = {
            'skills': skills,
            'contact_info': contact_info,
            'raw_text': text[:500] + "..." if len(text) > 500 else text  # First 500 chars
        }
        
        print(f"✅ Found {len(skills)} skills: {', '.join(skills[:10])}")
        print(f"✅ Extracted contact info: {list(contact_info.keys())}")
        
        return analysis
