"""
Resume Analysis and Job Matching System for Payo
Processes resumes and matches them with job requirements using NLP
"""

import re
import json
from typing import Dict, List, Any
from collections import Counter


class ResumeJobMatcher:
    """
    Analyzes resumes and matches them against job requirements
    """
    
    # Common skill variations for normalization
    SKILL_ALIASES = {
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'react.js': 'react',
        'node.js': 'node',
        'nodejs': 'node',
        'react native': 'reactnative',
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'db': 'database',
        'sql': 'database',
        'nosql': 'database',
        'ci/cd': 'cicd',
        'devops': 'devops',
        'aws': 'cloud',
        'azure': 'cloud',
        'gcp': 'cloud',
    }
    
    # Common soft skills
    SOFT_SKILLS = [
        'communication', 'teamwork', 'leadership', 'problem solving',
        'critical thinking', 'time management', 'adaptability', 
        'creativity', 'collaboration', 'analytical'
    ]
    
    def __init__(self, resume_text: str, job_description: str):
        self.resume_text = resume_text.lower() if resume_text else ""
        self.job_description = job_description.lower() if job_description else ""
        
    def clean_text(self, text: str) -> str:
        """Remove noise from text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters except periods and commas
        text = re.sub(r'[^a-zA-Z0-9\s.,+#\-/()]', '', text)
        return text.strip()
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract and normalize skills from text"""
        text = self.clean_text(text)
        
        # Common technical skills patterns
        tech_patterns = [
            r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|php|swift|kotlin|go|rust)\b',
            r'\b(react|angular|vue|django|flask|spring|express|laravel)\b',
            r'\b(sql|nosql|mongodb|postgresql|mysql|oracle|redis)\b',
            r'\b(aws|azure|gcp|docker|kubernetes|jenkins|git)\b',
            r'\b(html|css|bootstrap|tailwind|sass)\b',
            r'\b(machine learning|deep learning|nlp|computer vision|ai)\b',
            r'\b(agile|scrum|kanban|jira|devops|ci/cd)\b',
        ]
        
        skills = set()
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update([m.lower() for m in matches])
        
        # Check for soft skills
        for soft_skill in self.SOFT_SKILLS:
            if soft_skill in text:
                skills.add(soft_skill)
        
        # Normalize skills
        normalized_skills = []
        for skill in skills:
            normalized = self.SKILL_ALIASES.get(skill.lower(), skill.lower())
            normalized_skills.append(normalized)
        
        return list(set(normalized_skills))  # Remove duplicates
    
    def extract_experience(self, resume_text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume"""
        experiences = []
        
        # Look for experience section
        exp_section_match = re.search(
            r'(experience|work history|employment history)(.*?)(?=education|skills|$)',
            resume_text.lower(),
            re.DOTALL
        )
        
        if not exp_section_match:
            return experiences
        
        exp_text = exp_section_match.group(2)
        
        # Try to extract job entries (very basic pattern)
        # Look for patterns like: "Software Engineer at Company (2020-2022)"
        job_patterns = [
            r'([a-z\s]+?)\s+at\s+([a-z\s]+?)[\s,]*\(?(\d{4}[-–]\d{4}|\d{4}\s*[-–]\s*present)\)?',
            r'([a-z\s]+?)[\s,]+([a-z\s]+company|corp|inc|ltd)[\s,]*\(?(\d{4}[-–]\d{4}|\d{4}\s*[-–]\s*present)\)?',
        ]
        
        for pattern in job_patterns:
            matches = re.findall(pattern, exp_text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 3:
                    experiences.append({
                        "job_title": match[0].strip().title(),
                        "company": match[1].strip().title(),
                        "duration": match[2].strip(),
                        "responsibilities": []
                    })
        
        return experiences[:5]  # Limit to 5 most recent
    
    def extract_required_experience(self, job_text: str) -> Dict[str, Any]:
        """Extract required experience from job description"""
        # Look for experience requirements
        years_match = re.search(r'(\d+)\+?\s*years?\s*(of)?\s*experience', job_text)
        years = years_match.group(1) if years_match else ""
        
        # Try to extract role/domain
        role_match = re.search(r'experience\s*(in|as|with)\s+([a-z\s]+)', job_text)
        role = role_match.group(2).strip() if role_match else ""
        
        domain = ""
        domain_keywords = ['software', 'web', 'mobile', 'data', 'devops', 'machine learning']
        for keyword in domain_keywords:
            if keyword in job_text:
                domain = keyword
                break
        
        return {
            "years": f"{years}+" if years else "",
            "role": role.title() if role else "",
            "domain": domain.title() if domain else ""
        }
    
    def calculate_skill_match(self, resume_skills: List[str], required_skills: List[str], 
                            preferred_skills: List[str]) -> float:
        """Calculate skill match score (0 to 1)"""
        if not required_skills and not preferred_skills:
            return 0.5  # No requirements specified
        
        resume_set = set(resume_skills)
        required_set = set(required_skills)
        preferred_set = set(preferred_skills)
        
        # Match required skills (weight 0.8)
        required_match = len(resume_set & required_set) / len(required_set) if required_set else 1.0
        
        # Match preferred skills (weight 0.2)
        preferred_match = len(resume_set & preferred_set) / len(preferred_set) if preferred_set else 0.5
        
        # Combined score
        score = (required_match * 0.8) + (preferred_match * 0.2)
        
        return min(score, 1.0)
    
    def calculate_experience_match(self, resume_experiences: List[Dict], 
                                  required_exp: Dict[str, Any]) -> float:
        """Calculate experience match score (0 to 1)"""
        if not resume_experiences:
            return 0.0
        
        if not required_exp.get('years'):
            return 0.7  # No specific requirement
        
        # Extract years from requirement
        try:
            required_years = int(re.search(r'\d+', required_exp['years']).group())
        except:
            required_years = 0
        
        # Estimate total years from resume
        total_years = len(resume_experiences)  # Very basic estimate
        
        if total_years >= required_years:
            return 1.0
        elif total_years >= required_years * 0.7:
            return 0.8
        elif total_years >= required_years * 0.5:
            return 0.5
        else:
            return 0.3
    
    def categorize_match(self, score: float) -> Dict[str, str]:
        """Categorize match score into label, color, and recommendation"""
        if score >= 0.70:
            return {
                "match_label": "Strong Fit",
                "ui_color": "green",
                "recommendation": "Highly recommended"
            }
        elif score >= 0.40:
            return {
                "match_label": "Moderate Fit",
                "ui_color": "yellow",
                "recommendation": "Review profile"
            }
        else:
            return {
                "match_label": "Weak Fit",
                "ui_color": "red",
                "recommendation": "Low match"
            }
    
    def analyze(self) -> Dict[str, Any]:
        """Main analysis function - returns structured JSON"""
        # STEP 1: Process Resume
        resume_skills = self.extract_skills(self.resume_text)
        resume_experiences = self.extract_experience(self.resume_text)
        
        # STEP 2: Process Job Description
        job_required_skills = self.extract_skills(self.job_description)
        
        # Separate required vs preferred (basic heuristic)
        # Skills mentioned in "required" section vs "preferred" section
        required_section = re.search(r'required(.*?)(?=preferred|qualifications|$)', 
                                    self.job_description, re.DOTALL)
        preferred_section = re.search(r'preferred(.*?)(?=required|qualifications|$)', 
                                     self.job_description, re.DOTALL)
        
        required_skills = self.extract_skills(required_section.group(1)) if required_section else job_required_skills[:len(job_required_skills)//2]
        preferred_skills = self.extract_skills(preferred_section.group(1)) if preferred_section else job_required_skills[len(job_required_skills)//2:]
        
        required_exp = self.extract_required_experience(self.job_description)
        
        # STEP 3: Calculate Matching Scores
        skill_match_score = self.calculate_skill_match(resume_skills, required_skills, preferred_skills)
        experience_match_score = self.calculate_experience_match(resume_experiences, required_exp)
        
        # Final weighted score: 70% skills, 30% experience
        final_match_score = (skill_match_score * 0.7) + (experience_match_score * 0.3)
        final_match_score = min(final_match_score, 1.0)  # Cap at 1.0
        
        # STEP 4 & 5: Categorize and prepare output
        dashboard_result = self.categorize_match(final_match_score)
        
        return {
            "resume_extracted": {
                "skills": resume_skills,
                "experience": resume_experiences
            },
            "job_requirements": {
                "required_skills": required_skills,
                "preferred_skills": preferred_skills,
                "required_experience": required_exp
            },
            "matching": {
                "skill_match_score": round(skill_match_score, 2),
                "experience_match_score": round(experience_match_score, 2),
                "final_match_score": round(final_match_score, 2)
            },
            "dashboard_result": dashboard_result
        }


def analyze_resume_for_job(resume_text: str, job_description: str) -> str:
    """
    Convenience function that returns JSON string
    
    Args:
        resume_text: Raw text from resume
        job_description: Job description text
        
    Returns:
        JSON string with analysis results
    """
    matcher = ResumeJobMatcher(resume_text, job_description)
    result = matcher.analyze()
    return json.dumps(result, indent=2)
