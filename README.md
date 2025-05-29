# WRO FUTURE ENGINEERS 2025
## Build, Compile and Upload Process

The project was developed using **Python** as the programming language. All source code was written and edited using **Visual Studio Code (VS Code)**, along with the official Python extension for syntax highlighting and code assistance.

To upload and run the program on the robot, we followed these steps:

1. Make sure the **Fischertechnik TXT Controller** and your **PC are connected to the same network** (Wi-Fi from the mobile hotspot).
2. Locate the TXT Controller’s **IP address** from its interface.
3. In VS Code, after writing and saving the Python files, connect to the robot using the **"Upload and Run File"** option to transfer the Python script to the controller and start execution.
4. The robot will automatically begin executing the code once the upload completes and by clicking the run button on its interface.

### Additional Python Libraries Used:
- `opencv-python` – for image processing and color detection
- `numpy` – for numerical operations and array handling
- `fischertechnik` – to communicate with motors, servos, and sensors

## Electromechanical components

  
## Camera and Color Detection

In this project, we use the OpenCV library for computer vision to detect obstacles of specific colors (red and green) and to measure their height within the camera frame.

Before detecting the color, we convert each frame from the default **BGR (Blue, Green, Red)** format to the **HSV (Hue, Saturation, Value)** color space. This improves color detection accuracy under different lighting conditions by separating color (hue) from brightness (value). This way we made sure that the color detection does not depend on the brightness and lighting in the room. 

We define specific HSV value ranges for detecting **red** and **green** regions. Red is split into two ranges due to its position at both ends of the hue spectrum:

```python
RED_LOWER1 = np.array([0, 70, 50])
RED_UPPER1 = np.array([10, 255, 255])
RED_LOWER2 = np.array([170, 70, 50])
RED_UPPER2 = np.array([180, 255, 255])

GREEN_LOWER = np.array([40, 70, 50])
GREEN_UPPER = np.array([80, 255, 255])
```

Later, we used this logic to determine which obstacle is the closest to the robot, meaning the bigger number of pixels of a certain color point to the traffic sign in front of the camera. 
