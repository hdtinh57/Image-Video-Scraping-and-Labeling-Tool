# Image & Video Scraping and Labeling Tool

This project is a PyQt5-based application designed to help you build datasets for computer vision tasks such as training YOLO detectors. The tool integrates three main functionalities: image scraping, image labeling, and video frame extraction (video scraping).

## Features

### 1. Image Scraping
- **Web Image Search & Download:**  
  Uses the DuckDuckGo Search API (via the `duckduckgo_search` library) to search for images based on a given keyword and class name.
- **Preview & Download:**  
  Preview each image and choose to download it to a structured folder (`dataset/<class_name>/`).

### 2. Image Labeling
- **Interactive Labeling Interface:**  
  Load images from a dataset folder and draw bounding boxes directly on the images to label objects.
- **Bounding Box Editing:**  
  Edit, delete, and undo/redo bounding boxes using a context menu.
- **Annotation Saving:**  
  Save annotations in YOLO format (i.e., `<class_id> <x_center> <y_center> <width> <height>`, with normalized coordinates).

### 3. Video Scraping
- **Video Loading:**  
  Load video files from local storage or directly from YouTube (using [yt_dlp](https://github.com/yt-dlp/yt-dlp)). When downloading from YouTube, the video is saved using its title.
- **Frame Navigation:**  
  Navigate through video frames using a slider that displays the current time and total duration.
- **Jump to Specific Time:**  
  Input a specific time (in seconds, mm:ss, or hh:mm:ss format) to jump directly to the corresponding frame.
- **Frame Saving:**  
  Save the currently displayed frame into a folder under `dataset/<video_title>/` using a filename pattern of `{short_video_title}_{frame_index}.jpg` (where the video title is sanitized and shortened).

## Installation
1. **Clone the Repository:**
2. **Create a Virtual Environment (recommended):**
3. **Install Dependencies:**

## Usage
After installing the dependencies, run the application with:
```bash
python main.py
```

## Contributing
Contributions, suggestions, and bug reports are welcome! Please open an issue or submit a pull request with improvements.