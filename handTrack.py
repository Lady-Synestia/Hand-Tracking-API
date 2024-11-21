import cv2
import numpy as np
import mediapipe

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
    for i in range(len(array)):
        red = array[i][0]
        green = array[i][1]
        blue = array[i][2]

        red = 255-red
        green = 255-green
        blue = 255-blue

        array[i][0] = red
        array[i][1] = green
        array[i][2] = blue
    return array

def overlayTwoArrays(array1,array2):
    arr = array1
    for i in range(len(array1)):
        for j in range(len(array1[i])):
            array1[i][j][0] = (array1[i][j][0]+array2[i][j][0])//2
            array1[i][j][1] = (array1[i][j][1]+array2[i][j][1])//2
            array1[i][j][2] = (array1[i][j][2]+array2[i][j][2])//2
    return arr

image_is_reversed = False

while rval:
    np_frame = np.asarray(frame)
    reversed_np_frame = flip_image(np_frame,"y")
    image_is_reversed = not image_is_reversed
    cv2.imshow("preview",overlayTwoArrays(np_frame,reversed_np_frame))
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

cv2.destroyWindow("preview")
vc.release()