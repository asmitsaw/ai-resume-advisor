import re
import nltk
import spacy
import PyPDF2
import docx
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    # If model not found, download it
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load('en_core_web_sm')


class ResumeParser:
    """Class to parse resume text and extract relevant information"""
    
    def __init__(self):
        self.stopwords = nltk.corpus.stopwords.words('english')
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
        return text
    
    def extract_text_from_docx(self, docx_path):
        """Extract text from DOCX file"""
        doc = docx.Document(docx_path)
        text = [paragraph.text for paragraph in doc.paragraphs]
        return '\n'.join(text)
    
    def extract_text(self, file_path):
        """Extract text from resume file based on extension"""
        if file_path.endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            raise ValueError("Unsupported file format")
    
    def extract_skills(self, text):
        """Extract skills from resume text"""
        # Common technical skills
        skill_keywords = [
            # Programming languages
            'python', 'java', 'javascript', 'c\+\+', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust',
            # Web development
            'html', 'css', 'react', 'angular', 'vue', 'node\.js', 'express', 'django', 'flask', 'spring', 'asp\.net',
            # Data science
            'machine learning', 'deep learning', 'data analysis', 'statistics', 'r', 'pandas', 'numpy', 'tensorflow', 'pytorch',
            'scikit-learn', 'tableau', 'power bi', 'sql', 'database', 'big data', 'hadoop', 'spark',
            # Cloud
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'devops', 'ci/cd', 'jenkins',
            # Other technical skills
            'git', 'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'jira',
            # Soft skills
            'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking', 'time management',
            'project management', 'creativity', 'adaptability', 'collaboration'
        ]
        
        # Create regex pattern for skills
        pattern = re.compile(r'\b(' + '|'.join(skill_keywords) + r')\b', re.IGNORECASE)
        
        # Find all matches
        skill_matches = pattern.findall(text.lower())
        
        # Count occurrences of each skill
        skill_counts = {}
        for skill in skill_matches:
            if skill in skill_counts:
                skill_counts[skill] += 1
            else:
                skill_counts[skill] = 1
        
        # Sort skills by frequency
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'all_skills': [skill[0] for skill in sorted_skills],
            'top_skills': [skill[0] for skill in sorted_skills[:10]],
            'skill_counts': skill_counts
        }
    
    def extract_education(self, text):
        """Extract education information from resume text"""
        # Education related keywords
        education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'degree', 'bs', 'ms', 'ba', 'ma', 'mba',
            'university', 'college', 'institute', 'school', 'academy', 'gpa', 'major', 'minor',
            'graduated', 'graduation', 'diploma', 'certificate'
        ]
        
        # Create regex pattern for education
        pattern = re.compile(r'([^.]*(' + '|'.join(education_keywords) + r')[^.]*)\.',
                            re.IGNORECASE)
        
        # Find all matches
        education_matches = pattern.findall(text)
        
        # Extract education sentences
        education_info = [match[0].strip() for match in education_matches]
        
        # Process with spaCy to extract organizations
        education_orgs = []
        for edu in education_info:
            doc = nlp(edu)
            for ent in doc.ents:
                if ent.label_ == 'ORG':
                    education_orgs.append(ent.text)
        
        return {
            'education_sentences': education_info,
            'institutions': list(set(education_orgs))
        }
    
    def extract_experience(self, text):
        """Extract work experience information from resume text"""
        # Experience related keywords
        experience_keywords = [
            'experience', 'work', 'employment', 'job', 'career', 'position', 'role',
            'company', 'organization', 'firm', 'employer', 'corporation', 'enterprise',
            'years', 'months', 'responsibilities', 'duties', 'tasks', 'achievements',
            'managed', 'led', 'developed', 'created', 'implemented', 'designed', 'coordinated'
        ]
        
        # Create regex pattern for experience
        pattern = re.compile(r'([^.]*(' + '|'.join(experience_keywords) + r')[^.]*)\.',
                            re.IGNORECASE)
        
        # Find all matches
        experience_matches = pattern.findall(text)
        
        # Extract experience sentences
        experience_info = [match[0].strip() for match in experience_matches]
        
        # Process with spaCy to extract organizations and dates
        experience_orgs = []
        experience_dates = []
        
        for exp in experience_info:
            doc = nlp(exp)
            for ent in doc.ents:
                if ent.label_ == 'ORG':
                    experience_orgs.append(ent.text)
                elif ent.label_ == 'DATE':
                    experience_dates.append(ent.text)
        
        # Try to extract job titles using patterns
        job_title_pattern = re.compile(r'\b(Senior|Junior|Lead|Chief|Principal|Director|Manager|Engineer|Developer|Analyst|Consultant|Specialist|Coordinator|Administrator|Assistant|Officer|Supervisor|Head|Architect)\s+[A-Za-z]+\b', re.IGNORECASE)
        job_titles = job_title_pattern.findall(text)
        
        return {
            'experience_sentences': experience_info,
            'organizations': list(set(experience_orgs)),
            'dates': list(set(experience_dates)),
            'possible_job_titles': list(set(job_titles))
        }
    
    def generate_summary(self, skills, education, experience):
        """Generate a summary of the resume"""
        summary = "Resume Summary:\n\n"
        
        # Add skills summary
        if skills['top_skills']:
            summary += "Skills: " + ", ".join(skills['top_skills']) + "\n\n"
        
        # Add education summary
        if education['institutions']:
            summary += "Education: " + ", ".join(education['institutions']) + "\n\n"
        
        # Add experience summary
        if experience['organizations']:
            summary += "Experience: " + ", ".join(experience['organizations']) + "\n\n"
            
        if experience['possible_job_titles']:
            summary += "Roles: " + ", ".join(experience['possible_job_titles']) + "\n"
        
        return summary
    
    def parse_resume(self, file_path):
        """Parse resume and extract all relevant information"""
        # Extract text from resume
        text = self.extract_text(file_path)
        
        # Extract information
        skills = self.extract_skills(text)
        education = self.extract_education(text)
        experience = self.extract_experience(text)
        
        # Generate summary
        summary = self.generate_summary(skills, education, experience)
        
        return {
            'skills': skills,
            'education': education,
            'experience': experience,
            'summary': summary,
            'full_text': text
        }


