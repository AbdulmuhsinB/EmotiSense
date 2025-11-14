"""
Facial Expression Analyzer using DeepFace
Analyzes emotions from video frames
"""

import cv2
from deepface import DeepFace
import numpy as np
from collections import Counter


class FacialAnalyzer:
    """Analyzes facial expressions in video using DeepFace"""
    
    def __init__(self):
        """Initialize the facial analyzer"""
        self.emotions = []
        self.frame_count = 0
        
    def analyze_video(self, video_path, frame_skip=5):
        """
        Analyze facial expressions in a video
        
        Args:
            video_path: Path to the video file
            frame_skip: Process every nth frame (default: 5 for performance)
            
        Returns:
            Dictionary containing emotion analysis results
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise Exception("Could not open video file")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        frame_idx = 0
        emotions_detected = []
        
        print(f"Processing video: {total_frames} frames at {fps:.2f} fps")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Skip frames for performance
            if frame_idx % frame_skip != 0:
                frame_idx += 1
                continue
            
            try:
                # Analyze frame for emotions
                result = DeepFace.analyze(
                    frame,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='opencv',
                    silent=True
                )
                
                # Handle both single face and multiple faces
                if isinstance(result, list):
                    result = result[0]
                
                dominant_emotion = result['dominant_emotion']
                emotion_scores = result['emotion']
                
                emotions_detected.append({
                    'frame': frame_idx,
                    'timestamp': frame_idx / fps,
                    'emotion': dominant_emotion,
                    'scores': emotion_scores
                })
                
                if frame_idx % 30 == 0:  # Progress update
                    print(f"Processed frame {frame_idx}/{total_frames}")
                
            except Exception as e:
                # No face detected or other error - skip frame
                pass
            
            frame_idx += 1
        
        cap.release()
        
        if not emotions_detected:
            return {
                'error': 'No faces detected in video',
                'duration': duration,
                'frames_analyzed': 0
            }
        
        # Calculate statistics
        emotion_counts = Counter([e['emotion'] for e in emotions_detected])
        total_detections = len(emotions_detected)
        
        emotion_percentages = {
            emotion: (count / total_detections) * 100
            for emotion, count in emotion_counts.items()
        }
        
        # Calculate average emotion scores
        avg_scores = self._calculate_average_scores(emotions_detected)
        
        # Determine dominant emotion
        dominant_emotion = emotion_counts.most_common(1)[0][0]
        
        # Emotion timeline (simplified)
        timeline = self._create_timeline(emotions_detected, duration)
        
        return {
            'duration': round(duration, 2),
            'frames_analyzed': len(emotions_detected),
            'total_frames': total_frames,
            'dominant_emotion': dominant_emotion,
            'emotion_percentages': emotion_percentages,
            'average_scores': avg_scores,
            'timeline': timeline,
            'emotions_detected': emotions_detected
        }
    
    def _calculate_average_scores(self, emotions_detected):
        """Calculate average scores for each emotion"""
        emotion_keys = emotions_detected[0]['scores'].keys()
        avg_scores = {}
        
        for emotion in emotion_keys:
            scores = [e['scores'][emotion] for e in emotions_detected]
            avg_scores[emotion] = round(np.mean(scores), 2)
        
        return avg_scores
    
    def _create_timeline(self, emotions_detected, duration, num_segments=10):
        """Create a simplified emotion timeline"""
        if not emotions_detected:
            return []
        
        segment_duration = duration / num_segments
        timeline = []
        
        for i in range(num_segments):
            segment_start = i * segment_duration
            segment_end = (i + 1) * segment_duration
            
            # Get emotions in this segment
            segment_emotions = [
                e['emotion'] for e in emotions_detected
                if segment_start <= e['timestamp'] < segment_end
            ]
            
            if segment_emotions:
                dominant = Counter(segment_emotions).most_common(1)[0][0]
            else:
                dominant = 'neutral'
            
            timeline.append({
                'segment': i + 1,
                'start_time': round(segment_start, 2),
                'end_time': round(segment_end, 2),
                'emotion': dominant
            })
        
        return timeline

