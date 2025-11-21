"""
Analyze Facial Expressions using DeepFace
and separate emotions from video frames
"""

import cv2
from deepface import DeepFace
import numpy as np
from collections import Counter


class FacialAnalyzer:
    
    def __init__(self):
        """Initialization"""
        self.emotions = []
        self.frame_count = 0
        
    def analyze_video(self, video_path, frame_skip=5):
        """ Analyze vide for emotions from frames
        Arguments: video_path: path to the video file, frame_skip: process every nth frame (default: 5 - performance)
        Return: dictionary with emotion analysis
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise Exception("Could not open the video file!")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0 # duration of the video in seconds
        frame_idx = 0
        emotions_detected = []
        print(f"Processing video: {total_frames} frames at {fps:.2f} fps")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # skip frames for performance (5 frames per second)
            if frame_idx % frame_skip != 0:
                frame_idx += 1
                continue
            try:
                # analyze the frame
                result = DeepFace.analyze(
                    frame,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='opencv',
                    silent=True
                )
                # analyze both single and multiple faces
                if isinstance(result, list):
                    result = result[0]

                dominant_emotion = result['dominant_emotion']
                emotion_scores = result['emotion']
                
                # add the emotion analysis into a list
                emotions_detected.append({
                    'frame': frame_idx,
                    'timestamp': frame_idx / fps,
                    'emotion': dominant_emotion,
                    'scores': emotion_scores
                })
                if frame_idx % 30 == 0:  # update progress bar every 30 frames
                    print(f"Processed frame {frame_idx}/{total_frames}")
                
            except Exception as e:
                # when no face detected or some error happens, skip the frame
                # print(f"Error analyzing frame {frame_idx}: {e}")
                pass
            
            # go to the next frame
            frame_idx += 1
        
        # free resources after the analysis
        # release the video capture object
        cap.release()
        
        #if no faces detected, return an error
        if not emotions_detected:
            return {
                'error': 'No faces detected in video',
                'duration': duration,
                'frames_analyzed': 0
            }
        # calculate statistics
        emotion_counts = Counter([e['emotion'] for e in emotions_detected])
        total_detections = len(emotions_detected)
        #print(f"Total Emotions detected: {emotions_detected}")

        emotion_percentages = {
            emotion: (count / total_detections) * 100
            for emotion, count in emotion_counts.items()
        }
        
        # calculate average, dominant, and timeline for emotions scores
        avg_scores = self._calculate_average_scores(emotions_detected)
        dominant_emotion = emotion_counts.most_common(1)[0][0]
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
        """Calculate average scores of each emotion
        Arguments: emotions_detected: list of emotion analysis
        Return: dictionary with average scores of each emotion
        """

        emotion_keys = emotions_detected[0]['scores'].keys()
        avg_scores = {}
        
        for emotion in emotion_keys:
            scores = [e['scores'][emotion] for e in emotions_detected]
            avg_scores[emotion] = round(np.mean(scores), 2)
        
        return avg_scores
    
    def _create_timeline(self, emotions_detected, duration, num_segments=10):
        """Create a basic emotion timeline
        Arguments: emotions_detected: list of emotion analysis, duration: duration of video (sec), num_segments: number of segments to divide the video into (default: 10)
        Return: list of emotion timeline
        """
        if not emotions_detected:
            return []
        
        segment_duration = duration / num_segments
        timeline = []
        
        for i in range(num_segments):
            segment_start = i * segment_duration
            segment_end = (i + 1) * segment_duration
            segment_emotions = [ # get emotions in this segment
                e['emotion'] for e in emotions_detected
                if segment_start <= e['timestamp'] < segment_end
            ]
            # if emotions detected, get the dominant emotion
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