class CareerAdvisor:
    """Class to provide career advice based on resume analysis"""
    
    def __init__(self):
        # Career paths with required skills
        self.career_paths = {
            'Software Developer': [
                'python', 'java', 'javascript', 'c++', 'c#', 'html', 'css', 'sql', 'git', 'agile'
            ],
            'Data Scientist': [
                'python', 'r', 'sql', 'machine learning', 'statistics', 'pandas', 'numpy', 'tensorflow', 'data analysis'
            ],
            'Web Developer': [
                'html', 'css', 'javascript', 'react', 'angular', 'vue', 'node.js', 'php', 'django', 'flask'
            ],
            'DevOps Engineer': [
                'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'ci/cd', 'git', 'linux', 'bash'
            ],
            'Product Manager': [
                'agile', 'scrum', 'jira', 'product development', 'user experience', 'market research', 'leadership', 'communication'
            ],
            'UX/UI Designer': [
                'user experience', 'user interface', 'wireframing', 'prototyping', 'figma', 'sketch', 'adobe xd', 'design thinking'
            ],
            'Cybersecurity Specialist': [
                'network security', 'encryption', 'firewall', 'penetration testing', 'security auditing', 'risk assessment', 'compliance'
            ],
            'AI Engineer': [
                'machine learning', 'deep learning', 'neural networks', 'tensorflow', 'pytorch', 'nlp', 'computer vision', 'python'
            ],
            'Cloud Architect': [
                'aws', 'azure', 'gcp', 'cloud migration', 'serverless', 'microservices', 'docker', 'kubernetes'
            ],
            'Business Analyst': [
                'data analysis', 'requirements gathering', 'sql', 'tableau', 'power bi', 'excel', 'business intelligence', 'communication'
            ]
        }
    
    def calculate_career_matches(self, skills):
        """Calculate match percentage for different career paths"""
        user_skills = [skill.lower() for skill in skills['all_skills']]
        
        career_matches = {}
        for career, required_skills in self.career_paths.items():
            # Count matching skills
            matching_skills = [skill for skill in required_skills if skill in user_skills]
            match_percentage = (len(matching_skills) / len(required_skills)) * 100
            
            # Missing skills
            missing_skills = [skill for skill in required_skills if skill not in user_skills]
            
            career_matches[career] = {
                'match_percentage': round(match_percentage, 2),
                'matching_skills': matching_skills,
                'missing_skills': missing_skills
            }
        
        # Sort by match percentage
        sorted_matches = sorted(career_matches.items(), key=lambda x: x[1]['match_percentage'], reverse=True)
        
        return sorted_matches
    
    def identify_strengths_weaknesses(self, resume_analysis):
        """Identify strengths and weaknesses based on resume analysis"""
        strengths = []
        weaknesses = []
        
        # Check for technical skills
        if len(resume_analysis['skills']['top_skills']) >= 5:
            strengths.append("Strong technical skill set with diverse technologies")
        else:
            weaknesses.append("Limited range of technical skills")
        
        # Check for education
        if len(resume_analysis['education']['institutions']) > 0:
            strengths.append("Formal education credentials")
        else:
            weaknesses.append("Limited formal education information")
        
        # Check for experience
        if len(resume_analysis['experience']['organizations']) >= 2:
            strengths.append("Experience across multiple organizations")
        elif len(resume_analysis['experience']['organizations']) == 0:
            weaknesses.append("Limited professional experience")
        
        # Check for job titles
        if len(resume_analysis['experience']['possible_job_titles']) >= 2:
            strengths.append("Diverse role experience")
        
        # Add generic strengths/weaknesses based on skills
        for skill in resume_analysis['skills']['top_skills']:
            if skill in ['leadership', 'management', 'team lead']:
                strengths.append("Leadership experience")
            if skill in ['communication', 'presentation', 'public speaking']:
                strengths.append("Strong communication skills")
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses
        }
    
    def generate_career_advice(self, resume_analysis):
        """Generate career advice based on resume analysis"""
        # Calculate career matches
        career_matches = self.calculate_career_matches(resume_analysis['skills'])
        
        # Identify strengths and weaknesses
        strengths_weaknesses = self.identify_strengths_weaknesses(resume_analysis)
        
        # Get top 3 career paths
        top_careers = career_matches[:3]
        
        # Generate recommended skills to learn
        recommended_skills = []
        for career, details in top_careers:
            recommended_skills.extend(details['missing_skills'])
        
        # Remove duplicates
        recommended_skills = list(set(recommended_skills))
        
        # Generate advice text
        advice = f"Based on your resume analysis, here are some career insights:\n\n"
        
        # Add strengths
        advice += "Strengths:\n"
        for strength in strengths_weaknesses['strengths']:
            advice += f"- {strength}\n"
        
        # Add areas for improvement
        advice += "\nAreas for Improvement:\n"
        for weakness in strengths_weaknesses['weaknesses']:
            advice += f"- {weakness}\n"
        
        # Add career path recommendations
        advice += "\nRecommended Career Paths:\n"
        for career, details in top_careers:
            advice += f"- {career} (Match: {details['match_percentage']}%)\n"
        
        # Add skill recommendations
        advice += "\nRecommended Skills to Learn:\n"
        for skill in recommended_skills[:5]:  # Limit to top 5 skills
            advice += f"- {skill}\n"
        
        # Add general advice
        advice += "\nGeneral Advice:\n"
        advice += "- Keep your resume updated with your latest skills and experiences\n"
        advice += "- Consider obtaining certifications in your field of interest\n"
        advice += "- Build a portfolio of projects to showcase your skills\n"
        advice += "- Network with professionals in your target career path\n"
        
        return {
            'strengths': strengths_weaknesses['strengths'],
            'weaknesses': strengths_weaknesses['weaknesses'],
            'recommended_skills': recommended_skills[:5],
            'career_paths': [{'name': career, 'match_percentage': details['match_percentage']} 
                            for career, details in top_careers],
            'advice': advice
        }


