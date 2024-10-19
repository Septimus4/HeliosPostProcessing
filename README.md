# HeliosPostProcessing

HeliosPostProcessing is an AI-driven pipeline for processing videos to detect and count objects using a trained YOLO model. It automates the workflow from fetching new videos from a MongoDB database, running predictions, counting detected objects, and uploading the analysis results back to the database.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Example Configuration File](#example-configuration-file)
  - [MongoDB Credentials](#mongodb-credentials)
- [Usage](#usage)
- [Pipeline Workflow](#pipeline-workflow)
- [Error Handling](#error-handling)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

- **Automated Video Processing**: Monitors a MongoDB GridFS for new video uploads and processes them automatically.
- **Object Detection**: Utilizes a YOLO-based AI model for object detection in videos.
- **Object Counting**: Analyzes each frame to count detected objects.
- **Results Export**: Exports counting results in a CSV format suitable for database ingestion.
- **MongoDB Integration**: Uploads analysis results back to a MongoDB database.
- **Configurable Pipeline**: Fully customizable via a JSON configuration file.
- **Demo Mode**: Ability to run in demo mode without actual model prediction, useful for testing.

## Prerequisites

- **Python 3.x**
- **MongoDB** with GridFS configured
- **Python Packages**: Install required packages using `requirements.txt`

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Septimus4/HeliosPostProcessing.git
   cd HeliosPostProcessing
   ```

2. **Install Python Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up MongoDB**

   Ensure that MongoDB is installed, running, and accessible with the credentials you will provide in the configuration.

## Configuration

All configurations are managed through a JSON file (e.g., `config.json`) located in the `Config` directory. This file contains settings for the pipeline, including paths to models, databases, and other resources.

### Example Configuration File

Create a `config.json` file in the `Config` directory with the following content:

```json
{
    "is_demo": false,
    "location": "test01",
    "config_mongo": "./Config/mongodb.json",
    "db_get": "VideoToModel",
    "db_upload": "IAAnalysis",
    "expframe_config": {
        "filepath": "./Predict/OutFrames/test01.helios",
        "method": ["yolo", "./Config/FilesToPred/new_classes_order.txt"]
    },
    "expy_pred": "./Predict/OutFrames/test01.helios",
    "model_config": {
        "model_path": "./LastModel_yv3/yolov3_15102020_final.h5",
        "anchors_path": "./Config/FilesToPred/yolo_anchors.txt",
        "classes_path": "./Config/FilesToPred/data_classes.txt",
        "score": 0.5,
        "model_image_size": [416, 416]
    },
    "path_eq": "./Scripts/MapToPy/DataOut/test01.json"
}
```

#### Configuration Parameters:

- **is_demo**: *(boolean)* Run the pipeline in demo mode without model prediction.
- **location**: *(string)* Identifier for the processing location.
- **config_mongo**: *(string)* Path to the MongoDB credentials file.
- **db_get**: *(string)* Name of the MongoDB database to fetch videos from.
- **db_upload**: *(string)* Name of the MongoDB database to upload analysis results.
- **expframe_config**: *(object)* Configuration for exporting frames.
  - **filepath**: *(string)* Path to save exported frames.
  - **method**: *(array)* Method and parameters for frame export.
- **expy_pred**: *(string)* Path to the exported predictions file.
- **model_config**: *(object)* AI model configuration.
  - **model_path**: *(string)* Path to the trained model file.
  - **anchors_path**: *(string)* Path to the YOLO anchors file.
  - **classes_path**: *(string)* Path to the classes file.
  - **score**: *(number)* Confidence threshold for object detection.
  - **model_image_size**: *(array)* Input image size for the model.
- **path_eq**: *(string)* Path to the mapping equations file.

### MongoDB Credentials

Create a `mongodb.json` file in the `Config` directory with your MongoDB credentials:

```json
{
    "host": "localhost",
    "port": 27017,
    "username": "your_username",
    "password": "your_password",
    "authSource": "admin"
}
```

## Usage

Run the main script to start the pipeline:

```bash
python main.py
```

### Command-Line Arguments

- **--config**: Specify a custom path to the configuration file (default is `./Config/config.json`).
- **--show_graphics**: Display graphical output during processing (set to `True` or `False`).

Example:

```bash
python main.py --config ./Config/custom_config.json --show_graphics True
```

## Pipeline Workflow

1. **Initialization**: The `Core` class is initialized with the configuration settings.
2. **Monitoring**: The pipeline monitors the specified MongoDB database for new video uploads.
3. **Download**: When a new video is detected, it is downloaded locally.
4. **Prediction**:
   - If `is_demo` is `false`, the video is processed using the YOLO model specified in `model_config`.
   - Predictions are saved in a protobuf structure for efficient handling.
5. **Counting Objects**:
   - Predictions are loaded and analyzed frame by frame.
   - Objects are counted using the methods specified in `expframe_config`.
6. **Exporting Results**:
   - Counting results are exported in CSV format.
   - The data is formatted for database insertion.
7. **Uploading**:
   - The formatted results are uploaded to the MongoDB database specified in `db_upload`.
8. **Cleanup**: Temporary files are deleted, and the system returns to monitoring for new videos.

## License

[MIT License](LICENSE)
