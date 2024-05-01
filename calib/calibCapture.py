import os
import sys
import time
import argparse
import libcamera
from libcamera import controls
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder, Quality


def capture_calibration_image_set(output_folder: str, capture_delay: int, image_dim: tuple, num_images: int) -> None:
    """
    Capture a set of images uing the raspberry camera module for calibration

    Args:
        output_folder: the path to the folder in which image files will be written
        capture_delay: delay (in seconds) between captured images
        num_images: the number of image files to capture

    Raises:
        ValueError: If output_folder does not exist
        ValueError: If capture_delay is negative
        ValueError: If num_images is negative
    """

    # checkout function input
    if not os.path.isdir(output_folder):
        raise ValueError(f"Directory {output_folder} does not exist.")
    else:
        print(f"[WARNING] {output_folder} does not exist, creating directory")
        os.system(f"mkdir -p {output_folder}")

    if capture_delay < 0:
        raise ValueError(f"{capture_delay} must be a positive integer.")

    if num_images < 0:
        raise ValueError(f"{num_images} must be a positive integer.")

    # remove contents of output folder
    print(f"Removing contents of {output_folder}")
    os.system(f"rm -rf {output_folder}/*")

    # set controls to suite camera calibration (see Table 7 of picam2 docs)
    preview_controls = {
        "AfMode": controls.AfModeEnum.Manual, "Saturation": 0.0}
    video_controls = {"AeEnable": False, "AwbEnable": False}
    video_controls.update(preview_controls)

    # begin capturing
    print("[INFO] Capturing calibration image set")

    # start preview and set warm-up time for automatically ajusting gain, exposure, white balance, etc.
    picam2 = Picamera2()
    picam2.start_preview(Preview.QTGL, transform=libcamera.Transform(hflip=1))
    picam2.configure(picam2.create_preview_configuration(
        main={"size": image_dim}, controls=preview_controls))
    print("[INFO] Starting camera warm-up")
    picam2.start()
    time.sleep(5)
    picam2.stop()
    print("[INFO] camera warm-up complete")

    # start video stream
    picam2.configure(picam2.create_video_configuration(
        main={"size": image_dim}, controls=video_controls, encode="main"))
    encoder = H264Encoder(10000000)
    picam2.start_recording(encoder, output_folder +
                           "/video_tmp.h264", quality=Quality.HIGH)
    print("[INFO] Recording started. Capturing still images")

    # capture stills from stream for calibration
    for image_id in range(num_images):
        print(dynamic_loading_bar(image_id+1, num_images), end="\r")
        request = picam2.capture_request()
        # set ID to be compatible with kalibr_bagcreater
        request.save("main", output_folder+f"/{image_id}000000000.png")
        request.release()
        time.sleep(capture_delay)

    # finish
    os.system(f"rm -rf {output_folder}/video_tmp.h264")
    picam2.stop_recording()
    print("[INFO] Capturing completed. Exiting.")


def dynamic_loading_bar(image_id: int, num_images: int) -> None:
    """
    Print a dynamic loading bar indicating the number of images captured.

    Args:
        image_id: the ID of the captured image
        num_images: the number of image files to capture
    """
    bar_length = 40
    filled_length = int(bar_length * image_id/num_images)
    bar = "[" + "=" * filled_length + "-" * (bar_length - filled_length) + "]"
    return f"[INFO] Capturing still images: {bar} image {image_id} of {num_images} captured"


def main(args):
    parser = argparse.ArgumentParser(
        description='This script is used to collect a set of grey-scale images for camera calibration.')

    parser.add_argument('-o', '--output_folder', type=str,
                        help='output folder', required=True)
    parser.add_argument('-d', '--capture_delay', type=int,
                        help='delay in image capture (sec)', default=1)
    parser.add_argument('-i', '--image_dim', type=tuple,
                        help='dimension of image', default=(1536, 864))
    parser.add_argument('-n', '--num_images', type=int,
                        help='number of image files to collect ', default=60)

    args = parser.parse_args()
    output_folder = args.output_folder
    capture_delay = args.capture_delay
    image_dim = args.image_dim
    num_images = args.num_images

    # pair and restamp data/time message couples
    capture_calibration_image_set(
        output_folder, capture_delay, image_dim, num_images)


if __name__ == "__main__":
    main(sys.argv[1:])
