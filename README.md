# EmotiSense

## Developers & Collaborators
| Full Name | Student ID | GitHub | Email |
|--|--|--|--|
| Erkam Yildirim | 160235206 | emyildirim | eyildirim1@myseneca.ca |
| Abdulmuhsin Baksh | | | |
| Ahmed Hafiz Shaikh | 127566222 | ahshaikh4 | ahshaikh4@myseneca.ca |


## Project Description

EmotiSense is an AI-powered tool that analyzes nonverbal communication from video input to provide feedback on emotional expression, tone, and body language. It helps users understand how they are perceived in conversations, interviews, and presentations.

## Core Capabilities

The tool provides several key analysis features:

-   **Facial Expression Analysis:** Detects emotions (happy, sad, neutral, etc.) from video frames using DeepFace.
    
-   **Voice Tone Analysis:** Analyzes pitch, energy, speaking pace, and tone variation from audio using Librosa.
    
-   **Natural Language Feedback:** Generates actionable insights and recommendations by combining facial and tonal analysis.
    
-   **Privacy First:** All processing happens locally on the user's machine, and no video data is stored.
    
-   **Interactive Dashboard:** A simple web interface for uploading videos and viewing the results.
    

## Tech Stack

### Database

Our application is privacy-first and does not use a database. All video processing is done locally and is session-based; no user data is stored.

### Development

We are developing this application using **Python** for the backend logic and **Flask** as the web framework. The frontend interface is built using standard **HTML5**, **CSS3**, and **JavaScript**.

## Key Libraries & Tools
    
-   **AI Backend:** TensorFlow
    
-   **Video/Audio Processing:** DeepFace, Librosa, OpenCV
    
-   **Web Framework:** Flask
