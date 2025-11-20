"""
Analyze Voice Tone using Librosa
and identify tone, confidence, and emotional state from audio
"""

import librosa
import numpy as np
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    # if moviepy 2.x is used
    from moviepy import VideoFileClip
import tempfile
import os


class VoiceAnalyzer:
    """Analyzes voice characteristics from audio"""
    
    def __init__(self):
        """Initialize the voice analyzer"""
        self.sample_rate = 22050
        
    def analyze_video(self, video_path):
        """Extract audio from video and analyze voice characteristics
        Arguments: video_path: path to the video file
        Return: dictionary with voice analysis results
        """
        # create a temporary audio file with .wav extension
        temp_audio_path = tempfile.mktemp(suffix='.wav')
        try:
            # extract audio using moviepy
            video = VideoFileClip(video_path) # open the video file
            if video.audio is None:
                return {
                    'error': 'No audio track found in video',
                    'has_audio': False
                }
            
            video.audio.write_audiofile( # write the audio to the temporary file
                temp_audio_path,
                codec='pcm_s16le',
                logger=None
            )
            video.close() # close the actual video file
            
            # load audio to librosa
            y, sr = librosa.load(temp_audio_path, sr=self.sample_rate)
            
            # get voice features
            results = self._analyze_audio(y, sr)
            results['has_audio'] = True
            
            return results
            
        finally:
            # clean up temporary audio file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
    
    def _analyze_audio(self, y, sr):
        """Analyze audio features using librosa
        Arguments: y: audio time series, sr: sample rate
        Return: dictionary with audio analysis metrics
        """
        # get duration
        duration = librosa.get_duration(y=y, sr=sr)
        
        # pitch analysis (fundamental frequency)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        
        # get the pitch values
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        # calculate average and standard deviation of pitch values
        avg_pitch = np.mean(pitch_values) if pitch_values else 0
        pitch_std = np.std(pitch_values) if pitch_values else 0
        
        # energy and amplitude analysis
        rms = librosa.feature.rms(y=y)[0]
        avg_energy = np.mean(rms)
        energy_std = np.std(rms)
        
        # speaking rate (zero crossing rate as proxy)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        avg_zcr = np.mean(zcr)
        
        # spectral features and tempo (brightness of sound)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        avg_spectral_centroid = np.mean(spectral_centroids)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # convert features to human language (feedback)
        interpretation = self._interpret_features(
            avg_pitch, pitch_std, avg_energy, energy_std,
            avg_zcr, avg_spectral_centroid, tempo
        )
        
        return {
            'duration': round(duration, 2),
            'pitch': {
                'average': round(float(avg_pitch), 2),
                'variation': round(float(pitch_std), 2),
                'interpretation': interpretation['pitch']
            },
            'energy': {
                'average': round(float(avg_energy), 4),
                'variation': round(float(energy_std), 4),
                'interpretation': interpretation['energy']
            },
            'speaking_rate': {
                'value': round(float(avg_zcr), 4),
                'interpretation': interpretation['speaking_rate']
            },
            'spectral_centroid': {
                'average': round(float(avg_spectral_centroid), 2),
                'interpretation': interpretation['spectral']
            },
            'tempo': round(float(tempo), 2),
            'overall_tone': interpretation['overall']
        }
    
    def _interpret_features(self, pitch, pitch_std, energy, energy_std,
                           zcr, spectral_centroid, tempo):
        """Interpret audio features to provide natural language feedback
        Return: dictionary with interpretations for each feature
        """
        # pitch interpretation
        if pitch > 180:
            pitch_interp = "high (possible excitement or stress)"
        elif pitch > 120:
            pitch_interp = "moderate (neutral to confident)"
        else:
            pitch_interp = "low (calm or possibly monotone)"
        
        if pitch_std > 30:
            pitch_interp += " with high variation (expressive)"
        elif pitch_std < 15:
            pitch_interp += " with low variation (monotone)"
        
        # energy interpretation
        if energy > 0.05:
            energy_interp = "high (confident and clear)"
        elif energy > 0.02:
            energy_interp = "moderate (balanced)"
        else:
            energy_interp = "low (soft or hesitant)"
        
        # speaking rate interpretation
        if zcr > 0.1:
            rate_interp = "fast (energetic or nervous)"
        elif zcr > 0.05:
            rate_interp = "moderate (comfortable pace)"
        else:
            rate_interp = "slow (deliberate or uncertain)"
        
        # spectral interpretation (brightness of sound)
        if spectral_centroid > 3000:
            spectral_interp = "bright (clear articulation)"
        elif spectral_centroid > 2000:
            spectral_interp = "balanced"
        else:
            spectral_interp = "dark (muffled or low resonance)"
        
        # overall tone assessment
        confidence_score = 0
        
        if 120 < pitch < 200:
            confidence_score += 1
        if energy > 0.03:
            confidence_score += 1
        if 0.05 < zcr < 0.1:
            confidence_score += 1
        if pitch_std > 15:
            confidence_score += 1
        
        if confidence_score >= 3:
            overall = "confident and engaging"
        elif confidence_score >= 2:
            overall = "moderate confidence"
        else:
            overall = "room for improvement in vocal presence"
        
        return {
            'pitch': pitch_interp,
            'energy': energy_interp,
            'speaking_rate': rate_interp,
            'spectral': spectral_interp,
            'overall': overall
        }