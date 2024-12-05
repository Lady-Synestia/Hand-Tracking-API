# This module will need to be restructured to work with the flask api
import asyncio
import json

import cv2
import numpy as np
import mediapipe as mp
import math

from app.utils.Sockets.SocketSend import send_message


class HandTrackingMain:
    def __init__(self):
        # Initialise mediapipe's hand tracking solution
        self.mp_drawing = mp.solutions.drawing_utils  # so we can draw the hand landmarks onto the frame
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)

        # Create a window for the camera feed called "preview"
        cv2.namedWindow("preview")
        # Start capturing from the default camera
        self.vc = cv2.VideoCapture(0)

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        if self.vc.isOpened():  # try to get the first frame
            self.rval, self.frame = self.vc.read()
            self.np_frame = np.asarray(self.frame)
        else:
            self.rval = False

        self.gesture = False
        self.rising_edge = False

    # Assuming `results.multi_hand_landmarks` is the list you're passing
    def convert_to_serializable(self, landmark_list):
        all_landmarks = []  # List to store all landmarks for all hands

        for hand_landmarks in landmark_list:
            # Process landmarks for each hand
            hand_data = []  # List to store landmarks for this specific hand

            for landmark in hand_landmarks.landmark:
                # Append each landmark's x, y, z values as a dictionary
                hand_data.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z
                })

            # Append the landmarks for this hand to the overall list
            all_landmarks.append(hand_data)

        # Return the serialized JSON string of all landmarks
        return json.dumps(all_landmarks)

    def mainloop(self):
        with self.hands:
            while self.rval:
                np_frame = np.asarray(self.frame)
                image_flipped = self.flip_image(np_frame)  # Mirror the image. This makes it easier to control
                #                                          where you are putting your hand as people are more 
                #                                          used to looking in mirrors than at cameras.
                #                                          We want to input this image into mediapipe.

                image_flipped.flags.writeable = False
                image_flipped = cv2.cvtColor(image_flipped, cv2.COLOR_BGR2RGB)
                results = self.hands.process(image_flipped)  # Get hand tracking data for that frame

                image_flipped.flags.writeable = True
                image_flipped = cv2.cvtColor(image_flipped, cv2.COLOR_RGB2BGR)
                if results.multi_hand_landmarks:
                    # send the landmarks to the socket
                    dict = self.convert_to_serializable(results.multi_hand_landmarks)
                    asyncio.run(send_message(dict))
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
                        image_flipped = cv2.putText(image_flipped, "Fuck you", (50, 50), self.font, 1, (255, 0, 255), 2,
                                                    cv2.LINE_AA)
                        if not self.rising_edge:
                            self.rising_edge = True
                    else:
                        self.rising_edge = False

                cv2.imshow("preview", image_flipped)
                self.rval, self.frame = self.vc.read()
                key = cv2.waitKey(20)
                if key == 27:  # exit on ESC
                    break

        cv2.destroyWindow("preview")
        self.vc.release()

    def flip_image(self, array, axis="y"):
        array_x = array.shape[0]
        array_y = array.shape[1]
        if axis == "x":
            return array[::-1]  # Reverses the whole array
        else:
            array = array[::-1]
            rotated_array = array[::-1, ::-1]  # Reverses rows and columns of the array
            return rotated_array

    def invert_colours(self, array):  # This has no practical purpose at the moment
        return np.invert(array)

    def overlayTwoArrays(self, array1, array2):  # This has no practical purpose at the moment
        return np.bitwise_and(array1, array2)

    def getAngle3Points(self, point_a,point_b,point_c):
        a = math.sqrt((point_c.x-point_b.x)**2+(point_c.y-point_b.y)**2)
        b = math.sqrt((point_c.x-point_a.x)**2+(point_c.y-point_a.y)**2)
        c = math.sqrt((point_b.x-point_a.x)**2+(point_b.y-point_a.y)**2)

        return math.degrees(math.acos((a**2+c**2-b**2)/(2*a*c)))

    def isExtended(self,finger_tip,finger_mcp,wrist):
        """
        Returns False if the finger tip is between the finger metacarpal and the wrist,
        otherwise it returns True
        
        finger_tip, finger_mcp, and wrist all have x, y, and z attributes
        """
        angle_A = self.getAngle3Points(finger_tip,finger_mcp,wrist)
        return angle_A > 90
    
    def detect_gestures(self, landmarks):
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
        if self.isExtended(middle_tip, middle_mcp, wrist) and not (
                self.isExtended(index_tip, index_mcp, wrist) or self.isExtended(ring_tip, ring_mcp,
                                                                                wrist) or self.isExtended(pinky_tip,
                                                                                                          pinky_mcp,
                                                                                                          wrist)):
            return True
        else:
            return False


def main():
    handTrackManager = HandTrackingMain()
    handTrackManager.mainloop()


if __name__ == '__main__':
    main()
