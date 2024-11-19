-- Enable the TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create enum types
CREATE TYPE user_role AS ENUM ('coach', 'athlete');
CREATE TYPE exercise_type AS ENUM ('strength', 'cardio', 'flexibility', 'other');
CREATE TYPE set_type AS ENUM ('warmup', 'working', 'dropset', 'failure');

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create programs table
CREATE TABLE programs (
    id SERIAL PRIMARY KEY,
    coach_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create exercises table
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type exercise_type NOT NULL,
    description TEXT,
    video_url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create workouts table
CREATE TABLE workouts (
    id SERIAL PRIMARY KEY,
    program_id INTEGER REFERENCES programs(id),
    name VARCHAR(255) NOT NULL,
    day_number INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create workout_exercises table (junction table between workouts and exercises)
CREATE TABLE workout_exercises (
    id SERIAL PRIMARY KEY,
    workout_id INTEGER REFERENCES workouts(id),
    exercise_id INTEGER REFERENCES exercises(id),
    sets INTEGER NOT NULL,
    reps INTEGER,
    set_type set_type DEFAULT 'working',
    rest_time INTEGER, -- in seconds
    notes TEXT,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create athlete_programs table (junction table for athlete program assignments)
CREATE TABLE athlete_programs (
    id SERIAL PRIMARY KEY,
    athlete_id INTEGER REFERENCES users(id),
    program_id INTEGER REFERENCES programs(id),
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create performance_logs table (hypertable for time-series data)
CREATE TABLE performance_logs (
    id SERIAL,
    athlete_id INTEGER REFERENCES users(id),
    workout_exercise_id INTEGER REFERENCES workout_exercises(id),
    set_number INTEGER NOT NULL,
    weight DECIMAL(10,2),
    reps INTEGER,
    rpe DECIMAL(3,1),
    video_url VARCHAR(255),
    notes TEXT,
    logged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Convert performance_logs to a hypertable
SELECT create_hypertable('performance_logs', 'logged_at');

-- Create indexes for better query performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_programs_coach ON programs(coach_id);
CREATE INDEX idx_workouts_program ON workouts(program_id);
CREATE INDEX idx_workout_exercises_workout ON workout_exercises(workout_id);
CREATE INDEX idx_athlete_programs_athlete ON athlete_programs(athlete_id);
CREATE INDEX idx_athlete_programs_program ON athlete_programs(program_id);
CREATE INDEX idx_performance_logs_athlete ON performance_logs(athlete_id);
CREATE INDEX idx_performance_logs_exercise ON performance_logs(workout_exercise_id);

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_programs_updated_at
    BEFORE UPDATE ON programs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workouts_updated_at
    BEFORE UPDATE ON workouts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_athlete_programs_updated_at
    BEFORE UPDATE ON athlete_programs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
