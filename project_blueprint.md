# Strength Engine Project Blueprint

## Project Overview
A fitness application designed to:
1. Allow coaches to prescribe workout programs.
2. Enable athletes to track their exercises, log actual performance (weights, reps, and RPE), and record videos for form analysis.
3. Integrate MediaPipe Pose for pose detection and real-time feedback.
4. Sync athlete-entered data and videos to the backend database for analysis and feedback.

---

## Key Features
### 1. **Coaches' Dashboard**
- Create, edit, and prescribe workout programs.
- View athlete progress and performance summaries.

### 2. **Athletes' Dashboard**
- View assigned programs with daily breakdowns.
- Log performance metrics (weights, reps, RPE).
- Record and upload exercise videos.
- Trim video clips before uploading.

### 3. **Real-Time Video Processing**
- Use MediaPipe Pose for pose detection and feedback.
- Enable video trimming to focus on relevant parts.

### 4. **Database Sync**
- Program details sent to an external database for athletes.
- Athlete metrics and videos synced back to the core backend.

---

## Technical Stack
### **Backend**
- **Framework**: Flask
- **Database**: PostgreSQL (with TimeScaleDB)
- **Task Queue**: Celery or Redis for background tasks.

### **Frontend**
- **Mobile/Web**: Flutter for athletes and coaches.
- **Web Framework**: React (optional for expanded web interface).

### **Video and AI**
- **Pose Detection**: MediaPipe Pose.
- **Preprocessing**: OpenCV.

### **Deployment**
- Dockerized components for scalability and consistency.

---

## Project Directory Structure

```
strength-engine/
├── README.md
├── project_blueprint.md
├── docker-compose.yml
├── docker/
│   └── (Docker configuration files)
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth/
│   │   │   │   ├── exercises/
│   │   │   │   ├── workouts/
│   │   │   │   ├── users/
│   │   │   │   ├── health/
│   │   │   │   └── performance/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── workout.py
│   │   │   ├── exercise.py
│   │   │   ├── workout_exercise.py
│   │   │   ├── performance_log.py
│   │   │   ├── form_analysis.py
│   │   │   ├── athlete_program.py
│   │   │   └── program.py
│   │   ├── services/
│   │   └── utils/
│   │       ├── auth.py
│   │       └── video.py
│   ├── config.py
│   ├── manage.py
│   ├── requirements.txt
│   ├── migrations/
│   └── Dockerfile
│
└── frontend/
    ├── public/
    ├── src/
    ├── package.json
    ├── package-lock.json
    ├── .env.development
    └── README.md
```

### Key Components:

1. **Backend (Flask)**
   - `app/`: Main application package
   - `api/`: REST API endpoints organized by resource
   - `models/`: Database models and schemas
   - `utils/`: Utility functions and middleware
   - `services/`: Business logic and external service integrations
   - `migrations/`: Database migration scripts

2. **Frontend (React)**
   - `public/`: Static assets
   - `src/`: React components and application logic
   - `package.json`: Frontend dependencies and scripts

3. **Docker**
   - `docker-compose.yml`: Multi-container Docker configuration
   - `docker/`: Docker-related configuration files
   - `Dockerfile`: Container build instructions for each service

---

## API Endpoints

### **1. Coaches' Actions**
- `/add_program` - Create a new workout program.
- `/edit_program` - Edit program details.
- `/view_athletes` - View athletes' profiles and performances.

### **2. Athletes' Actions**
- `/view_program/<athlete_id>` - View assigned program.
- `/submit_session_data` - Log performance metrics.
- `/record_video` - Upload exercise videos.

### **3. Data Sync**
- `/sync_data` - Sync athlete-entered data and videos.

---

## To-Do List
### **Immediate**
- [ ] Define database schemas for program and athlete tracking.
- [ ] Set up Flask API endpoints.
- [ ] Integrate MediaPipe Pose with video recording.
- [ ] Establish data flow between external and internal databases.

### **Short-Term**
- [ ] Develop frontend athlete and coach dashboards.
- [ ] Implement real-time feedback for athletes during workouts.
- [ ] Configure Docker for backend and database.

### **Long-Term**
- [ ] Optimize video storage and processing.
- [ ] Incorporate AI for advanced analytics and feedback.
- [ ] Scale application for global users.

---

## Questions for Feedback
1. How can we optimize MediaPipe Pose integration for real-time use?
2. What are the best practices for syncing large video files to the backend?
3. How can we streamline athlete-coach interactions for better user experience?
4. Any suggestions for secure and scalable deployment?

## CORS Configuration and Security

