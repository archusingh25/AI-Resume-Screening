# AI-Powered Resume Screening System

An intelligent resume screening system that uses Natural Language Processing (NLP) to parse, analyze, and score resumes against job postings. The system includes skill matching, ranking algorithms, and bias reduction mechanisms to ensure fair and efficient candidate evaluation.

## Features

- **NLP-based CV Parsing**: Automatically extracts information from resumes using spaCy
- **Skill Matching**: Intelligent matching of candidate skills against job requirements
- **Automated Scoring**: Multi-criteria scoring system (skills, experience, education)
- **Bias Reduction**: Mechanisms to reduce unconscious bias in screening
- **Ranking System**: Automated ranking of candidates based on multiple factors
- **RESTful API**: FastAPI-based API for easy integration

## Tech Stack

- **Python 3.8+**
- **FastAPI**: Modern, fast web framework for building APIs
- **spaCy**: Advanced NLP library for text processing
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: ORM for database operations
- **scikit-learn**: Machine learning utilities for similarity calculations

## Project Structure

```
AI-Resume-Screening/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── resume.py          # Resume endpoints
│   │       ├── job_posting.py    # Job posting endpoints
│   │       └── screening.py       # Screening endpoints
│   ├── core/
│   │   ├── config.py              # Application configuration
│   │   └── database.py            # Database setup
│   ├── models/
│   │   ├── resume.py              # Resume database model
│   │   ├── job_posting.py         # Job posting model
│   │   └── screening_result.py    # Screening result model
│   ├── schemas/
│   │   ├── resume.py              # Resume Pydantic schemas
│   │   ├── job_posting.py         # Job posting schemas
│   │   └── screening.py           # Screening schemas
│   ├── services/
│   │   ├── resume_parser.py       # NLP-based resume parsing
│   │   ├── skill_matcher.py       # Skill matching algorithms
│   │   ├── scorer.py              # Scoring system
│   │   └── bias_reducer.py        # Bias reduction mechanisms
│   └── main.py                    # FastAPI application
├── scripts/
│   ├── init_db.py                 # Database initialization
│   └── download_spacy_model.py    # spaCy model download
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package manager)

### 2. Clone and Navigate to Project

```bash
cd AI-Resume-Screening
```

### 3. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Download spaCy Model

```bash
python scripts/download_spacy_model.py
```

Or manually:
```bash
python -m spacy download en_core_web_sm
```

### 6. Set Up PostgreSQL Database

Create a PostgreSQL database:

```sql
CREATE DATABASE resume_screening_db;
```

### 7. Configure Environment Variables

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/resume_screening_db
SECRET_KEY=your-secret-key-here
```

### 8. Initialize Database

```bash
python scripts/init_db.py
```

### 9. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## API Endpoints

### Resume Management

- `POST /api/v1/resumes/upload` - Upload and parse a resume (PDF, DOCX, or TXT)
- `GET /api/v1/resumes/` - List all resumes
- `GET /api/v1/resumes/{resume_id}` - Get a specific resume
- `DELETE /api/v1/resumes/{resume_id}` - Delete a resume

### Job Posting Management

- `POST /api/v1/job-postings/` - Create a new job posting
- `GET /api/v1/job-postings/` - List all job postings
- `GET /api/v1/job-postings/{job_posting_id}` - Get a specific job posting
- `PUT /api/v1/job-postings/{job_posting_id}` - Update a job posting
- `DELETE /api/v1/job-postings/{job_posting_id}` - Delete a job posting

### Screening

- `POST /api/v1/screening/screen` - Screen a single resume against a job posting
- `POST /api/v1/screening/screen-batch` - Screen multiple resumes and get ranked results
- `GET /api/v1/screening/results/{job_posting_id}` - Get all screening results for a job posting
- `GET /api/v1/screening/result/{result_id}` - Get a specific screening result

## Usage Example

### 1. Upload a Resume

```bash
curl -X POST "http://localhost:8000/api/v1/resumes/upload" \
  -F "file=@resume.pdf"
```

### 2. Create a Job Posting

```bash
curl -X POST "http://localhost:8000/api/v1/job-postings/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer...",
    "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "preferred_skills": ["AWS", "Kubernetes", "Machine Learning"],
    "min_experience_years": 5,
    "required_education": "Bachelor's"
  }'
```

### 3. Screen a Resume

```bash
curl -X POST "http://localhost:8000/api/v1/screening/screen" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": 1,
    "job_posting_id": 1
  }'
```

### 4. Screen Multiple Resumes

```bash
curl -X POST "http://localhost:8000/api/v1/screening/screen-batch?job_posting_id=1" \
  -H "Content-Type: application/json" \
  -d '[1, 2, 3]'
```

## Scoring System

The system calculates scores based on:

1. **Skill Match Score (50% weight)**: Matches candidate skills against required and preferred skills
2. **Experience Score (30% weight)**: Compares candidate experience with job requirements
3. **Education Score (20% weight)**: Matches education level with requirements

### Bias Reduction

The system includes bias reduction mechanisms:

- **Anonymization**: Removes personal identifiers that could lead to bias
- **Bias Scoring**: Calculates bias indicators in resumes
- **Anonymized Scoring**: Provides scores adjusted for bias reduction

## Development

### Running Tests

```bash
# Add pytest to requirements.txt and run:
pytest
```

### Code Structure

- **Models**: SQLAlchemy ORM models for database tables
- **Schemas**: Pydantic models for request/response validation
- **Services**: Business logic for parsing, matching, and scoring
- **API**: FastAPI route handlers

## Future Enhancements

- [ ] Advanced NLP models for better parsing accuracy
- [ ] Machine learning-based skill matching
- [ ] Integration with job boards
- [ ] Dashboard for visualizing screening results
- [ ] Multi-language support
- [ ] Advanced bias detection algorithms
- [ ] Resume ranking with custom weights
- [ ] Export functionality for screening results

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the GitHub repository. 
