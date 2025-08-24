# AI Resume Advisor

An intelligent Django web application that analyzes resumes and provides personalized career advice and job matching recommendations.

## Features

- **Resume Analysis**: Upload and analyze resumes using AI-powered text processing
- **Career Advice**: Get personalized career recommendations based on resume content
- **Job Matching**: Find relevant job opportunities that match your skills and experience
- **User Authentication**: Secure login and registration system
- **Dashboard**: Comprehensive dashboard to track your resume analysis history
- **Modern UI**: Clean and responsive user interface

## Technology Stack

- **Backend**: Django 4.x
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (development), PostgreSQL (production ready)
- **AI/ML**: Natural Language Processing for resume analysis
- **Deployment**: Nginx configuration included

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-resume-advisor.git
   cd ai-resume-advisor
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   Open your browser and go to `http://127.0.0.1:8000/`

## Usage

1. **Register/Login**: Create an account or log in to your existing account
2. **Upload Resume**: Upload your resume in PDF format
3. **Get Analysis**: View detailed analysis of your resume including skills, experience, and recommendations
4. **Career Advice**: Receive personalized career advice based on your profile
5. **Job Matching**: Find relevant job opportunities that match your skills

## Project Structure

```
ai_resume_advisor/
├── resume_analyzer/          # Django project settings
├── resume_app/              # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── forms.py             # Form definitions
│   ├── resume_analyzer.py   # AI analysis logic
│   ├── templates/           # HTML templates
│   └── static/              # CSS, JS, and images
├── media/                   # User uploaded files
├── static/                  # Static files
├── nginx/                   # Nginx configuration
├── requirements.txt         # Python dependencies
└── manage.py               # Django management script
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
```

### Production Deployment

1. Set `DEBUG=False` in settings
2. Configure a production database (PostgreSQL recommended)
3. Set up static file serving
4. Configure Nginx using the provided configuration in `nginx/conf.d/`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

## Acknowledgments

- Django community for the excellent web framework
- Contributors and users of this project