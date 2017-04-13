# USAGE
# python test_video.py

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import imutils
import argparse
import numpy
import datetime as dt

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
ap.add_argument("-c", "--codec", type=str, default="X264", help="codec of output video")

args = vars(ap.parse_args())

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
avg = None


# allow the camera to warmup
time.sleep(0.1)
motionCounter = 0

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	frame = frame.array
	text = "Empty"

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (5,5), 0)

	# if the average frame is None, initialize it
	if avg is None:
		print "[INFO] starting background model..."
		avg = gray.copy().astype("float")
		rawCapture.truncate(0)
		continue

	# accumulate the weighted average between the current frame and
	# previous frames, then compute the difference between the current
	# frame and running average
	cv2.accumulateWeighted(gray, avg, 0.6)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

	# threshold the delta image, dilate the thresholded image to fill
	# in holes, then find contours on thresholded image
	thresh = cv2.threshold(gray, 25, 255,
		cv2.THRESH_BINARY_INV)[1]
        (gray,cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)

     

        
        #loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
		text = "Object Detected"


	#annotate text time
        wk = dt.datetime.now().strftime('%d-%m-%Y | %H:%M:%S')
        cv2.putText(frame, wk, (5, frame.shape[0] - 10), cv2.FONT_HERSHEY_DUPLEX,
		0.6, (255, 255, 255), 1)
        cv2.putText(frame, "Room Status : {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 128), 1)
	
	



	# show the frame
	cv2.imshow("Frame", frame)
	#cv2.imshow("Frame Delta", frameDelta)
	#cv2.imshow("Frame Thresh", thresh)
	#cv2.imshow("output", output)
	key = cv2.waitKey(1) & 0xFF

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break


