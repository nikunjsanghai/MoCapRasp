import subprocess
import picamera2
import picamera2.encoders
import picamera2.sensors
import time
import cv2
import numpy as np

# Execute the LED.py script as a subprocess
subprocess.Popen(["python3", "LED.py"])

# Parse the command line arguments
width = 960
height = 720
sensor_mode = 4
crop_window = (0, 0, 960, 640)

# Create a camera instance
picam2 = picamera2.Picamera2()

# Configure the camera settings
preview_config = picam2.create_preview_configuration(
    main={"size": (width, height)},
    lores={
        "size": (width, height),
        "crop": crop_window,
    },
    display=None,
)
picam2.configure(preview_config)

# Set the sensor mode
picam2.sensor_mode = sensor_mode

# Start the camera preview
picam2.start()

# Create an encoder for YUV output
encoder = picamera2.encoders.yuv.YuvEncoder(
    width=width,
    height=height,
    lores_size=(width, height),
    lores_crop=crop_window,
    lores_yuv=True,
)

# Start the encoder
output = encoder.start()

# Capture and process frames
while True:
    try:
        # Get the next frame from the encoder
        frame = output.get_frame()

        # Process the frame as needed
        # For example, save the frame as an image
        timestamp = frame.timestamp
        image_data = frame.lores_yuv
        image_data = np.frombuffer(image_data, dtype=np.uint8)
        image_data = image_data.reshape((crop_window[3], crop_window[2], 2))
        cv2.imwrite(f"/dev/shm/{int(timestamp * 1e6):010d}.bmp", image_data[:, :, 0])

    except KeyboardInterrupt:
        break

# Stop the encoder and camera
output.stop()
encoder.stop()
picam2.stop()
