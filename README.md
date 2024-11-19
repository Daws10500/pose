# Strength Engine

A comprehensive fitness application that enables coaches to prescribe workout programs and athletes to track their performance with advanced video analysis.

## Features

- Coaches can create and manage workout programs
- Athletes can track exercises and log performance
- Real-time pose detection and form analysis using MediaPipe
- Video recording and trimming capabilities
- Performance analytics and progress tracking

## Tech Stack

### Backend
- Flask (Python web framework)
- PostgreSQL with TimeScaleDB (Database)
- Celery & Redis (Task Queue)
- MediaPipe & OpenCV (Video Processing)

### Frontend
- Flutter (Mobile/Web App)
- React (Optional Web Interface)

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- Flutter SDK
- Node.js (for React frontend)

### Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the development server:
```bash
flask run
```

### Frontend Setup

1. Install Flutter dependencies:
```bash
cd frontend
flutter pub get
```

2. Run the Flutter app:
```bash
flutter run
```

## Development

### Running Tests
```bash
pytest
```

### Code Style
We use Black for Python code formatting and ESLint for JavaScript/TypeScript.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.


Let me first check and clean up any running Flask processes:
$ lsof -i :5001

Ran terminal command
$ kill -9 17512

$ python3 -m flask --app app run --port 5001

$ curl -X POST http://localhost:5001/api/v1/auth/register -H Content-Type: application/json -d {"email": "test3@example.com", "password": "testpassword123", "name": "Test User 3", "role": "coach"}