class JobMatcher:
    """Class to match resume with job descriptions"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def match_resume_to_job(self, resume_text, job_description):
        """Match resume to job description using TF-IDF and cosine similarity"""
        # Create corpus with resume and job description
        corpus = [resume_text, job_description]
        
        # Vectorize the corpus
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        
        # Calculate cosine similarity
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Convert to percentage
        match_percentage = round(cosine_sim * 100, 2)
        
        return match_percentage
    
    def extract_job_skills(self, job_description):
        """Extract skills from job description"""
        # Use the same skill extraction logic as in ResumeParser
        parser = ResumeParser()
        skills = parser.extract_skills(job_description)
        
        return skills['all_skills']
    
    def identify_matching_missing_skills(self, resume_skills, job_skills):
        """Identify matching and missing skills"""
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Find matching skills
        matching_skills = [skill for skill in job_skills_lower if skill in resume_skills_lower]
        
        # Find missing skills
        missing_skills = [skill for skill in job_skills_lower if skill not in resume_skills_lower]
        
        return {
            'matching_skills': matching_skills,
            'missing_skills': missing_skills
        }
    
    def match_job(self, resume_analysis, job_title, company, job_description):
        """Match resume to job and provide detailed analysis"""
        # Calculate match percentage
        match_percentage = self.match_resume_to_job(resume_analysis['full_text'], job_description)
        
        # Extract skills from job description
        job_skills = self.extract_job_skills(job_description)
        
        # Identify matching and missing skills
        skills_analysis = self.identify_matching_missing_skills(
            resume_analysis['skills']['all_skills'], job_skills)
        
        return {
            'job_title': job_title,
            'company': company,
            'match_percentage': match_percentage,
            'job_description': job_description,
            'skills_matched': skills_analysis['matching_skills'],
            'skills_missing': skills_analysis['missing_skills']
        }