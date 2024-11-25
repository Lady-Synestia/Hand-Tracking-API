import cv2
import numpy as np
import mediapipe as mp

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
    np_frame = np.asarray(frame)
    FRAME_DIMENSIONS = np_frame.shape
else:
    rval = False

def flip_image(array,axis = "y"):
    array_x = array.shape[0]
    array_y = array.shape[1]
    if axis == "x":
        return array[::-1]
    else:
        array = array[::-1]
        rotated_array = array[::-1,::-1]
        return rotated_array

def invert_colours(array):
    return np.invert(array)

def overlayTwoArrays(array1,array2):
    return np.bitwise_and(array1,array2)

image_is_reversed = False
previous_frame = flip_image(np_frame)

while rval:
    np_frame = np.asarray(frame)
    reversed_np_frame = flip_image(np_frame,"y")
    
    reversed_np_frame = overlayTwoArrays(flip_image(np_frame),previous_frame)
    cv2.imshow("preview",reversed_np_frame)
    previous_frame = flip_image(np_frame)
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

cv2.destroyWindow("preview")
vc.release()