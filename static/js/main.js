// EmotiSense Main JavaScript

let selectedFile = null;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const videoInput = document.getElementById('videoInput');
const selectedFileDiv = document.getElementById('selectedFile');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFile');
const analyzeButton = document.getElementById('analyzeButton');

const uploadSection = document.getElementById('uploadSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

const newAnalysisButton = document.getElementById('newAnalysisButton');
const retryButton = document.getElementById('retryButton');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // File input change
    videoInput.addEventListener('change', handleFileSelect);
    
    // Upload button
    const uploadButton = document.getElementById('uploadButton');
    uploadButton.addEventListener('click', (e) => {
        e.stopPropagation();
        videoInput.click();
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Remove file
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearSelectedFile();
    });
    
    // Analyze button
    analyzeButton.addEventListener('click', analyzeVideo);
    
    // New analysis button
    newAnalysisButton.addEventListener('click', resetToUpload);
    
    // Retry button
    retryButton.addEventListener('click', resetToUpload);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        validateAndSetFile(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const file = e.dataTransfer.files[0];
    if (file) {
        validateAndSetFile(file);
    }
}

function validateAndSetFile(file) {
    // Check file type
    if (!file.type.includes('mp4') && !file.name.toLowerCase().endsWith('.mp4')) {
        alert('Please upload an MP4 video file');
        videoInput.value = ''; // Clear the input
        return;
    }
    
    // Check file size (100MB)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('File size exceeds 100MB limit');
        videoInput.value = ''; // Clear the input
        return;
    }
    
    selectedFile = file;
    fileName.textContent = file.name;
    selectedFileDiv.style.display = 'block';
    analyzeButton.disabled = false;
}

function clearSelectedFile() {
    selectedFile = null;
    videoInput.value = '';
    selectedFileDiv.style.display = 'none';
    analyzeButton.disabled = true;
}

async function analyzeVideo() {
    if (!selectedFile) return;
    
    // Show loading screen
    showSection('loading');
    
    // Start progress simulation
    startProgressSimulation();
    
    // Create form data
    const formData = new FormData();
    formData.append('video', selectedFile);
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Stop the progress simulation
            if (progressInterval) {
                clearInterval(progressInterval);
            }
            
            // Complete progress to 100%
            updateProgress(100, 'Complete!');
            updateStepStatus('step3', 'completed');
            
            // Wait to show 100% before displaying results
            setTimeout(() => displayResults(data), 1000);
        } else {
            if (progressInterval) {
                clearInterval(progressInterval);
            }
            showError(data.error || 'Analysis failed');
        }
    } catch (error) {
        console.error('Error:', error);
        if (progressInterval) {
            clearInterval(progressInterval);
        }
        showError('Network error. Please try again.');
    }
}

let progressInterval = null;
let currentProgress = 0;

function startProgressSimulation() {
    currentProgress = 0;
    updateProgress(0, 'Starting analysis...');
    
    // Clear any existing interval
    if (progressInterval) {
        clearInterval(progressInterval);
    }
    
    // Simulate progress
    progressInterval = setInterval(() => {
        if (currentProgress < 30) {
            // Fast initial progress (uploading)
            currentProgress += 2;
            updateProgress(currentProgress, 'Uploading video...');
        } else if (currentProgress < 60) {
            // Facial analysis phase (slower)
            currentProgress += 0.5;
            updateProgress(currentProgress, 'Analyzing facial expressions...');
            updateStepStatus('step1', 'in-progress');
        } else if (currentProgress < 85) {
            // Voice analysis phase
            currentProgress += 0.8;
            updateProgress(currentProgress, 'Analyzing voice tone...');
            updateStepStatus('step1', 'completed');
            updateStepStatus('step2', 'in-progress');
        } else if (currentProgress < 95) {
            // Generating feedback
            currentProgress += 0.3;
            updateProgress(currentProgress, 'Generating feedback...');
            updateStepStatus('step2', 'completed');
            updateStepStatus('step3', 'in-progress');
        }
        
        // Stop at 95% and wait for actual completion
        if (currentProgress >= 95) {
            clearInterval(progressInterval);
            updateProgress(95, 'Finalizing results...');
        }
    }, 100);
}

function updateProgress(percent, message) {
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    const loadingText = document.getElementById('loadingText');
    
    if (progressBar) progressBar.style.width = percent + '%';
    if (progressPercent) progressPercent.textContent = Math.round(percent) + '%';
    if (loadingText) loadingText.textContent = message;
}

function updateStepStatus(stepId, status) {
    const step = document.getElementById(stepId);
    if (!step) return;
    
    const icon = step.querySelector('.step-icon');
    if (!icon) return;
    
    if (status === 'in-progress') {
        step.classList.add('in-progress');
        icon.textContent = '⏳';
    } else if (status === 'completed') {
        step.classList.remove('in-progress');
        step.classList.add('completed');
        icon.textContent = '✅';
    }
}

function displayResults(data) {
    const { facial_analysis, voice_analysis, feedback } = data;
    
    // Display summary
    document.getElementById('summaryText').textContent = feedback.summary;
    
    // Display facial results
    displayFacialResults(facial_analysis);
    
    // Display voice results
    displayVoiceResults(voice_analysis);
    
    // Display strengths
    displayList('strengthsList', feedback.strengths);
    
    // Display improvements
    displayList('improvementsList', feedback.areas_for_improvement);
    
    // Display detailed feedback in summary card
    displayDetailedFeedbackInSummary(feedback.facial_feedback, feedback.voice_feedback);
    
    // Display recommendations
    displayRecommendations(feedback.recommendations);
    
    // Display emotion timeline (now under summary)
    if (facial_analysis.timeline) {
        displayTimeline(facial_analysis.timeline);
    }
    
    // Show results section
    showSection('results');
}

