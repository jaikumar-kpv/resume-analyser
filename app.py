from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from resume_parser import ResumeParser
from job_matcher import JobMatcher
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

resume_parser = ResumeParser()
job_matcher = JobMatcher()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return redirect(request.url)
        
        file = request.files['resume']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save the file with a unique name
            filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Parse resume
            resume_data = resume_parser.parse_resume(filepath)
            
            # Match jobs
            matched_jobs = job_matcher.match_jobs(resume_data['skills'], resume_data['experience'])
            
            # Convert to dict for template
            jobs_list = matched_jobs.to_dict('records')
            
            return render_template('results.html', 
                                resume=resume_data, 
                                jobs=jobs_list,
                                match_count=len(jobs_list))
    
    return render_template('index.html')

@app.route('/job/<job_id>')
def job_details(job_id):
    job = job_matcher.get_job_details(job_id)
    return render_template('job_details.html', job=job)

if __name__ == '__main__':
    app.run(debug=True)