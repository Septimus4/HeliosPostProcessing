
# HeliosPostProcessing

## Overview
**HeliosPostProcessing** is a Python-based post-processing tool designed to work in conjunction with the [HeliosIA](https://github.com/Septimus4/HeliosIA) framework. It processes drone-captured aerial videos of neighborhoods, focusing on nighttime road activity. Offering configurable options for advanced data transformation.

This project supports Docker for easy setup and deployment, allowing for consistent and reproducible environments.

## Features
- Python post-processing scripts for HeliosIA data.
- Dockerized environment for ease of use.
- Customizable via `docker-compose.yml`.
- Core processing logic located in `Core.py`.

## Installation

### Prerequisites
- Docker
- Python 3.x

### Clone the Repository
```bash
git clone https://github.com/Septimus4/HeliosPostProcessing.git
cd HeliosPostProcessing
```

### Docker Setup
To build and run the application in Docker:
```bash
docker-compose up --build
```

After processing, to clean up the Docker environment:
```bash
./cleardocker.sh
```

### Python Setup (Optional)
If you prefer to run the tool outside of Docker, install the necessary dependencies:
```bash
pip install -r requirements.txt
```

## Usage
To start the post-processing, run the core script:
```bash
python Core.py
```
Ensure that your output from [HeliosIA](https://github.com/Septimus4/HeliosIA) is available for processing.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request, or open an issue to discuss proposed changes.

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT), which allows for modification, forking, and redistribution.
