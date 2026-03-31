const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const uploadSection = document.getElementById('upload-section');
const loadingSection = document.getElementById('loading-section');
const resultSection = document.getElementById('result-section');
const previewImg = document.getElementById('preview-img');
const resultBadge = document.getElementById('result-badge');
const confidenceText = document.getElementById('confidence-text');
const confidenceFill = document.getElementById('confidence-fill');
const resultExplanation = document.getElementById('result-explanation');
const resetBtn = document.getElementById('reset-btn');

// Trigger file input on click
browseBtn.addEventListener('click', () => {
    fileInput.click();
});

// Drag and drop events
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
        dropZone.classList.add('dragover');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('dragover');
    }, false);
});

// Handle file drop
dropZone.addEventListener('drop', (e) => {
    let dt = e.dataTransfer;
    let files = dt.files;
    handleFiles(files);
});

// Handle file selection
fileInput.addEventListener('change', function () {
    handleFiles(this.files);
});

function handleFiles(files) {
    if (files.length > 0) {
        const file = files[0];
        if (file.type.startsWith('image/')) {
            processUpload(file);
        } else {
            alert('Please select a valid image file.');
        }
    }
}

function processUpload(file) {
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
    };
    reader.readAsDataURL(file);

    // Update UI states
    uploadSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');

    // Send to backend
    const formData = new FormData();
    formData.append('file', file);

    // Send to backend via absolute URL so it works even if index.html is opened directly
    fetch('http://localhost:8000/api/detect', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            displayResults(data.label, data.confidence);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during verification. Please try again.');
            resetUI();
        });
}

function displayResults(label, confidence) {
    loadingSection.classList.add('hidden');
    resultSection.classList.remove('hidden');

    const isReal = label.toUpperCase() === 'REAL' || label.toUpperCase() === 'ORIGINAL';
    const confPercent = Math.round(confidence * 100);

    // Animate percentage text and progress bar
    confidenceFill.style.width = '0%';
    setTimeout(() => {
        confidenceFill.style.width = `${confPercent}%`;
    }, 100);

    // Update badge styling
    resultBadge.textContent = isReal ? 'REAL' : 'FAKE';
    resultBadge.className = `result-badge ${isReal ? 'real' : 'fake'}`;

    // Update progress bar styling
    confidenceFill.className = `progress-bar-fill ${isReal ? 'real' : 'fake'}`;

    // Animate text counter
    let currentPercent = 0;
    const interval = setInterval(() => {
        if (currentPercent >= confPercent) {
            clearInterval(interval);
            confidenceText.textContent = `${confPercent}%`;
        } else {
            currentPercent++;
            confidenceText.textContent = `${currentPercent}%`;
        }
    }, 10);

    // Set explanation text
    if (isReal) {
        if (confPercent > 90) {
            resultExplanation.innerHTML = `High confidence! The model detects natural features, authentic noise patterns, and lighting consistency typical of a real photograph. No obvious signs of AI generation were found.`;
        } else {
            resultExplanation.innerHTML = `This image leans towards being real, but the model exhibits some uncertainty. While most features appear authentic, certain elements might resemble AI traits.`;
        }
    } else {
        if (confPercent > 90) {
            resultExplanation.innerHTML = `Highly likely to be AI-generated! The model detected artifacts typical of deepfakes, such as inconsistent lighting, unnatural textures, or structural anomalies often produced by GANs or Diffusion models.`;
        } else {
            resultExplanation.innerHTML = `This image is suspected to be a deepfake or manipulated. The model identified suspicious patterns, though some features appear natural, resulting in moderate confidence.`;
        }
    }
}

function resetUI() {
    fileInput.value = '';
    resultSection.classList.add('hidden');
    loadingSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
    confidenceFill.style.width = '0%';
}

resetBtn.addEventListener('click', resetUI);
