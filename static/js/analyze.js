// Video Facial Analysis JavaScript

let selectedFile = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Video Facial Analysis page loaded!');

    // Get DOM elements
    const uploadArea = document.getElementById('uploadArea');
    const videoInput = document.getElementById('videoInput');
    const selectVideoBtn = document.getElementById('selectVideoBtn');
    const videoPreview = document.getElementById('videoPreview');
    const previewVideo = document.getElementById('previewVideo');
    const videoInfo = document.getElementById('videoInfo');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const clearBtn = document.getElementById('clearBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');
    const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');

    // Event Listeners
    selectVideoBtn.addEventListener('click', () => videoInput.click());
    videoInput.addEventListener('change', handleFileSelect);
    analyzeBtn.addEventListener('click', analyzeVideo);
    clearBtn.addEventListener('click', clearVideo);
    analyzeAnotherBtn.addEventListener('click', clearVideo);

    // Drag and drop events
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => videoInput.click());
});

/**
 * Handle file selection from input
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file && file.type.startsWith('video/')) {
        selectedFile = file;
        displayVideoPreview(file);
    } else {
        alert('Please select a valid video file (MP4, AVI, MOV, MKV, WebM).');
    }
}

/**
 * Handle drag over event
 */
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

/**
 * Handle drag leave event
 */
function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag-over');
}

/**
 * Handle drop event
 */
function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('video/')) {
        selectedFile = file;
        displayVideoPreview(file);
    } else {
        alert('Please drop a valid video file (MP4, AVI, MOV, MKV, WebM).');
    }
}

/**
 * Display video preview
 */
function displayVideoPreview(file) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        document.getElementById('previewVideo').src = e.target.result;
        document.getElementById('uploadArea').style.display = 'none';
        document.getElementById('videoPreview').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';
        
        // Display video info
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
        document.getElementById('videoInfo').innerHTML = `
            <p><strong>File:</strong> ${file.name}</p>
            <p><strong>Size:</strong> ${fileSizeMB} MB</p>
            <p><strong>Type:</strong> ${file.type}</p>
        `;
        
        // Get video duration
        const video = document.getElementById('previewVideo');
        video.addEventListener('loadedmetadata', function() {
            const duration = Math.floor(video.duration);
            const minutes = Math.floor(duration / 60);
            const seconds = duration % 60;
            document.getElementById('videoInfo').innerHTML += `
                <p><strong>Duration:</strong> ${minutes}:${seconds.toString().padStart(2, '0')}</p>
            `;
        });
    };
    
    reader.readAsDataURL(file);
}

/**
 * Clear video and reset form
 */
function clearVideo() {
    selectedFile = null;
    document.getElementById('videoInput').value = '';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('videoPreview').style.display = 'none';
    document.getElementById('loadingIndicator').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('previewVideo').src = '';
}

/**
 * Analyze the uploaded video
 */
async function analyzeVideo() {
    if (!selectedFile) {
        alert('Please select a video first.');
        return;
    }

    // Check file size (100MB limit)
    const fileSizeMB = selectedFile.size / (1024 * 1024);
    if (fileSizeMB > 100) {
        alert('File size exceeds 100MB limit. Please upload a smaller video.');
        return;
    }

    // Show loading indicator
    document.getElementById('videoPreview').style.display = 'none';
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';

    // Prepare form data
    const formData = new FormData();
    formData.append('video', selectedFile);

    try {
        const response = await fetch('/api/analyze-video', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Hide loading indicator
        document.getElementById('loadingIndicator').style.display = 'none';

        if (response.ok && data.status === 'success') {
            displayResults(data.analysis);
        } else {
            alert(data.message || 'Analysis failed. Please try again.');
            document.getElementById('videoPreview').style.display = 'block';
        }

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loadingIndicator').style.display = 'none';
        document.getElementById('videoPreview').style.display = 'block';
        alert('Network error. Please check your connection and try again.');
    }
}

/**
 * Display analysis results
 */
function displayResults(analysis) {
    // Display video statistics
    document.getElementById('videoStats').innerHTML = `
        <div class="stat-grid">
            <div class="stat-item">
                <span class="stat-label">Duration:</span>
                <span class="stat-value">${analysis.duration}s</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Total Frames:</span>
                <span class="stat-value">${analysis.total_frames}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Analyzed Frames:</span>
                <span class="stat-value">${analysis.frames_analyzed}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">FPS:</span>
                <span class="stat-value">${analysis.fps}</span>
            </div>
        </div>
    `;

    // Update age
    document.getElementById('ageResult').textContent = `${analysis.age} years`;

    // Update gender
    document.getElementById('genderResult').textContent = 
        analysis.gender.value.charAt(0).toUpperCase() + analysis.gender.value.slice(1);
    displayConfidenceBars('genderConfidence', analysis.gender.confidence);

    // Update emotion
    document.getElementById('emotionResult').textContent = 
        analysis.emotion.value.charAt(0).toUpperCase() + analysis.emotion.value.slice(1);
    displayConfidenceBars('emotionConfidence', analysis.emotion.confidence);

    // Update race
    document.getElementById('raceResult').textContent = 
        analysis.race.value.charAt(0).toUpperCase() + analysis.race.value.slice(1);
    displayConfidenceBars('raceConfidence', analysis.race.confidence);

    // Display emotion distribution if available
    if (analysis.emotion.distribution) {
        displayEmotionDistribution(analysis.emotion.distribution);
    }

    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
}

/**
 * Display confidence bars for a category
 */
function displayConfidenceBars(elementId, confidenceData) {
    const container = document.getElementById(elementId);
    container.innerHTML = '';

    // Sort by confidence value (descending)
    const sortedData = Object.entries(confidenceData)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3); // Show top 3

    sortedData.forEach(([label, value]) => {
        const barDiv = document.createElement('div');
        barDiv.className = 'confidence-bar';

        const labelDiv = document.createElement('div');
        labelDiv.className = 'confidence-label';
        labelDiv.innerHTML = `
            <span>${label.charAt(0).toUpperCase() + label.slice(1)}</span>
            <span>${value.toFixed(1)}%</span>
        `;

        const progressDiv = document.createElement('div');
        progressDiv.className = 'confidence-progress';

        const fillDiv = document.createElement('div');
        fillDiv.className = 'confidence-fill';
        fillDiv.style.width = `${value}%`;

        progressDiv.appendChild(fillDiv);
        barDiv.appendChild(labelDiv);
        barDiv.appendChild(progressDiv);
        container.appendChild(barDiv);
    });
}

/**
 * Display emotion distribution chart
 */
function displayEmotionDistribution(distribution) {
    const container = document.getElementById('emotionChart');
    container.innerHTML = '';

    // Sort by count (descending)
    const sortedEmotions = Object.entries(distribution)
        .sort((a, b) => b[1] - a[1]);

    const maxCount = Math.max(...sortedEmotions.map(([, count]) => count));

    sortedEmotions.forEach(([emotion, count]) => {
        const emotionBar = document.createElement('div');
        emotionBar.className = 'emotion-bar-item';

        const percentage = (count / maxCount) * 100;

        emotionBar.innerHTML = `
            <div class="emotion-bar-label">
                <span>${emotion.charAt(0).toUpperCase() + emotion.slice(1)}</span>
                <span>${count} frames</span>
            </div>
            <div class="emotion-bar-graph">
                <div class="emotion-bar-fill" style="width: ${percentage}%"></div>
            </div>
        `;

        container.appendChild(emotionBar);
    });

    document.getElementById('emotionTimeline').style.display = 'block';
}
