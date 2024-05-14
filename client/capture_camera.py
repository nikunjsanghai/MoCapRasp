import RPi.GPIO as GPIO
import picamera2
import picamera2.encoders
import picamera2.sensors
import time
import cv2
import numpy as np
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-w', type=int, default=960, help='Image width')
parser.add_argument('-h', type=int, default=720, help='Image height')
parser.add_argument('-md', type=int, default=4, help='Camera sensor mode')
parser.add_argument('-p', type=str, default='0,0,960,640', help='Crop window (x,y,width,height)')
args = parser.parse_args()

# LED setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led = 4
GPIO.setup(led, GPIO.OUT)
print("[INFO] LED on and parameters configured")
GPIO.output(led, 1)

# Parse crop window
crop_window = tuple(map(int, args.p.split(',')))

# Create a camera instance
picam2 = picamera2.Picamera2()

# Configure the camera settings
preview_config = picam2.create_preview_configuration(
    main={"size": (args.w, args.h)},
    lores={
        "size": (args.w, args.h),
        "crop": crop_window,
    },
    display=None,
)
picam2.configure(preview_config)

# Set the sensor mode
picam2.sensor_mode = args.md

# Start the camera preview
picam2.start()

# Create an encoder for YUV output
encoder = picamera2.encoders.yuv.YuvEncoder(
    width=args.w,
    height=args.h,
    lores_size=(args.w, args.h),
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
GPIO.output(led, 0)
print('[INFO] buffer closed and LED off')
