import cv2
import numpy as np
import time
import math
import serial  

try:
	print "Trying to establish connection ..."
	arduino = serial.Serial('/dev/ttyACM0', 9600,timeout=1)
	print arduino.readline()
	
except:
	print "Connect Arduino / change the index to something else"
	

	
def data(angle):
      
	try:    
		
		print "Transferring data to Arduino... "
		val = str(angle)	
		print val
		arduino.write(val)
		time.sleep(0)
		#print "echo:"
		#print arduino.readline()
		
     	
	except:    
		print "Failed to send!"
		
		
# Start Recording 
cap = cv2.VideoCapture(1)
time.sleep(4)
# HSV values to detect orange colour
h,s,v,counter,l,m = 0,255,213,1,8,8 # Orange 
h0,s0,v0 = 24,207,87  # green
# Daylight
h0,s0,v0 = 32,75,145  # green
h,s,v,counter,l,m = 13,88,222,1,8,8 # Orange 
h1,s1,v1 = 50,96,0

# Masking boundaries...
lower_colour = np.array([h,s,v])
upper_colour = np.array([180,255,255])

lower_colour0 = np.array([h0,s0,v0])
upper_colour0 = np.array([180,255,255])

lower_colour1 = np.array([h1,s1,v1])
upper_colour1 = np.array([180,255,255])

# declarations
centroid_x,centroid_y = 0,0

while(True) : 
	_, frame = cap.read()
	
	# RGB to HSV
	hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
	
	# Calculating mask from hsv
	mask = cv2.inRange(hsv,lower_colour, upper_colour)
	mask0 = cv2.inRange(hsv,lower_colour0, upper_colour0)
	mask1 = cv2.inRange(hsv,lower_colour1, upper_colour1)
	
	
	# Finding contours to find Moments & Centroid
	contours, hierarchy = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	contours0, hierarchy0 = cv2.findContours(mask0,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	contours1, hierarchy1 = cv2.findContours(mask1,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	cv2.drawContours(mask,contours,-1,(255,255,225),-1)
	cv2.imshow('Thimble', mask)
	
	# Initializing area parameter and its corresponding contour, named 'contour_max'
	area_max = 0
	area_max0 = 0
	area_max1 = 0
	
	###### !!!!Computational Burden!!!! You'll improve this somehow. #######
	for h,cnt in enumerate(contours):
		# Finding area of each contour and picking up the one with max area.
		area = cv2.contourArea(cnt)
		if (area > area_max) :
			area_max = area
			contour_max = cnt
			
			
	for h0,cnt0 in enumerate(contours0):
		# Finding area of each contour and picking up the one with max area.
		area = cv2.contourArea(cnt0)
		if (area > area_max0) :
			area_max0 = area
			contour_max0 = cnt0

	for h1,cnt1 in enumerate(contours1):
		# Finding area of each contour and picking up the one with max area.
		area = cv2.contourArea(cnt1)
		if (area > area_max1) :
			area_max1 = area
			contour_max1 = cnt1
			
	# Finding centroid of that cue.
	
	
	
	M = cv2.moments(contour_max)
	
	past_x,past_y = centroid_x,centroid_y
	centroid_x = int(M['m10']/M['m00'])
	centroid_y = int(M['m01']/M['m00'])
	print (centroid_x,centroid_y)
	
	M0 = cv2.moments(contour_max0)
	
	
	centroid_x0 = int(M0['m10']/M0['m00'])
	centroid_y0 = int(M0['m01']/M0['m00'])


	M1 = cv2.moments(contour_max1)
	
	
	centroid_x1 = int(M1['m10']/M1['m00'])
	centroid_y1 = int(M1['m01']/M1['m00'])
	# difference in X & difference in Y per time period
	dX,dY = -(past_x-centroid_x),-(past_y-centroid_y)
	
	cv2.circle(frame,(centroid_x,centroid_y),10,(0,255,0),-1)
	cv2.imshow('Tracked',frame)
	cv2.circle(frame,(centroid_x0,centroid_y0),10,(255,255,0),-1)
	cv2.imshow('Tracked',frame)
	cv2.circle(frame,(centroid_x1,centroid_y1),10,(0,255,255),-1)
	cv2.imshow('Tracked',frame)
	
	# Next probable coordinate prediction | Kinematic equations
	#try:
	#	if (dY !=0) or (dX !=0)
	#		theta = math.atan(dY/dX)
	#except:
	#	theta = 1.57		
	#	print "90' hit point"
	
	
#	Xp = centroid_x + (dX*(math.cos(theta)))
#	Yp = centroid_y + (dY*(math.sin(theta)))

	Xp = centroid_x + dX
	Yp = centroid_y + dY
	
	# Calculating alpha and beta for motors ... 
	# From that research paper
	
	r1 = math.sqrt((centroid_x0 - centroid_x1)*(centroid_x0 - centroid_x1) + (centroid_y0 - centroid_y1)*(centroid_y0 - centroid_y1))
	r2 = math.sqrt((centroid_x1 - centroid_x)*(centroid_x1 - centroid_x) + (centroid_y1 - centroid_y)*(centroid_y1 - centroid_y))
	a = Xp - centroid_x0
	b = Yp - centroid_y0

	a = float(a)
	b = float(b)
	
	try :
		
		al =  ((1/(2*r1*r2))*(a*a + b*b -(r1*r1 + r2*r2)))
		beta = math.acos((1/(2*r1*r2))*(a*a + b*b -(r1*r1 + r2*r2)))
	#	print ((1/(2*r1*r2))*(a*a + b*b -(r1*r1 + r2*r2)))
	#	print ((1/(a*a + b*b)) * ((a*(r1+r2*math.cos(beta)))+ (b*r2*math.sqrt(1- ((math.cos(beta))*(math.cos(beta)))))))
	#	print (1/(a*a + b*b))
	#	print ((1/(a*a + b*b)) * ((a*(r1+r2*al))+ (b*r2*math.sqrt(1- ((al)*(al))))))
		alpha = math.acos((1/(a*a + b*b)) * ((a*(r1+r2*math.cos(beta)))+ (b*r2*math.sqrt(1- ((math.cos(beta))*(math.cos(beta)))))))
		print "(a,b,X,Y,alpha,beta)",(a,b,centroid_x-centroid_x0,centroid_y-centroid_y0,alpha*(180/3.14),beta*(180/3.14) 	)
		
	except :
		print "Alpha/Beta calculation failed, division by zero probably."

	
	# Arduino server upload 
#	data ("alpha")	
#	data (alpha*(180/3.14))
#	data ("beta")
#	data (beta*(180/3.14))	
	
	
	 

	
	#print alpha*(180/3.14), beta*(180/3.14)
	
	print (centroid_x0,centroid_y0)
	
	
	cv2.imshow('Tracked',frame)
	
	
	k = cv2.waitKey(5)
	
	if k == 27:
		break
		
cv2.imwrite("Shoot.png",frame)
cap.release()
cv2.destroyAllWindows()
	
	