function displayFacialResults(facial) {
    const container = document.getElementById('facialResults');
    
    if (facial.error) {
        container.innerHTML = `<p class="error-message">${facial.error}</p>`;
        return;
    }
    
    let html = '';
    
    // Dominant emotion
    html += `
        <div class="metric">
            <span class="metric-label">Dominant Emotion</span>
            <span class="metric-value" style="text-transform: capitalize; font-size: 1.2rem; font-weight: bold; color: var(--primary-color);">
                ${facial.dominant_emotion}
            </span>
        </div>
    `;
    
    // Emotion percentages
    html += '<div class="metric"><span class="metric-label">Emotion Distribution</span>';
    
    for (const [emotion, percentage] of Object.entries(facial.emotion_percentages)) {
        html += `
            <div class="emotion-bar">
                <span class="emotion-label">${emotion}</span>
                <div class="emotion-progress">
                    <div class="emotion-fill" style="width: ${percentage}%"></div>
                </div>
                <span class="emotion-percentage">${percentage.toFixed(1)}%</span>
            </div>
        `;
    }
    
    html += '</div>';
    
    // Analysis stats
    html += `
        <div class="metric">
            <span class="metric-label">Analysis Details</span>
            <span class="metric-value">
                Analyzed ${facial.frames_analyzed} frames out of ${facial.total_frames} total frames
                (${facial.duration} seconds)
            </span>
        </div>
    `;
    
    container.innerHTML = html;
}

function displayVoiceResults(voice) {
    const container = document.getElementById('voiceResults');
    
    if (voice.error || !voice.has_audio) {
        container.innerHTML = `<p class="error-message">${voice.error || 'No audio detected'}</p>`;
        return;
    }
    
    let html = '';
    
    // Overall tone
    html += `
        <div class="metric">
            <span class="metric-label">Overall Tone</span>
            <span class="metric-value" style="text-transform: capitalize; font-size: 1.1rem; font-weight: bold; color: var(--primary-color);">
                ${voice.overall_tone}
            </span>
        </div>
    `;
    
    // Pitch
    html += `
        <div class="metric">
            <span class="metric-label">Pitch Analysis</span>
            <span class="metric-value">
                Average: ${voice.pitch.average} Hz<br>
                ${voice.pitch.interpretation}
            </span>
        </div>
    `;
    
    // Energy
    html += `
        <div class="metric">
            <span class="metric-label">Vocal Energy</span>
            <span class="metric-value">
                ${voice.energy.interpretation}
            </span>
        </div>
    `;
    
    // Speaking rate
    html += `
        <div class="metric">
            <span class="metric-label">Speaking Rate</span>
            <span class="metric-value">
                ${voice.speaking_rate.interpretation}
            </span>
        </div>
    `;
    
    // Duration
    html += `
        <div class="metric">
            <span class="metric-label">Duration</span>
            <span class="metric-value">${voice.duration} seconds</span>
        </div>
    `;
    
    container.innerHTML = html;
}

function displayList(elementId, items) {
    const container = document.getElementById(elementId);
    
    if (!items || items.length === 0) {
        container.innerHTML = '<li>None identified</li>';
        return;
    }
    
    container.innerHTML = items.map(item => `<li>${item}</li>`).join('');
}

function displayDetailedFeedbackInSummary(facialFeedback, voiceFeedback) {
    const container = document.getElementById('summaryDetailedFeedback');
    
    const allFeedback = [...facialFeedback, ...voiceFeedback];
    
    if (allFeedback.length === 0) {
        return;
    }
    
    let html = '<div class="summary-feedback-items">';
    
    for (const item of allFeedback) {
        html += `
            <div class="summary-feedback-item">
                <div class="summary-feedback-category">📌 ${item.category}</div>
                <div class="summary-feedback-tip">${item.tip}</div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsList');
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p>No recommendations available</p>';
        return;
    }
    
    let html = '';
    
    for (const rec of recommendations) {
        html += `
            <div class="recommendation-item">
                <div class="recommendation-title">${rec.title}</div>
                <div class="recommendation-description">${rec.description}</div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function displayTimeline(timeline) {
    const container = document.getElementById('emotionTimeline');
    
    if (!timeline || timeline.length === 0) {
        container.innerHTML = '<p>No timeline data available</p>';
        return;
    }
    
    let html = '<div class="timeline">';
    
    for (const segment of timeline) {
        html += `
            <div class="timeline-segment ${segment.emotion}" 
                 title="${segment.emotion} (${segment.start_time}s - ${segment.end_time}s)">
                <div>${segment.emotion}</div>
                <small>${segment.start_time}s</small>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function showSection(section) {
    uploadSection.style.display = 'none';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    if (section === 'upload') {
        uploadSection.style.display = 'block';
    } else if (section === 'loading') {
        loadingSection.style.display = 'flex';
    } else if (section === 'results') {
        resultsSection.style.display = 'block';
    } else if (section === 'error') {
        errorSection.style.display = 'flex';
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    showSection('error');
}

function resetToUpload() {
    clearSelectedFile();
    showSection('upload');
}

