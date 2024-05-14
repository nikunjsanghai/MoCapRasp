import numpy as np
import picamera
import picamera.array
import RPi.GPIO as GPIO
import time, cv2, atexit, socket, argparse

# Parser for command line
parser = argparse.ArgumentParser(description='''Capture client for the MoCap system at the Erobotica lab of UFCG.
                                                \nPlease use it together with the corresponding server script.''', add_help=False)
parser.add_argument('-w', type=int, help='image width (default: 960px)', default=960)
parser.add_argument('-h', type=int, help='image height (default: 720px)', default=720)
parser.add_argument('-fps', type=int, help='frames per second (default: 40FPS)', default=40)
parser.add_argument('-ag', type=int, help='camera analog gain (default: 2)', default=2)
parser.add_argument('-dg', type=int, help='camera digital gain (default: 4)', default=4)
parser.add_argument('-md', type=int, default=4, help='camera mode (default: 4)')
parser.add_argument('--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
args = parser.parse_args()

# Video capture parameters
(w, h) = (args.w, args.h)
md, ag, dg, fps = args.md, args.ag, args.dg, args.fps
winH = int(h * 960 / w)
print('[INFO] Size ' + str(w) + 'x' + str(h) + ', FPS ' + str(fps) + ', mode ' + str(md))

# Turning LED on
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led = 4
GPIO.setup(led, GPIO.OUT)
print("[INFO] LED on and parameters configured")
GPIO.output(led, 1)

# Server parameters
print('[INFO] connecting to server')
hostnamePC = socket.gethostbyname('debora-pc.local')
UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPSocket.sendto(str(str(w) + ',' + str(h) + ',' + str(md)).encode(), (hostnamePC, 8888))
message, _ = UDPSocket.recvfrom(1024)
start = float(message.split()[0])
max_frames = int(message.split()[1]) * fps
print('[INFO] waiting trigger')
now = time.time()
while now < start:
    now = time.time()
print('[INFO] delay in sec: ', now - start)

# Running camera capture
with picamera.PiCamera() as camera:
    camera.resolution = (w, h)
    camera.framerate = fps
    camera.analog_gain = ag
    camera.digital_gain = dg
    camera.sensor_mode = md
    time.sleep(2)  # Warm-up time for the camera
    camera.start_recording('/dev/null', format='yuv', resize=(w, winH), splitter_port=2)
    start = time.time()
    N_frames = 0
    while True:
        stream = picamera.array.PiYUVArray(camera, size=(w, winH))
        camera.capture(stream, format='yuv', use_video_port=True)
        frame = np.reshape(stream.array, (winH, w))
        ts = camera.frame.timestamp
        cv2.imwrite('/dev/shm/' + str(int(ts * 1e6)).zfill(10) + '.bmp', frame)
        stream.truncate(0)
        N_frames += 1
        if N_frames == max_frames:
            break
    camera.stop_recording(splitter_port=2)

# Closing buffer
end = time.time() - start
GPIO.output(led, 0)
print('[INFO] buffer closed and LED off')

# Verbose
elapsed_seconds = float(ts) / 1e6
print("[RESULTS] " + str(round(N_frames / elapsed_seconds, 2)) + " FPS (PTS) and " +
      str(round(N_frames / end, 2)) + " FPS (time lib)")
