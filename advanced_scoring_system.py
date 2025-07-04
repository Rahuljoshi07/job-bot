#!/usr/bin/env python3
"""
🎯 ADVANCED SCORING SYSTEM FOR JOB BOT
Enhanced job matching with detailed scoring metrics and analytics
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import sqlite3
from pathlib import Path

# NLP and ML libraries with fallback
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    NLP_AVAILABLE = True
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
        
except ImportError:
    NLP_AVAILABLE = False
    print("⚠️ NLP libraries not available. Using basic scoring.")

logger = logging.getLogger(__name__)

@dataclass
class ScoringMetrics:
    """Comprehensive scoring metrics for job matching"""
    overall_score: float
    skills_score: float
    experience_score: float
    location_score: float
    salary_score: float
    company_score: float
    title_relevance: float
    description_match: float
    requirements_match: float
    nlp_similarity: float
    sentiment_score: float
    urgency_score: float
    competition_score: float
    growth_potential: float
    
    def to_dict(self) -> Dict:
        return asdict(self)

class AdvancedJobScorer:
    """Advanced job scoring system with multiple weighted factors"""
    
    def __init__(self, user_profile: Dict):
        self.user_profile = user_profile
        self.skills_keywords = self._load_skills_database()
        self.experience_keywords = self._load_experience_keywords()
        self.location_preferences = user_profile.get('location_preferences', {})
        self.salary_preferences = user_profile.get('salary_preferences', {})
        
        # Scoring weights (can be customized per user)
        self.weights = {
            'skills': 0.25,
            'experience': 0.15,
            'location': 0.10,
            'salary': 0.10,
            'company': 0.10,
            'title_relevance': 0.10,
            'description_match': 0.10,
            'nlp_similarity': 0.10
        }
        
        # Initialize NLP components if available
        if NLP_AVAILABLE:
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        logger.info("Advanced Job Scorer initialized")

    def _load_skills_database(self) -> Dict[str, List[str]]:
        """Load comprehensive skills database with categories"""
        return {
            'programming_languages': [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
                'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl'
            ],
            'web_technologies': [
                'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django', 'Flask',
                'Spring', 'Laravel', 'ASP.NET', 'HTML5', 'CSS3', 'SASS', 'Bootstrap'
            ],
            'cloud_platforms': [
                'AWS', 'Azure', 'Google Cloud', 'GCP', 'DigitalOcean', 'Heroku',
                'Firebase', 'Vercel', 'Netlify', 'Cloudflare'
            ],
            'devops_tools': [
                'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions',
                'Terraform', 'Ansible', 'Chef', 'Puppet', 'Vagrant', 'Helm'
            ],
            'databases': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
                'Cassandra', 'DynamoDB', 'SQLite', 'Oracle', 'SQL Server'
            ],
            'monitoring_tools': [
                'Prometheus', 'Grafana', 'ELK Stack', 'Splunk', 'DataDog',
                'New Relic', 'Nagios', 'Zabbix', 'CloudWatch'
            ],
            'version_control': [
                'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN', 'Mercurial'
            ],
            'methodologies': [
                'Agile', 'Scrum', 'Kanban', 'DevOps', 'CI/CD', 'TDD', 'BDD',
                'Microservices', 'REST API', 'GraphQL', 'SOAP'
            ]
        }

    def _load_experience_keywords(self) -> Dict[str, List[str]]:
        """Load experience-level keywords"""
        return {
            'junior': ['junior', 'entry', 'associate', 'trainee', '0-2 years', 'graduate'],
            'mid': ['mid', 'intermediate', 'regular', '2-5 years', 'experienced'],
            'senior': ['senior', 'sr', 'lead', 'principal', '5+ years', 'expert'],
            'executive': ['manager', 'director', 'vp', 'chief', 'head', 'executive']
        }

    def score_job(self, job_data: Dict) -> ScoringMetrics:
        """
        Comprehensive job scoring with multiple factors
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            ScoringMetrics object with detailed scoring breakdown
        """
        try:
            # Extract job information
            title = job_data.get('title', '').lower()
            description = job_data.get('description', '').lower()
            requirements = job_data.get('requirements', '').lower()
            company = job_data.get('company', '').lower()
            location = job_data.get('location', '').lower()
            salary = job_data.get('salary', '')
            
            # Calculate individual scores
            skills_score = self._calculate_skills_score(title, description, requirements)
            experience_score = self._calculate_experience_score(title, description, requirements)
            location_score = self._calculate_location_score(location)
            salary_score = self._calculate_salary_score(salary)
            company_score = self._calculate_company_score(company)
            title_relevance = self._calculate_title_relevance(title)
            description_match = self._calculate_description_match(description)
            requirements_match = self._calculate_requirements_match(requirements)
            nlp_similarity = self._calculate_nlp_similarity(description) if NLP_AVAILABLE else 0.5
            
            # Additional scoring factors
            sentiment_score = self._calculate_sentiment_score(description)
            urgency_score = self._calculate_urgency_score(title, description)
            competition_score = self._calculate_competition_score(title, description)
            growth_potential = self._calculate_growth_potential(title, description, company)
            
            # Calculate weighted overall score
            overall_score = (
                skills_score * self.weights['skills'] +
                experience_score * self.weights['experience'] +
                location_score * self.weights['location'] +
                salary_score * self.weights['salary'] +
                company_score * self.weights['company'] +
                title_relevance * self.weights['title_relevance'] +
                description_match * self.weights['description_match'] +
                nlp_similarity * self.weights['nlp_similarity']
            )
            
            # Create scoring metrics
            metrics = ScoringMetrics(
                overall_score=round(overall_score * 100, 1),
                skills_score=round(skills_score * 100, 1),
                experience_score=round(experience_score * 100, 1),
                location_score=round(location_score * 100, 1),
                salary_score=round(salary_score * 100, 1),
                company_score=round(company_score * 100, 1),
                title_relevance=round(title_relevance * 100, 1),
                description_match=round(description_match * 100, 1),
                requirements_match=round(requirements_match * 100, 1),
                nlp_similarity=round(nlp_similarity * 100, 1),
                sentiment_score=round(sentiment_score * 100, 1),
                urgency_score=round(urgency_score * 100, 1),
                competition_score=round(competition_score * 100, 1),
                growth_potential=round(growth_potential * 100, 1)
            )
            
            logger.info(f"Job scored: {job_data.get('title', 'Unknown')} - {metrics.overall_score}%")
            return metrics
            
        except Exception as e:
            logger.error(f"Error scoring job: {e}")
            # Return default metrics on error
            return ScoringMetrics(
                overall_score=50.0, skills_score=50.0, experience_score=50.0,
                location_score=50.0, salary_score=50.0, company_score=50.0,
                title_relevance=50.0, description_match=50.0, requirements_match=50.0,
                nlp_similarity=50.0, sentiment_score=50.0, urgency_score=50.0,
                competition_score=50.0, growth_potential=50.0
            )

    def _calculate_skills_score(self, title: str, description: str, requirements: str) -> float:
        """Calculate skills match score"""
        user_skills = [skill.lower() for skill in self.user_profile.get('skills', [])]
        combined_text = f"{title} {description} {requirements}"
        
        skill_matches = 0
        total_user_skills = len(user_skills)
        
        if total_user_skills == 0:
            return 0.5  # Default score if no skills defined
        
        for skill in user_skills:
            if skill in combined_text:
                skill_matches += 1
        
        # Bonus for skill category matches
        for category, skills in self.skills_keywords.items():
            category_matches = sum(1 for skill in skills if skill.lower() in combined_text)
            if category_matches > 0:
                skill_matches += category_matches * 0.1  # Bonus weight
        
        return min(skill_matches / total_user_skills, 1.0)

    def _calculate_experience_score(self, title: str, description: str, requirements: str) -> float:
        """Calculate experience level match score"""
        user_experience = self.user_profile.get('experience_years', 0)
        combined_text = f"{title} {description} {requirements}"
        
        # Determine job experience level
        job_level = 'mid'  # default
        
        for level, keywords in self.experience_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                job_level = level
                break
        
        # Match user experience to job level
        if user_experience <= 2:
            user_level = 'junior'
        elif user_experience <= 5:
            user_level = 'mid'
        elif user_experience <= 10:
            user_level = 'senior'
        else:
            user_level = 'executive'
        
        # Calculate match score
        level_hierarchy = {'junior': 0, 'mid': 1, 'senior': 2, 'executive': 3}
        user_level_num = level_hierarchy[user_level]
        job_level_num = level_hierarchy[job_level]
        
        # Perfect match = 1.0, adjacent levels = 0.8, etc.
        score = max(0, 1.0 - abs(user_level_num - job_level_num) * 0.2)
        return score

    def _calculate_location_score(self, location: str) -> float:
        """Calculate location preference score"""
        user_location = self.user_profile.get('location', '').lower()
        remote_preference = self.user_profile.get('remote_only', False)
        
        if remote_preference and ('remote' in location or 'anywhere' in location):
            return 1.0
        
        if user_location and user_location in location:
            return 1.0
        
        # Check for nearby locations or country matches
        if user_location:
            user_parts = user_location.split(',')
            for part in user_parts:
                if part.strip() in location:
                    return 0.8
        
        return 0.5  # Default for unknown locations

    def _calculate_salary_score(self, salary: str) -> float:
        """Calculate salary match score"""
        if not salary:
            return 0.5  # Default if no salary info
        
        user_min_salary = self.user_profile.get('salary_min', 0)
        if user_min_salary == 0:
            return 0.5
        
        # Extract salary numbers
        salary_numbers = re.findall(r'[\d,]+', salary.replace('$', '').replace('k', '000'))
        
        if not salary_numbers:
            return 0.5
        
        try:
            job_salary = int(salary_numbers[0].replace(',', ''))
            if 'k' in salary.lower():
                job_salary *= 1000
            
            if job_salary >= user_min_salary:
                return 1.0
            else:
                return job_salary / user_min_salary
                
        except (ValueError, IndexError):
            return 0.5

    def _calculate_company_score(self, company: str) -> float:
        """Calculate company preference score"""
        preferred_companies = [c.lower() for c in self.user_profile.get('preferred_companies', [])]
        blacklisted_companies = [c.lower() for c in self.user_profile.get('blacklisted_companies', [])]
        
        if company in blacklisted_companies:
            return 0.0
        
        if company in preferred_companies:
            return 1.0
        
        return 0.5  # Default for unknown companies

    def _calculate_title_relevance(self, title: str) -> float:
        """Calculate job title relevance score"""
        preferred_roles = [role.lower() for role in self.user_profile.get('preferred_roles', [])]
        
        if not preferred_roles:
            return 0.5
        
        relevance_score = 0.0
        for role in preferred_roles:
            if role in title:
                relevance_score += 1.0
            elif any(word in title for word in role.split()):
                relevance_score += 0.5
        
        return min(relevance_score / len(preferred_roles), 1.0)

    def _calculate_description_match(self, description: str) -> float:
        """Calculate job description match score"""
        user_keywords = self.user_profile.get('keywords', [])
        if not user_keywords:
            return 0.5
        
        matches = sum(1 for keyword in user_keywords if keyword.lower() in description)
        return min(matches / len(user_keywords), 1.0)

    def _calculate_requirements_match(self, requirements: str) -> float:
        """Calculate requirements match score"""
        user_skills = [skill.lower() for skill in self.user_profile.get('skills', [])]
        if not user_skills:
            return 0.5
        
        matches = sum(1 for skill in user_skills if skill in requirements)
        return min(matches / len(user_skills), 1.0)

    def _calculate_nlp_similarity(self, description: str) -> float:
        """Calculate NLP-based similarity score"""
        if not NLP_AVAILABLE:
            return 0.5
        
        try:
            user_profile_text = ' '.join([
                ' '.join(self.user_profile.get('skills', [])),
                ' '.join(self.user_profile.get('preferred_roles', [])),
                self.user_profile.get('bio', '')
            ])
            
            if not user_profile_text.strip():
                return 0.5
            
            # Create TF-IDF vectors
            corpus = [user_profile_text, description]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity[0][0])
            
        except Exception as e:
            logger.error(f"NLP similarity calculation error: {e}")
            return 0.5

    def _calculate_sentiment_score(self, description: str) -> float:
        """Calculate sentiment score of job description"""
        positive_words = ['exciting', 'innovative', 'growth', 'opportunity', 'benefits', 'flexible']
        negative_words = ['urgent', 'immediate', 'stressful', 'demanding', 'overtime']
        
        positive_count = sum(1 for word in positive_words if word in description)
        negative_count = sum(1 for word in negative_words if word in description)
        
        if positive_count + negative_count == 0:
            return 0.5
        
        return positive_count / (positive_count + negative_count)

    def _calculate_urgency_score(self, title: str, description: str) -> float:
        """Calculate urgency/competition score"""
        urgency_keywords = ['urgent', 'immediate', 'asap', 'quickly', 'fast', 'right away']
        combined_text = f"{title} {description}"
        
        urgency_count = sum(1 for keyword in urgency_keywords if keyword in combined_text)
        return min(urgency_count / len(urgency_keywords), 1.0)

    def _calculate_competition_score(self, title: str, description: str) -> float:
        """Calculate competition level score"""
        high_competition = ['senior', 'lead', 'principal', 'architect', 'director']
        low_competition = ['junior', 'entry', 'trainee', 'intern']
        
        combined_text = f"{title} {description}"
        
        high_comp_count = sum(1 for keyword in high_competition if keyword in combined_text)
        low_comp_count = sum(1 for keyword in low_competition if keyword in combined_text)
        
        if high_comp_count > low_comp_count:
            return 0.8  # High competition
        elif low_comp_count > high_comp_count:
            return 0.3  # Low competition
        else:
            return 0.5  # Medium competition

    def _calculate_growth_potential(self, title: str, description: str, company: str) -> float:
        """Calculate growth potential score"""
        growth_keywords = ['growth', 'career', 'advancement', 'promotion', 'development', 'learning']
        startup_keywords = ['startup', 'early stage', 'series a', 'series b', 'funding']
        
        combined_text = f"{title} {description} {company}"
        
        growth_count = sum(1 for keyword in growth_keywords if keyword in combined_text)
        startup_count = sum(1 for keyword in startup_keywords if keyword in combined_text)
        
        score = (growth_count * 0.1) + (startup_count * 0.2)
        return min(score, 1.0)

    def get_scoring_explanation(self, metrics: ScoringMetrics) -> str:
        """Generate human-readable explanation of scoring"""
        explanation = f"""
