// AprilTag 6DOF Detection System - Frontend JavaScript

// DOM elements
const tagsCountElement = document.getElementById('tags-count');
const processingFpsElement = document.getElementById('processing-fps');
const lastDetectionElement = document.getElementById('last-detection');
const poseDataContainer = document.getElementById('pose-data-container');

// Additional DOM elements for latest pose stats
const latestTagIdElement = document.getElementById('latest-tag-id');
const latestDistanceElement = document.getElementById('latest-distance');
const latestPositionElement = document.getElementById('latest-position');
const latestRollElement = document.getElementById('latest-roll');
const latestPitchElement = document.getElementById('latest-pitch');
const latestYawElement = document.getElementById('latest-yaw');

// Function to fetch and update statistics
function updateStats() {
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            // Update basic stats
            tagsCountElement.textContent = data.tags_detected;
            processingFpsElement.textContent = data.processing_fps;
            
            if (data.last_detection_time) {
                lastDetectionElement.textContent = data.last_detection_time;
            } else {
                lastDetectionElement.textContent = 'Never';
            }
            
            // Update latest pose data in statistics area (for first tag)
            updateLatestPoseStats(data.pose_data || []);
            
            // Update all pose data
            updatePoseData(data.pose_data || []);
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
        });
}

// Function to update the latest pose statistics
function updateLatestPoseStats(poseData) {
    const latestPoseStatsElement = document.getElementById('latest-pose-stats');
    
    if (poseData.length === 0) {
        // Hide or reset pose stats if no tags detected
        latestTagIdElement.textContent = '-';
        latestDistanceElement.textContent = '-';
        latestPositionElement.textContent = '-';
        latestRollElement.textContent = '-';
        latestPitchElement.textContent = '-';
        latestYawElement.textContent = '-';
        return;
    }
    
    // Get the first detected tag (assumed to be the most prominent)
    const latestTag = poseData[0];
    
    // Update the pose statistics
    latestTagIdElement.textContent = latestTag.tag_id;
    latestDistanceElement.textContent = `${latestTag.distance.toFixed(3)} m`;
    latestPositionElement.textContent = `X:${latestTag.position.x.toFixed(2)}, Y:${latestTag.position.y.toFixed(2)}, Z:${latestTag.position.z.toFixed(2)}`;
    latestRollElement.textContent = `${latestTag.angles.roll.toFixed(1)}°`;
    latestPitchElement.textContent = `${latestTag.angles.pitch.toFixed(1)}°`;
    latestYawElement.textContent = `${latestTag.angles.yaw.toFixed(1)}°`;
}

// Function to update pose data display
function updatePoseData(poseData) {
    // Clear previous pose data
    poseDataContainer.innerHTML = '';
    
    if (poseData.length === 0) {
        poseDataContainer.innerHTML = '<p class="no-tags">No tags detected</p>';
        return;
    }
    
    // Create a table for each detected tag
    poseData.forEach(tag => {
        const tagTable = document.createElement('div');
        tagTable.className = 'tag-data';
        
        // Tag header
        const tagHeader = document.createElement('h3');
        tagHeader.textContent = `Tag ID: ${tag.tag_id}`;
        tagTable.appendChild(tagHeader);
        
        // Tag distance
        const distanceRow = document.createElement('div');
        distanceRow.className = 'data-row';
        distanceRow.innerHTML = `
            <span class="data-label">Distance:</span>
            <span class="data-value">${tag.distance.toFixed(3)} meters</span>
        `;
        tagTable.appendChild(distanceRow);
        
        // Tag angles
        const anglesRow = document.createElement('div');
        anglesRow.className = 'data-row';
        anglesRow.innerHTML = `
            <span class="data-label">Angles:</span>
            <span class="data-value">
                Roll: ${tag.angles.roll.toFixed(1)}°,
                Pitch: ${tag.angles.pitch.toFixed(1)}°,
                Yaw: ${tag.angles.yaw.toFixed(1)}°
            </span>
        `;
        tagTable.appendChild(anglesRow);
        
        // Tag position
        const positionRow = document.createElement('div');
        positionRow.className = 'data-row';
        positionRow.innerHTML = `
            <span class="data-label">Position:</span>
            <span class="data-value">
                X: ${tag.position.x.toFixed(3)},
                Y: ${tag.position.y.toFixed(3)},
                Z: ${tag.position.z.toFixed(3)}
            </span>
        `;
        tagTable.appendChild(positionRow);
        
        // Tag direction
        const directionRow = document.createElement('div');
        directionRow.className = 'data-row';
        directionRow.innerHTML = `
            <span class="data-label">Direction:</span>
            <span class="data-value">
                [${tag.direction[0].toFixed(2)}, 
                ${tag.direction[1].toFixed(2)}, 
                ${tag.direction[2].toFixed(2)}]
            </span>
        `;
        tagTable.appendChild(directionRow);
        
        // Add table to container
        poseDataContainer.appendChild(tagTable);
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