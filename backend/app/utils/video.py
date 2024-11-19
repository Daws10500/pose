import os
import cv2
import numpy as np
import mediapipe as mp
from flask import current_app
from app.models import FormAnalysis
from celery import shared_task
import json
from datetime import datetime

def save_uploaded_video(file, filename):
    """Save an uploaded video file to the configured upload directory."""
    upload_dir = current_app.config['VIDEO_UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create date-based subdirectory
    date_dir = os.path.join(upload_dir, datetime.now().strftime('%Y/%m/%d'))
    os.makedirs(date_dir, exist_ok=True)
    
    # Save file
    filepath = os.path.join(date_dir, filename)
    file.save(filepath)
    
    return filepath

@shared_task
def process_video_form(analysis_id):
    """Process a video for form analysis using MediaPipe Pose."""
    analysis = FormAnalysis.query.get(analysis_id)
    if not analysis:
        return
    
    try:
        # Initialize MediaPipe Pose
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=current_app.config.get('MEDIAPIPE_MODEL_COMPLEXITY', 2),
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Open video file
        cap = cv2.VideoCapture(analysis.video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Initialize results storage
        pose_landmarks = []
        frame_scores = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame
            results = pose.process(frame_rgb)
            
            if results.pose_landmarks:
                # Store landmarks
                frame_landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    frame_landmarks.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    })
                pose_landmarks.append(frame_landmarks)
                
                # Calculate form score for frame
                frame_score = calculate_form_score(frame_landmarks, analysis.exercise_id)
                frame_scores.append(frame_score)
        
        cap.release()
        pose.close()
        
        # Calculate overall metrics
        avg_score = np.mean(frame_scores) if frame_scores else 0
        consistency = np.std(frame_scores) if frame_scores else 0
        
        # Save analysis results
        analysis.status = 'completed'
        analysis.form_score = float(avg_score)
        analysis.consistency_score = float(consistency)
        analysis.pose_data = json.dumps({
            'landmarks': pose_landmarks,
            'frame_scores': frame_scores,
            'metadata': {
                'frame_count': frame_count,
                'fps': fps
            }
        })
        analysis.save()
        
    except Exception as e:
        analysis.status = 'failed'
        analysis.error_message = str(e)
        analysis.save()

def calculate_form_score(landmarks, exercise_id):
    """Calculate a form score for a single frame based on exercise-specific criteria."""
    # This is a simplified scoring system - in practice, you would have
    # exercise-specific criteria and more sophisticated scoring algorithms
    
    # Example: Check if key joints are in expected positions
    score = 1.0
    
    # Get key joint positions
    hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]
    knee = landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE]
    ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE]
    
    # Example: Check knee alignment for squats
    if exercise_id == 1:  # Assuming 1 is squat
        # Calculate knee angle
        knee_angle = calculate_angle(hip, knee, ankle)
        
        # Penalize if knee angle is outside expected range
        if knee_angle < 60 or knee_angle > 100:
            score *= 0.8
    
    return score

def calculate_angle(p1, p2, p3):
    """Calculate the angle between three points."""
    # Convert landmarks to numpy arrays
    a = np.array([p1['x'], p1['y']])
    b = np.array([p2['x'], p2['y']])
    c = np.array([p3['x'], p3['y']])
    
    # Calculate vectors
    ba = a - b
    bc = c - b
    
    # Calculate angle
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    
    return np.degrees(angle)
