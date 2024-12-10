# This module will need to be restructured to work with the flask api
import asyncio
import json

import cv2
import numpy as np
import mediapipe as mp
import math

from app.utils.Sockets.SocketSend import send_message

def get_angle_3_points(point_a, point_b, point_c):
    a = math.sqrt((point_c.x - point_b.x) ** 2 + (point_c.y - point_b.y) ** 2)
    b = math.sqrt((point_c.x - point_a.x) ** 2 + (point_c.y - point_a.y) ** 2)
    c = math.sqrt((point_b.x - point_a.x) ** 2 + (point_b.y - point_a.y) ** 2)

    return math.degrees(math.acos((a ** 2 + c ** 2 - b ** 2) / (2 * a * c)))

class Finger:
    def __init__(self, a, b, c, d, is_thumb):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.is_thumb = is_thumb

    def is_extended(self, wrist):
        """
        Returns True if the selected digit is extended

        finger_tip, finger_mcp, and wrist all have x, y, and z attributes
        """
        if self.is_thumb:
            angle_1 = get_angle_3_points(wrist, self.a, self.b)  # Angle at THUMB_CMC, landmarks[1]
            angle_2 = get_angle_3_points(self.a, self.b, self.c)  # Angle at THUMB_MCP, landmarks[2]
            angle_3 = get_angle_3_points(self.b, self.c, self.d)  # Angle at THUMB_IP, landmarks[3]
            threshold = 160  # If any of the angles are below this number, the thumb is bent and therefore not extended fully (can be adjusted if it's too sensitive or not enough)
            return angle_1 >= threshold and angle_2 >= threshold and angle_3 >= threshold  # Return True if all angles are above the threshold
        else:
            angle_a = get_angle_3_points(self.d, self.a, wrist)
            return angle_a > 90

class Gesture:
    def __init__(self, name, orientation, fingers):
        self.name = name # String containing the name of the gesture, e.g. "thumb up"
        self.orientation = orientation # String containing the orientation of the hand to produce this gesture, e.g. "up", "down", "left", "right", "any"
        self.fingers = fingers # Which fingers+thumbs are being held up to produce this gesture

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

            # * using a dictionary so points can have keys
            hand_data = {}

            for index, landmark in enumerate(hand_landmarks.landmark):
                # Add each landmark's x, y, z values as a dictionary
                hand_data["point" + str(index)] = {
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z
                }

            # Append the landmarks for this hand to the overall list
            all_landmarks.append(hand_data)

        # Return the serialized JSON string of all landmarks
        return json.dumps(all_landmarks[0])  # ! only sending first hand for testing purposes

    def mainloop(self):
        with self.hands:
            while self.rval:
                image_flipped = cv2.flip(self.frame, 1)  # Mirror the image. This makes it easier to control
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
                        image_flipped = cv2.putText(image_flipped, "Thumb up", (50, 50), self.font, 1, (255, 0, 255), 2,
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

    def get_angle_3_points(self, point_a,point_b,point_c):
        a = math.sqrt((point_c.x-point_b.x)**2+(point_c.y-point_b.y)**2)
        b = math.sqrt((point_c.x-point_a.x)**2+(point_c.y-point_a.y)**2)
        c = math.sqrt((point_b.x-point_a.x)**2+(point_b.y-point_a.y)**2)

        return math.degrees(math.acos((a**2+c**2-b**2)/(2*a*c)))

    def is_extended(self, tip, mcp, wrist, is_thumb = False, thumb_cmc = None, thumb_ip = None):
        """
        Returns True if the selected digit is extended
        
        finger_tip, finger_mcp, and wrist all have x, y, and z attributes
        """
        if is_thumb:
            angle_1 = self.get_angle_3_points(wrist, thumb_cmc, mcp) # Angle at THUMB_CMC, landmarks[1]
            angle_2 = self.get_angle_3_points(thumb_cmc, mcp, thumb_ip) # Angle at THUMB_MCP, landmarks[2]
            angle_3 = self.get_angle_3_points(mcp, thumb_ip, tip) # Angle at THUMB_IP, landmarks[3]
            threshold = 135 # If any of the angles are below this number, the thumb is bent and therefore not extended fully (can be adjusted if it's too sensitive or not enough)
            return angle_1 >= threshold and angle_2 >= threshold and angle_3 >= threshold # Return True if all angles are above the threshold
        else:
            angle_a = self.get_angle_3_points(tip,mcp,wrist)
            return angle_a > 90
    
    def detect_gestures(self, landmarks):
        """
        Detect what hand gestures are being shown
        """
        wrist = landmarks[0]
        f_thumb = Finger(landmarks[1],landmarks[2],landmarks[3],landmarks[4], True).is_extended(wrist)
        f_index = Finger(landmarks[5],landmarks[6],landmarks[7],landmarks[8], False).is_extended(wrist)
        f_middle = Finger(landmarks[9],landmarks[10],landmarks[11],landmarks[12], False).is_extended(wrist)
        f_ring = Finger(landmarks[13],landmarks[14],landmarks[15],landmarks[16], False).is_extended(wrist)
        f_pinky = Finger(landmarks[17],landmarks[18],landmarks[19],landmarks[20], False).is_extended(wrist)

        hand = [wrist, f_thumb, f_index, f_middle, f_ring, f_pinky]

        #if f_middle.is_extended(wrist) and not (f_thumb.is_extended(wrist) or f_index.is_extended(wrist) or f_ring.is_extended(wrist) or f_pinky.is_extended(wrist)):
        if f_thumb and not (f_index or f_middle or f_ring or f_pinky):
            return True
        else:
            return False


def main():
    handTrackManager = HandTrackingMain()
    handTrackManager.mainloop()


if __name__ == '__main__':
    main()
