# Bug Tracker - Flask Web Application

A modern, responsive bug tracking system built with Flask, designed for efficient bug management and team collaboration.

## 🚀 Features

- **User Authentication**: Secure login/registration system
- **Bug Management**: Create, edit, assign, and track bugs
- **Status Tracking**: New, In Progress, Resolved, Closed
- **Priority Levels**: High, Medium, Low priority classification
- **Comment System**: Collaborative discussion on bugs
- **Dashboard**: Overview with statistics and recent activity
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **Search & Filter**: Advanced filtering and search capabilities

## 🛠️ Technology Stack

- **Backend**: Python Flask with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, Font Awesome, Custom CSS/JS
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: Vercel Serverless Functions
- **Development**: Docker & Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development without Docker)
- Git

## 🚀 Quick Start with Docker

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Ind-Project
```

### 2. Run Local Development
```bash
# Make the script executable (Linux/Mac)
chmod +x local-deploy.sh

# Start the application
./local-deploy.sh
```

### 3. Access the Application
- **URL**: http://localhost:5000
- **Admin Login**: 
  - Username: `admin`
  - Password: `admin123`

## 🐳 Docker Commands

```bash
# Start application
./local-deploy.sh

# Stop application
./local-deploy.sh stop

# View logs
./local-deploy.sh logs

# Restart application
./local-deploy.sh restart

# Open shell in container
./local-deploy.sh shell

# Clean up everything
./local-deploy.sh clean
```

## 💻 Local Development (Without Docker)

### 1. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Initialize Database
```bash
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 5. Run Application
```bash
python app.py
```

## 🌐 Deployment to Vercel

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Deploy
```bash
vercel --prod
```

### 3. Configure Environment Variables
Set the following in Vercel dashboard:
- `SECRET_KEY`: Your secret key
- `DATABASE_URL`: PostgreSQL connection string
- `MAIL_SERVER`: SMTP server (optional)
- `MAIL_USERNAME`: SMTP username (optional)
- `MAIL_PASSWORD`: SMTP password (optional)

## 📁 Project Structure

```
Ind-Project/
├── api/                    # Vercel serverless functions
│   └── index.py
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/              # Jinja2 templates
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── bug_form.html
│   ├── bug_detail.html
│   ├── bugs_list.html
│   └── report_bug.html
├── instance/               # Database and uploads
├── app.py                  # Flask application factory
├── models.py               # Database models
├── routes.py               # Application routes
├── forms.py                # WTForms definitions
├── config.py               # Configuration settings
├── wsgi.py                 # WSGI entry point
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel configuration
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Full Docker setup
├── docker-compose.dev.yml # Development Docker setup
├── nginx.conf             # Nginx configuration
└── local-deploy.sh        # Local deployment script
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `SECRET_KEY` | Flask secret key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///instance/bugtracker.db` |
| `MAIL_SERVER` | SMTP server | `localhost` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USE_TLS` | Use TLS for email | `1` |
| `MAIL_USERNAME` | SMTP username | Optional |
| `MAIL_PASSWORD` | SMTP password | Optional |

### Database Models

- **User**: User authentication and profile
- **Bug**: Bug reports with status, priority, and metadata
- **BugComment**: Comments and discussions on bugs

## 🎨 Customization

### Styling
- Edit `static/css/style.css` for custom styles
- Modify Bootstrap variables in CSS
- Update `templates/base.html` for layout changes

### Functionality
- Add new routes in `routes.py`
- Create new forms in `forms.py`
- Extend models in `models.py`

## 🧪 Testing

```bash
# Run tests (when implemented)
python -m pytest

# Check code style
flake8 .

# Type checking
mypy .
```

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard/Home page |
| `/login` | GET, POST | User login |
| `/register` | GET, POST | User registration |
| `/logout` | POST | User logout |
| `/bugs` | GET | List all bugs |
| `/bugs/new` | GET, POST | Create new bug |
| `/bugs/<id>` | GET | View bug details |
| `/bugs/<id>/edit` | GET, POST | Edit bug |
| `/bugs/<id>/comment` | POST | Add comment |
| `/api/stats` | GET | Bug statistics |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the Docker logs: `./local-deploy.sh logs`

## 🔄 Updates

To update the application:
1. Pull latest changes
2. Rebuild containers: `./local-deploy.sh clean && ./local-deploy.sh`
3. Check for database migrations if needed
