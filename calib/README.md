# Intrinsics calibration

## 🏗️ Requirements

- Deactivate legacy camera support via `sudo raspi-config` :arrow_right: `Interface Options` :arrow_right: `Legacy Camera` :arrow_right: `no`
- Check `picamera2` library (default at the Raspbian distro)
``` python
python3
import picamera2
```
- Have a bright light source directly behind the camera
- Print a [calibration pattern](https://docs.opencv.org/4.x/da/d0d/tutorial_camera_calibration_pattern.html) - ours has 11 X 12 with 30cm side square ([PDF](https://github.com/debOliveira/myCameraCalibrator/tree/main/python/pdf))

## 🧰 Configuration

### Gain, Exposure, White Balance

- The gain, exposure, white balance are set to adjust automatically during the first 5 seconds
- Approximate the calibration pattern in these 5 seconds so the image is very bright

## ⚔️ Usage

- Run `python3 calibCapture.py`. For example:
```sh
cd ~/MoCapRasp/calib
python3 calibCapture.py --output_folder=/home/pi/pics
```
- Run `python3 calibCapture.py --help` for description of input arguments.
- Copy the images to the server (use `scp`) and run the [camera calibrator application](https://github.com/debOliveira/myCameraCalibrator)

## 🖼️ Example pics

 <p align="center">
<img src="https://user-images.githubusercontent.com/48807586/177628962-0bc55667-9e42-4df5-b561-c19c39566cfd.png" height="300" align="center">
<img src="https://user-images.githubusercontent.com/48807586/177629909-fe780ae5-4fff-4817-a7e8-bd28ac0e00a5.png" height="300" align="center"><br><br>
<img src="https://user-images.githubusercontent.com/48807586/177629924-51aee180-2a6a-44b6-892f-6906a22174c9.png" height="300" align="center">
<img src="https://user-images.githubusercontent.com/48807586/177630302-cd32b6c9-6b18-49d8-9d33-7db810586d98.png" height="300" align="center">
</p>