### Global CORS Setup
- **Allowed Origins**: http://localhost:3000 (Frontend)
- **Methods**: GET, POST, PUT, DELETE, PATCH, OPTIONS
- **Headers**: Content-Type, Authorization
- **Credentials**: Enabled
- **Max Age**: 3600 seconds

### Implementation Details

1. **Flask App Configuration**
```python
CORS(app, 
    origins=["http://localhost:3000"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    supports_credentials=True,
    max_age=3600
)
```

## Database Schema

### Custom Types and Enums

#### 1. user_role
An enum type defining the possible roles in the system
- `coach`: User who can create and manage workout programs
- `athlete`: User who follows assigned programs and logs performance

#### 2. exercise_type
An enum type categorizing different types of exercises
- `strength`: Weight-based resistance training exercises
- `cardio`: Cardiovascular endurance exercises
- `flexibility`: Stretching and mobility exercises
- `other`: Miscellaneous exercise types

#### 3. set_type
An enum type defining different types of exercise sets
- `working`: Main working sets of the exercise
- `warmup`: Preparatory sets with lighter weights
- `dropset`: Sets performed immediately after working sets with reduced weight
- `backoff`: Sets with reduced weight for volume

### Tables and Relationships

#### 1. Users
Core user management table storing both coaches and athletes
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,                    -- Unique identifier for the user
    email VARCHAR(255) UNIQUE NOT NULL,        -- User's email address, used for authentication
    password_hash VARCHAR(255) NOT NULL,       -- Securely hashed password
    role user_role NOT NULL,                   -- User type: either 'coach' or 'athlete'
    first_name VARCHAR(100),                   -- User's first name
    last_name VARCHAR(100),                    -- User's last name
    created_at TIMESTAMPTZ DEFAULT NOW(),      -- Account creation timestamp
    updated_at TIMESTAMPTZ DEFAULT NOW()       -- Last modification timestamp
);
```

#### 2. Programs
Workout programs created by coaches
```sql
CREATE TABLE programs (
    id INTEGER PRIMARY KEY,                    -- Unique identifier for the program
    coach_id INTEGER NOT NULL,                 -- Reference to the coach who created the program
    name VARCHAR(255) NOT NULL,                -- Program name
    description TEXT,                          -- Detailed program description
    created_at TIMESTAMPTZ DEFAULT NOW(),      -- Program creation timestamp
    updated_at TIMESTAMPTZ DEFAULT NOW(),      -- Last modification timestamp
    FOREIGN KEY (coach_id) REFERENCES users(id)
);
```

#### 3. Athlete_Programs
Junction table linking athletes to their assigned programs
```sql
CREATE TABLE athlete_programs (
    id INTEGER PRIMARY KEY,                    -- Unique identifier for the assignment
    athlete_id INTEGER NOT NULL,               -- Reference to the athlete
    program_id INTEGER NOT NULL,               -- Reference to the assigned program
    start_date DATE NOT NULL,                  -- Program start date
    end_date DATE,                            -- Optional program end date
    status VARCHAR(50),                        -- Program status (active, completed, paused)
    created_at TIMESTAMPTZ DEFAULT NOW(),      -- Assignment creation timestamp
    updated_at TIMESTAMPTZ DEFAULT NOW(),      -- Last modification timestamp
    FOREIGN KEY (athlete_id) REFERENCES users(id),
    FOREIGN KEY (program_id) REFERENCES programs(id)
);
```

#### 4. Workouts
Individual workout sessions within a program
```sql
CREATE TABLE workouts (
    id INTEGER PRIMARY KEY,                    -- Unique identifier for the workout
    program_id INTEGER,                        -- Reference to the parent program
    name VARCHAR(255) NOT NULL,                -- Workout name
    description TEXT,                          -- Detailed workout description
    day_number INTEGER,                        -- Day number within the program
    notes TEXT,                               -- Additional workout notes
    created_at TIMESTAMPTZ DEFAULT NOW(),      -- Workout creation timestamp
    updated_at TIMESTAMPTZ DEFAULT NOW(),      -- Last modification timestamp
    FOREIGN KEY (program_id) REFERENCES programs(id)
);
```

#### 5. Exercises
Master list of available exercises
```sql
CREATE TABLE exercises (
    id INTEGER PRIMARY KEY,                    -- Unique identifier for the exercise
    name VARCHAR(255) NOT NULL,                -- Exercise name
    type exercise_type NOT NULL,               -- Exercise category
    description TEXT,                          -- Exercise description and instructions
    video_url VARCHAR(255),                    -- Reference video demonstration URL
    created_at TIMESTAMPTZ DEFAULT NOW(),      -- Exercise creation timestamp
    updated_at TIMESTAMPTZ DEFAULT NOW()       -- Last modification timestamp
);
```

#### 6. Workout_Exercises
Exercises assigned to specific workouts with their parameters
```sql
CREATE TABLE workout_exercises (
    id INTEGER PRIMARY KEY,                    -- Unique identifier for the workout exercise
    workout_id INTEGER NOT NULL,               -- Reference to the parent workout
    exercise_id INTEGER NOT NULL,              -- Reference to the exercise
    sets INTEGER NOT NULL,                     -- Number of sets to perform
    reps INTEGER,                             -- Number of repetitions per set
    set_type set_type DEFAULT 'working',       -- Type of set (working, warmup, etc.)
    rest_time INTEGER,                         -- Rest time between sets in seconds
    notes TEXT,                               -- Additional exercise notes
    order_index INTEGER DEFAULT 0,             -- Order within the workout
    weight DOUBLE PRECISION,                   -- Prescribed weight in kg/lbs
    created_at TIMESTAMPTZ DEFAULT NOW(),      -- Creation timestamp
    updated_at TIMESTAMPTZ DEFAULT NOW(),      -- Last modification timestamp
    FOREIGN KEY (workout_id) REFERENCES workouts(id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);
```

#### 7. Performance_Logs
Actual performance data logged by athletes
```sql
CREATE TABLE performance_logs (
    id INTEGER PRIMARY KEY,                    -- Unique identifier for the performance log
    athlete_id INTEGER NOT NULL,               -- Reference to the athlete
    workout_exercise_id INTEGER NOT NULL,      -- Reference to the prescribed exercise
    weight DECIMAL(10,2),                      -- Actual weight used
    reps INTEGER,                             -- Actual reps performed
    set_number INTEGER NOT NULL,               -- Set number within the exercise
    notes TEXT,                               -- Performance notes or feedback
    logged_at TIMESTAMPTZ DEFAULT NOW(),       -- When the set was performed
    created_at TIMESTAMPTZ DEFAULT NOW(),      -- Log creation timestamp
    updated_at TIMESTAMPTZ DEFAULT NOW(),      -- Last modification timestamp
    FOREIGN KEY (athlete_id) REFERENCES users(id),
    FOREIGN KEY (workout_exercise_id) REFERENCES workout_exercises(id)
);
```

#### 8. Form_Analyses
Video analysis and feedback for exercise form
```sql
CREATE TABLE form_analyses (
    id INTEGER PRIMARY KEY,                    -- Unique identifier for the form analysis
    athlete_id INTEGER NOT NULL,               -- Reference to the athlete
    exercise_id INTEGER NOT NULL,              -- Reference to the exercise
    video_url VARCHAR(255) NOT NULL,           -- URL to the recorded exercise video
    analysis_data JSON,                        -- MediaPipe Pose analysis results
    feedback TEXT,                            -- Coach or automated feedback
    analyzed_at TIMESTAMPTZ,                   -- When the analysis was performed
    created_at TIMESTAMPTZ DEFAULT NOW(),      -- Analysis creation timestamp
    updated_at TIMESTAMPTZ DEFAULT NOW(),      -- Last modification timestamp
    FOREIGN KEY (athlete_id) REFERENCES users(id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);
```

### Key Constraints and Indexes

#### Unique Constraints
- `users.email`: Ensures unique email addresses for authentication
- `athlete_programs(athlete_id, program_id)`: Prevents duplicate program assignments
- `workout_exercises(workout_id, order_index)`: Maintains exercise order within workouts

#### Foreign Key Relationships
- `programs → users (coach_id)`: Links programs to their creators
- `athlete_programs → users (athlete_id)`: Links program assignments to athletes
- `athlete_programs → programs (program_id)`: Links assignments to programs
- `workouts → programs (program_id)`: Organizes workouts within programs
- `workout_exercises → workouts (workout_id)`: Places exercises in workouts
- `workout_exercises → exercises (exercise_id)`: References exercise definitions
- `performance_logs → users (athlete_id)`: Tracks athlete performance
- `performance_logs → workout_exercises (workout_exercise_id)`: Links performance to prescribed exercises
- `form_analyses → users (athlete_id)`: Links form analysis to athletes
- `form_analyses → exercises (exercise_id)`: Associates analysis with specific exercises

#### Performance Indexes
- `users(email)`: Optimizes user lookup by email
- `programs(coach_id)`: Speeds up coach's program listing
- `athlete_programs(athlete_id, program_id)`: Optimizes program assignment queries
- `workouts(program_id)`: Improves workout listing within programs
- `workout_exercises(workout_id, order_index)`: Optimizes ordered exercise retrieval
- `performance_logs(athlete_id, workout_exercise_id)`: Speeds up performance history queries
- `form_analyses(athlete_id, exercise_id)`: Optimizes form analysis retrieval