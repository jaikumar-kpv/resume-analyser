import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

class JobMatcher:
    def __init__(self, job_data_path: str = "data/job_listings.csv"):
        self.job_data = pd.read_csv(job_data_path)
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self._prepare_job_vectors()
    
    def _prepare_job_vectors(self):
        """Prepare TF-IDF vectors for job descriptions"""
        job_texts = self.job_data['description'] + " " + self.job_data['required_skills']
        self.job_vectors = self.vectorizer.fit_transform(job_texts)
    
    def match_jobs(self, resume_skills: List[str], resume_experience: List[Dict], top_n: int = 5) -> pd.DataFrame:
        """Match resume to jobs based on skills and experience"""
        resume_text = " ".join(resume_skills) + " " + " ".join([exp.get("organization", "") for exp in resume_experience])
        resume_vector = self.vectorizer.transform([resume_text])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(resume_vector, self.job_vectors)
        self.job_data['similarity'] = similarities[0]
        
        # Get top matches
        matched_jobs = self.job_data.sort_values('similarity', ascending=False).head(top_n)
        
        return matched_jobs
    
    def get_job_details(self, job_id: str) -> Dict:
        """Get details for a specific job"""
        job = self.job_data[self.job_data['id'] == job_id].iloc[0]
        return job.to_dict()