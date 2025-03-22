// AprilTag Detection System - Frontend JavaScript

// DOM elements
const tagsCountElement = document.getElementById('tags-count');
const processingFpsElement = document.getElementById('processing-fps');
const lastDetectionElement = document.getElementById('last-detection');

// Function to fetch and update statistics
function updateStats() {
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            tagsCountElement.textContent = data.tags_detected;
            processingFpsElement.textContent = data.processing_fps;
            
            if (data.last_detection_time) {
                lastDetectionElement.textContent = data.last_detection_time;
            } else {
                lastDetectionElement.textContent = 'Never';
            }
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
        });
}

// Update stats every second
setInterval(updateStats, 1000);

// Initial stats update
updateStats();

// Handle video stream errors
const videoFeed = document.getElementById('video-feed');
videoFeed.onerror = function() {
    console.error('Error loading video feed');
    videoFeed.style.display = 'none';
    const videoContainer = document.querySelector('.video-container');
    videoContainer.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <h3 style="color: #ff6b6b;">Video Stream Unavailable</h3>
            <p>The camera stream could not be loaded. Please check your connection and refresh the page.</p>
        </div>
    `;
};

// Add responsive behavior
function handleResize() {
    const container = document.querySelector('.container');
    const windowWidth = window.innerWidth;
    
    if (windowWidth < 768) {
        container.style.padding = '10px';
    } else {
        container.style.padding = '20px';
    }
}

// Listen for window resize
window.addEventListener('resize', handleResize);

// Initial call
handleResize();
