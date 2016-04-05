import numpy as np
import cv2

def contoursGen(gray, candidate = 5):

	edges = cv2.Canny(gray,
		cv2.getTrackbarPos('Canny-Arg-1', 'control'),
		cv2.getTrackbarPos('Canny-Arg-2', 'control'),
		L2gradient = True)


	cv2.imshow('edges', edges)

	# cv2.findContours will change input paramenter edges.
	# do this router,if you want to using edges at other place 
	_, contours, hierarchy = cv2.findContours(np.copy(edges),
	# _, contours, hierarchy = cv2.findContours(edges,
		cv2.RETR_LIST,
		# cv2.CHAIN_APPROX_SIMPLE)
		cv2.RETR_CCOMP)

	# select first 5 bigger contours
	contours = sorted(contours,
		key = cv2.contourArea,
		reverse = True)[:candidate]

	rate = cv2.getTrackbarPos('approxPolyDP-Rate', 'control')
	rate = float(rate) / 100.0

	for ctrn in range(len(contours)):
		ctr = contours[ctrn]
		apx = cv2.approxPolyDP(ctr,
			float(cv2.arcLength(ctr, True)) * rate,
			True)
	
		yield ctr, apx

def main():
	cap = cv2.VideoCapture(0)

	def setExposure(x):
		cap.set(cv2.CAP_PROP_EXPOSURE, float(-x))

	cv2.namedWindow('control', cv2.WINDOW_NORMAL)
	cv2.createTrackbar('exposure', 'control', int(-cap.get(cv2.CAP_PROP_EXPOSURE)), 10, setExposure)
	cv2.createTrackbar('approxPolyDP-Rate', 'control', 2, 10, lambda x: None)
	cv2.createTrackbar('Canny-Arg-1', 'control', 160, 255, lambda x: None)
	cv2.createTrackbar('Canny-Arg-2', 'control', 230, 255, lambda x: None)

	try:
		if cap.isOpened():
			while cap.isOpened():
				_, frame = cap.read()
				cv2.imshow('orginal', frame)
				result = np.copy(frame)

				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				gray = cv2.bilateralFilter(gray, 9, 75, 75)

				contours = contoursGen(gray, 3)
				t = list()
				for ctr, apx in contours:
					t.append(ctr)
					try:
						M = cv2.moments(ctr)
						cx = int(M['m10'] / M['m00'])
						cy = int(M['m01'] / M['m00'])

						cv2.putText(result,
							'%d' % len(apx),
							(cx, cy),
							cv2.FONT_HERSHEY_COMPLEX_SMALL,
							1,
							(0, 255, 0))

					except ZeroDivisionError as e:
						pass

				cv2.drawContours(result, t, -1, (0, 0, 255), -1)

				cv2.imshow('result', result)


				if (cv2.waitKey(1) & 0xFF) == ord('q'):
					break
		else:
			print 'please connect camera'
	except Exception as e:
		print e
	finally:
		cap.release()
		cv2.destroyAllWindows()

if __name__ == '__main__':
	main()