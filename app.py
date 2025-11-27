"""
EmotiSense, AI-powered communication analyzer
Main Flask App
"""

import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import tempfile
import numpy as np

from analyzers.facial_analyzer import FacialAnalyzer
from analyzers.voice_analyzer import VoiceAnalyzer
from analyzers.feedback_generator import FeedbackGenerator

app = Flask(__name__)

# configurations
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

def allowed_file(filename):
    """check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4'}


def convert_to_json_serializable(obj):
    """
    convert NumPy types to native types for JSON serialization
    """
    if isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_video():
    """
    Analyze uploaded video for facial expressions and voice tone
    Return JSON with analysis and feedback results
    """
    try:
        # check if file was uploaded
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided!'}), 400
        
        file = request.files['video']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected!'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only MP4 files are allowed!'}), 400
        
        # save uploaded file temporarily
        # we cannot run analysis directly on the raw upload stream so,
        # the we save the uploaded video into a temporary directory, use it then delete it.
        filename = secure_filename(file.filename)
        temp_video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_video_path)
        
        try:
            # initialize analyzers
            facial_analyzer = FacialAnalyzer()
            voice_analyzer = VoiceAnalyzer()
            feedback_generator = FeedbackGenerator()
            
            # perform facial analysis
            print("starting facial analysis...")
            facial_results = facial_analyzer.analyze_video(temp_video_path)
            
            # perform voice analysis
            print("starting voice analysis...")
            voice_results = voice_analyzer.analyze_video(temp_video_path)
            
            # generate feedback
            print("generating feedback...")
            feedback = feedback_generator.generate_feedback(facial_results, voice_results)
            
            # combine all results
            results = {
                'facial_analysis': facial_results,
                'voice_analysis': voice_results,
                'feedback': feedback,
                'success': True
            }
            
            # convert NumPy types to JSON-serializable types
            results = convert_to_json_serializable(results)
            
            return jsonify(results)
            
        finally:
            # clean up temporary file
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
                print(f"Cleaned up temporary file: {temp_video_path}")
    
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return jsonify({
            'error': f'Analysis failed: {str(e)}',
            'success': False
        }), 500


@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'EmotiSense'})


if __name__ == '__main__':
    print("=" * 50)
    print("EmotiSense - AI Nonverbal Communication Analyzer")
    print("=" * 50)
    print("Starting Flask server...")
    print("Navigate to http://localhost:8080 in your browser")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=8080)