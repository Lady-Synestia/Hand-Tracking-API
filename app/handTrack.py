# This module will need to be restructured to work with the flask api
import cv2
import numpy as np
import mediapipe as mp
import math
import winsound

class HandTrackingMain:
    def __init__(self):
        # Initialise mediapipe's hand tracking solution
        self.mp_drawing = mp.solutions.drawing_utils # so we can draw the hand landmarks onto the frame
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)

        # Create a window for the camera feed called "preview"
        cv2.namedWindow("preview")
        # Start capturing from the default camera
        self.vc = cv2.VideoCapture(0)

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        if self.vc.isOpened(): # try to get the first frame
            self.rval, self.frame = self.vc.read()
            self.np_frame = np.asarray(self.frame)
        else:
            self.rval = False
        
        self.gesture = False
        self.rising_edge = False
    def mainloop(self):
        with self.hands:
            while self.rval:
                np_frame = np.asarray(self.frame)
                image_flipped = self.flip_image(np_frame) # Mirror the image. This makes it easier to control
                #                                          where you are putting your hand as people are more 
                #                                          used to looking in mirrors than at cameras.
                #                                          We want to input this image into mediapipe.

                image_flipped.flags.writeable = False
                image_flipped = cv2.cvtColor(image_flipped, cv2.COLOR_BGR2RGB)
                results = self.hands.process(image_flipped)# Get hand tracking data for that frame

                image_flipped.flags.writeable = True
                image_flipped = cv2.cvtColor(image_flipped, cv2.COLOR_RGB2BGR)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(
                            image_flipped,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.mp_drawing_styles.get_default_hand_connections_style()
                        )
                        landmarks = hand_landmarks.landmark
                        self.gesture = self.detect_gestures(landmarks)
                        
                    if self.gesture:
                        image_flipped = cv2.putText(image_flipped, "Fuck you", (50,50), self.font, 1, (255,0,255), 2, cv2.LINE_AA)
                        if not self.rising_edge:
                            self.rising_edge = True
                            winsound.PlaySound('D:\\Qwazor\'s Folder\\Documents\\Github\\Hand-Tracking-API\\app\\vine_boom.wav',winsound.SND_ASYNC)
                    else:
                        self.rising_edge = False
                
                cv2.imshow("preview",image_flipped)
                self.rval, self.frame = self.vc.read()
                key = cv2.waitKey(20)
                if key == 27: # exit on ESC
                    break

        cv2.destroyWindow("preview")
        self.vc.release()
    def flip_image(self,array,axis = "y"):
        array_x = array.shape[0]
        array_y = array.shape[1]
        if axis == "x":
            return array[::-1] # Reverses the whole array
        else:
            array = array[::-1]
            rotated_array = array[::-1,::-1]# Reverses rows and columns of the array
            return rotated_array
    def invert_colours(self,array): # This has no practical purpose at the moment
        return np.invert(array)

    def overlayTwoArrays(self,array1,array2): # This has no practical purpose at the moment
        return np.bitwise_and(array1,array2)

    def isExtended(self,finger_tip,finger_mcp,wrist):
        """
        Returns False if the finger tip is between the finger metacarpal and the wrist,
        otherwise it returns True
        
        finger_tip, finger_mcp, and wrist all have x, y, and z attributes
        """
        a = math.sqrt((wrist.x-finger_mcp.x)**2+(wrist.y-finger_mcp.y)**2)
        b = math.sqrt((wrist.x-finger_tip.x)**2+(wrist.y-finger_tip.y)**2)
        c = math.sqrt((finger_mcp.x-finger_tip.x)**2+(finger_mcp.y-finger_tip.y)**2)

        angle_A = math.degrees(math.acos((a**2+c**2-b**2)/(2*a*c)))
        return angle_A > 90
    def detect_gestures(self,landmarks):
        """
        Detect what hand gestures are being shown
        """
        wrist = landmarks[0]
        thumb_mcp = landmarks[2]
        thumb_tip = landmarks[4]
        index_mcp = landmarks[5]
        index_tip = landmarks[8]
        middle_mcp = landmarks[9]
        middle_tip = landmarks[12]
        ring_mcp = landmarks[13]
        ring_tip = landmarks[16]
        pinky_mcp = landmarks[17]
        pinky_tip = landmarks[20]
        if self.isExtended(middle_tip,middle_mcp,wrist) and not (self.isExtended(index_tip,index_mcp,wrist) or self.isExtended(ring_tip,ring_mcp,wrist) or self.isExtended(pinky_tip,pinky_mcp,wrist)):
            return True
        else:
            return False

if __name__ == '__main__':
    handTrackManager = HandTrackingMain()
    handTrackManager.mainloop()