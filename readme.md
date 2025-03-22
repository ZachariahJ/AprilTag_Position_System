# AprilTag Detection System

A Raspberry Pi-based system that detects AprilTags using the PiCamera and provides a web interface via Flask.

## Features

- **Clean Separation**: Backend and frontend components are clearly separated
- **Flask Web Interface**: Modern responsive web interface for viewing the detection stream
- **Real-time Statistics**: Live updates of detection counts, FPS, and detection times
- **Simplified Detection**: Focuses on the most common AprilTag family (tag36h11) for reliability
- **Modular Design**: Easily extensible with additional features

## Project Structure

```
apriltag-detection/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── backend/                    # Backend components
│   ├── __init__.py            
│   ├── camera_manager.py       # Camera handling
│   ├── apriltag_detector.py    # AprilTag detection
│   └── frame_processor.py      # Frame processing and streaming
└── frontend/                   # Frontend components
    ├── templates/              # HTML templates
    │   └── index.html          # Main page template
    └── static/                 # Static assets
        ├── style.css           # Stylesheet
        └── app.js              # Frontend JavaScript
```

## Requirements

- Raspberry Pi 4 (recommended) or Raspberry Pi 3
- Raspberry Pi Camera Module
- Python 3.7+
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/apriltag-detection.git
   cd apriltag-detection
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Raspberry Pi specific dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-picamera2
   ```

## Usage

1. Run the application:
   ```bash
   python app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://<raspberry_pi_ip>:5000
   ```

## Troubleshooting

### Common Issues

1. **"Unrecognized tag family name"**:
   - This error occurs when the AprilTag detector receives incorrect family format
   - Solution: Make sure to pass families as a list, not a string

2. **Camera not working**:
   - Check that the camera is properly connected
   - Ensure the camera is enabled in Raspberry Pi configuration

3. **Low FPS**:
   - Try reducing the resolution in `camera_manager.py`
   - Set `quad_decimate` to a higher value (e.g., 2.0) for faster processing

## Customization

- To use different tag families: Edit the `tag_family` variable in `backend/apriltag_detector.py`
- To change the camera resolution: Modify the resolution parameter in `app.py`
- To customize the UI: Edit the files in the `frontend` directory

## License

This project is released under the MIT License.
