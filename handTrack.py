# This module will need to be restructured to work with the flask api
import cv2
import numpy as np
import mediapipe as mp

# Initialise mediapipe's hand tracking solution
mp_drawing = mp.solutions.drawing_utils # so we can draw the hand landmarks onto the frame
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Create a window for the camera feed called "preview"
cv2.namedWindow("preview")
# Start capturing from the default camera
vc = cv2.VideoCapture(0)

font = cv2.FONT_HERSHEY_SIMPLEX


if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
    np_frame = np.asarray(frame)
else:
    rval = False

def flip_image(array,axis = "y"):
    array_x = array.shape[0]
    array_y = array.shape[1]
    if axis == "x":
        return array[::-1] # Reverses the whole array
    else:
        array = array[::-1]
        rotated_array = array[::-1,::-1]# Reverses rows and columns of the array
        return rotated_array

def invert_colours(array): # This has no practical purpose at the moment
    return np.invert(array)

def overlayTwoArrays(array1,array2): # This has no practical purpose at the moment
    return np.bitwise_and(array1,array2)

image_is_reversed = False

def detect_gestures(landmarks):
    """
    Detect what hand gestures are being shown
    """
    ...

with hands:
    while rval:
        np_frame = np.asarray(frame)
        image_flipped = flip_image(np_frame) # Mirror the image. This makes it easier to control
        #                                          where you are putting your hand as people are more 
        #                                          used to looking in mirrors than at cameras.
        #                                          We want to input this image into mediapipe.

        image_flipped.flags.writeable = False
        image_flipped = cv2.cvtColor(image_flipped, cv2.COLOR_BGR2RGB)
        results = hands.process(image_flipped)# Get hand tracking data for that frame

        image_flipped.flags.writeable = True
        image_flipped = cv2.cvtColor(image_flipped, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image_flipped,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
        
        image_flipped = cv2.putText(image_flipped, 'OpenCV', (50,50), font, 1, (255,128,0), 2, cv2.LINE_AA)
        
        cv2.imshow("preview",image_flipped)
        rval, frame = vc.read()
        key = cv2.waitKey(20)
        if key == 27: # exit on ESC
            break
cv2.destroyWindow("preview")
vc.release()