📊 JOB SCORING BREAKDOWN
Overall Score: {metrics.overall_score}%

🎯 Skills Match: {metrics.skills_score}%
💼 Experience Level: {metrics.experience_score}%
📍 Location Preference: {metrics.location_score}%
💰 Salary Match: {metrics.salary_score}%
🏢 Company Preference: {metrics.company_score}%
📝 Title Relevance: {metrics.title_relevance}%
📋 Description Match: {metrics.description_match}%
🔍 Requirements Match: {metrics.requirements_match}%
🤖 NLP Similarity: {metrics.nlp_similarity}%

📈 Additional Factors:
• Sentiment Score: {metrics.sentiment_score}%
• Urgency Level: {metrics.urgency_score}%
• Competition Level: {metrics.competition_score}%
• Growth Potential: {metrics.growth_potential}%
"""
        return explanation

    def save_scoring_data(self, job_id: str, metrics: ScoringMetrics, db_path: str = "job_bot.db"):
        """Save scoring data to database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create scoring table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_scoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT,
                    timestamp TIMESTAMP,
                    overall_score REAL,
                    skills_score REAL,
                    experience_score REAL,
                    location_score REAL,
                    salary_score REAL,
                    company_score REAL,
                    title_relevance REAL,
                    description_match REAL,
                    requirements_match REAL,
                    nlp_similarity REAL,
                    sentiment_score REAL,
                    urgency_score REAL,
                    competition_score REAL,
                    growth_potential REAL
                )
            ''')
            
            # Insert scoring data
            cursor.execute('''
                INSERT INTO job_scoring (
                    job_id, timestamp, overall_score, skills_score, experience_score,
                    location_score, salary_score, company_score, title_relevance,
                    description_match, requirements_match, nlp_similarity,
                    sentiment_score, urgency_score, competition_score, growth_potential
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id, datetime.now(), metrics.overall_score, metrics.skills_score,
                metrics.experience_score, metrics.location_score, metrics.salary_score,
                metrics.company_score, metrics.title_relevance, metrics.description_match,
                metrics.requirements_match, metrics.nlp_similarity, metrics.sentiment_score,
                metrics.urgency_score, metrics.competition_score, metrics.growth_potential
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving scoring data: {e}")

if __name__ == "__main__":
    # Example usage
    user_profile = {
        'skills': ['Python', 'AWS', 'Docker', 'Kubernetes', 'DevOps'],
        'experience_years': 5,
        'preferred_roles': ['DevOps Engineer', 'Cloud Engineer', 'SRE'],
        'location': 'New York, NY',
        'remote_only': True,
        'salary_min': 100000,
        'preferred_companies': ['Google', 'Amazon', 'Microsoft'],
        'blacklisted_companies': ['Facebook']
    }
    
    scorer = AdvancedJobScorer(user_profile)
    
    # Test job data
    job_data = {
        'title': 'Senior DevOps Engineer',
        'company': 'Tech Company',
        'description': 'Looking for an experienced DevOps engineer with Python, AWS, and Docker experience',
        'requirements': 'Must have 3+ years Python, AWS, Kubernetes experience',
        'location': 'Remote',
        'salary': '$120,000 - $150,000'
    }
    
    metrics = scorer.score_job(job_data)
    print(scorer.get_scoring_explanation(metrics))
