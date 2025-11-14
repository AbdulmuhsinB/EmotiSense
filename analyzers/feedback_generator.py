"""
Feedback Generator
Combines facial and voice analysis to generate actionable feedback
"""


class FeedbackGenerator:
    """Generates natural language feedback from analysis results"""
    
    def __init__(self):
        """Initialize feedback generator"""
        self.emotion_insights = {
            'happy': {
                'positive': 'Great! You appeared happy and positive.',
                'tip': 'Maintain this positive energy throughout your communication.'
            },
            'neutral': {
                'positive': 'You maintained a neutral expression.',
                'tip': 'Consider showing more emotional engagement to connect better with your audience.'
            },
            'sad': {
                'positive': 'You showed some sadness or concern.',
                'tip': 'If this is unintentional, practice maintaining a more neutral or positive expression.'
            },
            'angry': {
                'positive': 'You appeared frustrated or intense.',
                'tip': 'Try to relax your facial muscles and maintain a calmer demeanor.'
            },
            'surprise': {
                'positive': 'You showed surprise or interest.',
                'tip': 'This can be engaging, but use it purposefully to emphasize key points.'
            },
            'fear': {
                'positive': 'You appeared nervous or anxious.',
                'tip': 'Practice relaxation techniques before important conversations to appear more confident.'
            },
            'disgust': {
                'positive': 'You showed some negative reaction.',
                'tip': 'Be mindful of facial expressions that might convey unintended negativity.'
            }
        }
    
    def generate_feedback(self, facial_results, voice_results):
        """
        Generate comprehensive feedback from analysis results
        
        Args:
            facial_results: Results from facial analysis
            voice_results: Results from voice analysis
            
        Returns:
            Dictionary containing structured feedback
        """
        feedback = {
            'summary': '',
            'facial_feedback': [],
            'voice_feedback': [],
            'recommendations': [],
            'strengths': [],
            'areas_for_improvement': []
        }
        
        # Handle errors
        has_facial_error = 'error' in facial_results
        has_voice_error = 'error' in voice_results
        
        if has_facial_error and has_voice_error:
            feedback['summary'] = 'Unable to analyze video. Please ensure the video contains visible faces and clear audio.'
            return feedback
        
        # Generate facial feedback
        if not has_facial_error:
            facial_feedback = self._generate_facial_feedback(facial_results)
            feedback['facial_feedback'] = facial_feedback['feedback']
            feedback['strengths'].extend(facial_feedback['strengths'])
            feedback['areas_for_improvement'].extend(facial_feedback['improvements'])
        
        # Generate voice feedback
        if not has_voice_error:
            voice_feedback = self._generate_voice_feedback(voice_results)
            feedback['voice_feedback'] = voice_feedback['feedback']
            feedback['strengths'].extend(voice_feedback['strengths'])
            feedback['areas_for_improvement'].extend(voice_feedback['improvements'])
        
        # Generate overall summary
        feedback['summary'] = self._generate_summary(
            facial_results, voice_results, feedback['strengths'],
            feedback['areas_for_improvement']
        )
        
        # Generate actionable recommendations
        feedback['recommendations'] = self._generate_recommendations(
            facial_results, voice_results
        )
        
        return feedback
    
    def _generate_facial_feedback(self, facial_results):
        """Generate feedback from facial analysis"""
        feedback_items = []
        strengths = []
        improvements = []
        
        dominant_emotion = facial_results.get('dominant_emotion', 'neutral')
        emotion_percentages = facial_results.get('emotion_percentages', {})
        
        # Main emotion feedback
        if dominant_emotion in self.emotion_insights:
            insight = self.emotion_insights[dominant_emotion]
            feedback_items.append({
                'category': 'Dominant Emotion',
                'observation': f"Your dominant emotion was '{dominant_emotion}' ({emotion_percentages.get(dominant_emotion, 0):.1f}% of the time).",
                'insight': insight['positive'],
                'tip': insight['tip']
            })
            
            # Determine if it's a strength or improvement area
            if dominant_emotion in ['happy', 'neutral']:
                strengths.append(f"Maintained {dominant_emotion} expression")
            else:
                improvements.append(f"Work on managing {dominant_emotion} expressions")
        
        # Emotional consistency
        emotion_count = len(emotion_percentages)
        if emotion_count > 5:
            feedback_items.append({
                'category': 'Emotional Consistency',
                'observation': 'Your emotions varied significantly throughout the video.',
                'insight': 'This could indicate natural expressiveness or lack of emotional control.',
                'tip': 'For professional settings, aim for more consistent emotional expression.'
            })
            improvements.append("Practice emotional consistency")
        else:
            strengths.append("Consistent emotional expression")
        
        # Check for positive emotions
        positive_emotions = emotion_percentages.get('happy', 0)
        if positive_emotions > 40:
            strengths.append("Strong positive emotional presence")
        elif positive_emotions < 10:
            improvements.append("Consider showing more positive engagement")
        
        return {
            'feedback': feedback_items,
            'strengths': strengths,
            'improvements': improvements
        }
    
    def _generate_voice_feedback(self, voice_results):
        """Generate feedback from voice analysis"""
        feedback_items = []
        strengths = []
        improvements = []
        
        overall_tone = voice_results.get('overall_tone', '')
        pitch = voice_results.get('pitch', {})
        energy = voice_results.get('energy', {})
        speaking_rate = voice_results.get('speaking_rate', {})
        
        # Overall tone feedback
        feedback_items.append({
            'category': 'Overall Vocal Tone',
            'observation': f"Your vocal tone was {overall_tone}.",
            'insight': 'Vocal tone significantly impacts how your message is received.',
            'tip': 'Continue developing vocal confidence through practice and preparation.'
        })
        
        if 'confident' in overall_tone:
            strengths.append("Confident vocal tone")
        else:
            improvements.append("Build more vocal confidence")
        
        # Pitch feedback
        pitch_interp = pitch.get('interpretation', '')
        if 'monotone' in pitch_interp.lower():
            feedback_items.append({
                'category': 'Pitch Variation',
                'observation': 'Your pitch variation was limited.',
                'insight': 'Monotone delivery can make content less engaging.',
                'tip': 'Practice emphasizing key words and varying your pitch to maintain interest.'
            })
            improvements.append("Increase pitch variation")
        elif 'expressive' in pitch_interp.lower():
            strengths.append("Good pitch variation")
        
        # Energy feedback
        energy_interp = energy.get('interpretation', '')
        if 'confident' in energy_interp.lower():
            strengths.append("Clear and confident vocal energy")
        elif 'soft' in energy_interp.lower() or 'hesitant' in energy_interp.lower():
            improvements.append("Project voice with more energy")
        
        # Speaking rate feedback
        rate_interp = speaking_rate.get('interpretation', '')
        if 'fast' in rate_interp.lower():
            feedback_items.append({
                'category': 'Speaking Rate',
                'observation': 'You spoke at a fast pace.',
                'insight': 'Fast speaking can indicate nervousness or enthusiasm.',
                'tip': 'Slow down and add strategic pauses for emphasis and clarity.'
            })
            improvements.append("Moderate speaking pace")
        elif 'slow' in rate_interp.lower():
            feedback_items.append({
                'category': 'Speaking Rate',
                'observation': 'You spoke at a slower pace.',
                'insight': 'Slow speaking can be deliberate or indicate uncertainty.',
                'tip': 'Ensure your pace matches your message and maintains engagement.'
            })
        else:
            strengths.append("Comfortable speaking pace")
        
        return {
            'feedback': feedback_items,
            'strengths': strengths,
            'improvements': improvements
        }
    
    def _generate_summary(self, facial_results, voice_results, strengths, improvements):
        """Generate overall summary"""
        has_facial = 'error' not in facial_results
        has_voice = 'error' not in voice_results
        
        summary_parts = []
        
        if has_facial:
            dominant_emotion = facial_results.get('dominant_emotion', 'neutral')
            summary_parts.append(f"You appeared {dominant_emotion} throughout most of the video")
        
        if has_voice:
            overall_tone = voice_results.get('overall_tone', '')
            summary_parts.append(f"your vocal tone was {overall_tone}")
        
        if len(strengths) > len(improvements):
            conclusion = "Overall, you demonstrated strong communication skills with a few areas for refinement."
        elif len(improvements) > len(strengths):
            conclusion = "There are several areas where you can improve your nonverbal communication for greater impact."
        else:
            conclusion = "You showed balanced nonverbal communication with both strengths and opportunities for growth."
        
        if summary_parts:
            return f"{'. '.join(summary_parts).capitalize()}. {conclusion}"
        else:
            return conclusion
    
    def _generate_recommendations(self, facial_results, voice_results):
        """Generate actionable recommendations"""
        recommendations = []
        
        has_facial = 'error' not in facial_results
        has_voice = 'error' not in voice_results
        
        if has_facial:
            dominant_emotion = facial_results.get('dominant_emotion', 'neutral')
            
            if dominant_emotion in ['fear', 'sad', 'angry']:
                recommendations.append({
                    'title': 'Practice Relaxation Techniques',
                    'description': 'Before important conversations, take deep breaths and practice positive visualization to appear more calm and confident.'
                })
            
            emotion_percentages = facial_results.get('emotion_percentages', {})
            positive_ratio = emotion_percentages.get('happy', 0)
            
            if positive_ratio < 20:
                recommendations.append({
                    'title': 'Increase Positive Expressions',
                    'description': 'Smile more naturally and show genuine interest. This makes you more approachable and engaging.'
                })
        
        if has_voice:
            pitch = voice_results.get('pitch', {})
            
            if 'monotone' in pitch.get('interpretation', '').lower():
                recommendations.append({
                    'title': 'Vary Your Pitch',
                    'description': 'Practice reading aloud with exaggerated emphasis. Gradually incorporate natural variation into your speaking.'
                })
            
            energy = voice_results.get('energy', {})
            if 'soft' in energy.get('interpretation', '').lower():
                recommendations.append({
                    'title': 'Project Your Voice',
                    'description': 'Speak from your diaphragm, not your throat. Practice projecting your voice to fill the room confidently.'
                })
        
        # Always add a general recommendation
        recommendations.append({
            'title': 'Record and Review',
            'description': 'Regularly record yourself in practice sessions and review your nonverbal communication. Self-awareness is key to improvement.'
        })
        
        recommendations.append({
            'title': 'Practice with Feedback',
            'description': 'Present to friends or colleagues and ask for honest feedback about your body language and tone.'
        })
        
        return recommendations

