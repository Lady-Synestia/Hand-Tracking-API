import asyncio
import json
import time

import cv2
import numpy as np
import mediapipe as mp
import math


def get_angle_3_points(point_a, point_b, point_c):
    """
    :param point_a: mediapipe hand landmark
    :param point_b: mediapipe hand landmark
    :param point_c: mediapipe hand landmark
    :return: angle at point_b, in degrees (yeah I could've just used radians but I value my sanity more than efficiency)
    """
    a = math.sqrt((point_c.x - point_b.x) ** 2 + (point_c.y - point_b.y) ** 2)
    b = math.sqrt((point_c.x - point_a.x) ** 2 + (point_c.y - point_a.y) ** 2)
    c = math.sqrt((point_b.x - point_a.x) ** 2 + (point_b.y - point_a.y) ** 2)

    return math.degrees(math.acos((a ** 2 + c ** 2 - b ** 2) / (2 * a * c)))


class Finger:
    def __init__(self, a, b, c, d, is_thumb=False, name=None, extended=None):
        """
        params a, b, c and d are all 3D vectors from HandLandmarkerResults
        :param a: finger mcp (thumb cmc)
        :param b: finger pip (thumb mcp)
        :param c: finger dip (thumb ip)
        :param d: finger tip (thumb tip)
        :param is_thumb: bool, is this a thumb or not
        :param name: used to differentiate different fingers
        """
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.is_thumb = is_thumb
        self.name = name
        self.extended = extended

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
            angle_a = get_angle_3_points(self.d, self.b, wrist)
            return angle_a > 90


class Gesture:
    """
    Class Gesture:

    Attributes
    ----------
    name : str
    orientation : str
    fingers : list[Finger,Finger,Finger,Finger,Finger]
    wrist : single mediapipe hand landmark

    Methods
    -------
    __init__(name, orientation, fingers, wrist = None):
        Constructor
    compare(other):
        Compares two gestures to each other
    get_orientation():
        Gets the orientation of the gesture if self.orientation is set to "unknown"
    """

    def __init__(self, name, orientation, fingers, wrist=None, handedness=None):
        """
        Class Gesture

        :param name: str, name of the gesture. set to "unknown" if this unset
        :param orientation: str, can be "up", "down", "left" or "right"
        :param fingers: list, must only contain objects of type Finger
        :param wrist: mediapipe hand landmark (landmarks[0])
        """
        self.name = name  # String containing the name of the gesture, e.g. "thumb up"
        self.orientation = orientation  # String containing the orientation of the hand to produce this gesture, e.g. "up", "down", "left", "right", "any"
        self.fingers = fingers  # List of fingers used to produce this gesture
        self.wrist = wrist
        self.handedness = handedness
        if self.wrist is not None:
            for finger in self.fingers:
                finger.extended = finger.is_extended(self.wrist)

    def compare(self, other):
        """compare(other)

        :param other: Gesture
        :return: True if the gestures match, False if they don't
        """
        if other.orientation == self.orientation or other.orientation == "any":
            for i in range(len(self.fingers)):
                if self.fingers[i].extended != other.fingers[i].extended:
                    return False
            return True
        else:
            return False

    def get_orientation(self):
        """

        :return: orientation: str, can be "up", "down", "left", or "right"
        """
        # We are only concerned about the position of the middle finger relative to the wrist
        if self.orientation == "unknown":
            a = self.fingers[2].a  # Middle finger position

            if abs(a.x - self.wrist.x) < abs(a.y - self.wrist.y):  # then we know the hand is pointing either up or down
                if a.y < self.wrist.y:  # middle finger is above the wrist
                    orientation = "up"
                else:
                    orientation = "down"
            else:  # then we know the hand is pointing either left or right
                if a.x > self.wrist.x:  # middle finger is to the right of the wrist
                    orientation = "right"
                else:
                    orientation = "left"

            return orientation
        else:
            return self.orientation


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

        self.gesture = Gesture("unknown", "unknown", [Finger(None, None, None, None, True, "thumb", False),
                                                      Finger(None, None, None, None, False, "index", False),
                                                      Finger(None, None, None, None, False, "middle", False),
                                                      Finger(None, None, None, None, False, "ring", False),
                                                      Finger(None, None, None, None, False, "pinky", False)], None,
                               None)
        self.left_gesture = self.gesture
        self.left_gesture.handedness = "Left"
        self.left_orientation = None
        self.right_orientation = None
        self.right_gesture = self.gesture
        self.right_gesture.handedness = "Right"
        self.rising_edge = False

        self.gestures = [Gesture("thumbs up", "left", [
            Finger(None, None, None, None, True, "thumb", True),
            Finger(None, None, None, None, False, "index", False),
            Finger(None, None, None, None, False, "middle", False),
            Finger(None, None, None, None, False, "ring", False),
            Finger(None, None, None, None, False, "pinky", False)]),
                         Gesture("thumbs up", "right", [
                             Finger(None, None, None, None, True, "thumb", True),
                             Finger(None, None, None, None, False, "index", False),
                             Finger(None, None, None, None, False, "middle", False),
                             Finger(None, None, None, None, False, "ring", False),
                             Finger(None, None, None, None, False, "pinky", False)]),
                         Gesture("fuck you", "up", [
                             Finger(None, None, None, None, True, "thumb", False),
                             Finger(None, None, None, None, False, "index", False),
                             Finger(None, None, None, None, False, "middle", True),
                             Finger(None, None, None, None, False, "ring", False),
                             Finger(None, None, None, None, False, "pinky", False)]),
                         Gesture("fist", "any", [
                             Finger(None, None, None, None, True, "thumb", False),
                             Finger(None, None, None, None, False, "index", False),
                             Finger(None, None, None, None, False, "middle", False),
                             Finger(None, None, None, None, False, "ring", False),
                             Finger(None, None, None, None, False, "pinky", False)]),
                         Gesture("open hand", "any", [
                             Finger(None, None, None, None, True, "thumb", True),
                             Finger(None, None, None, None, False, "index", True),
                             Finger(None, None, None, None, False, "middle", True),
                             Finger(None, None, None, None, False, "ring", True),
                             Finger(None, None, None, None, False, "pinky", True)]),
                         Gesture("metal", "up", [
                             Finger(None, None, None, None, True, "thumb", False),
                             Finger(None, None, None, None, False, "index", True),
                             Finger(None, None, None, None, False, "middle", False),
                             Finger(None, None, None, None, False, "ring", False),
                             Finger(None, None, None, None, False, "pinky", True)]),
                         Gesture("web shooter", "down", [
                             Finger(None, None, None, None, True, "thumb", False),
                             Finger(None, None, None, None, False, "index", True),
                             Finger(None, None, None, None, False, "middle", False),
                             Finger(None, None, None, None, False, "ring", False),
                             Finger(None, None, None, None, False, "pinky", True)]),
                         Gesture("erm ackshually", "up", [
                             Finger(None, None, None, None, True, "thumb", False),
                             Finger(None, None, None, None, False, "index", True),
                             Finger(None, None, None, None, False, "middle", False),
                             Finger(None, None, None, None, False, "ring", False),
                             Finger(None, None, None, None, False, "pinky", False)]),
                         Gesture("victory", "up", [
                             Finger(None, None, None, None, True, "thumb", False),
                             Finger(None, None, None, None, False, "index", True),
                             Finger(None, None, None, None, False, "middle", True),
                             Finger(None, None, None, None, False, "ring", False),
                             Finger(None, None, None, None, False, "pinky", False)]),
                         Gesture("number 3", "up", [
                             Finger(None, None, None, None, True, "thumb", False),
                             Finger(None, None, None, None, False, "index", True),
                             Finger(None, None, None, None, False, "middle", True),
                             Finger(None, None, None, None, False, "ring", True),
                             Finger(None, None, None, None, False, "pinky", False)]),
                         Gesture("ok", "up", [
                             Finger(None, None, None, None, True, "thumb", True),
                             Finger(None, None, None, None, False, "index", False),
                             Finger(None, None, None, None, False, "middle", True),
                             Finger(None, None, None, None, False, "ring", True),
                             Finger(None, None, None, None, False, "pinky", True)]),
                         Gesture("lmao gottem", "down", [
                             Finger(None, None, None, None, True, "thumb", False),
                             Finger(None, None, None, None, False, "index", False),
                             Finger(None, None, None, None, False, "middle", True),
                             Finger(None, None, None, None, False, "ring", True),
                             Finger(None, None, None, None, False, "pinky", True)]),
                         ]

    # Assuming `results.multi_hand_landmarks` is the list you're passing
    def convert_to_serializable(self,
                                landmark_list):  # Update this to your heart's content I won't touch this unless you want me to - will
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
            all_landmarks.append([hand_data])

        # Return the serialized JSON string of all landmarks
        return all_landmarks

    def detect_gestures(self, landmarks):
        hand = self.assemble_hand(landmarks)
        hand.orientation = hand.get_orientation()
        # print(hand.orientation)

        for gesture in self.gestures:
            if hand.compare(gesture):
                hand.name = gesture.name

        return hand

    def assemble_hand(self, landmarks):
        wrist = landmarks[0]
        f_thumb = Finger(landmarks[1], landmarks[2], landmarks[3], landmarks[4], wrist, True)
        f_index = Finger(landmarks[5], landmarks[6], landmarks[7], landmarks[8], wrist)
        f_middle = Finger(landmarks[9], landmarks[10], landmarks[11], landmarks[12], wrist)
        f_ring = Finger(landmarks[13], landmarks[14], landmarks[15], landmarks[16], wrist)
        f_pinky = Finger(landmarks[17], landmarks[18], landmarks[19], landmarks[20], wrist)

        hand = Gesture("unknown", "unknown", [f_thumb, f_index, f_middle, f_ring, f_pinky],
                       wrist)  # The current gesture that we want to check against the list of gestures

        return hand

    async def mainloop(self, websocket_client, tracking_interval=0.1):
        last_processed_time = time.time()  # Track the last processed frame time

        with self.hands:
            while self.rval:
                current_time = time.time()
                if current_time - last_processed_time >= tracking_interval:
                    last_processed_time = current_time  # Update the time of the last processed frame

                    image_flipped = cv2.flip(self.frame, 1)
                    image_flipped.flags.writeable = False
                    image_flipped = cv2.cvtColor(image_flipped, cv2.COLOR_BGR2RGB)
                    results = self.hands.process(image_flipped)

                    image_flipped.flags.writeable = True
                    image_flipped = cv2.cvtColor(image_flipped, cv2.COLOR_RGB2BGR)
                    if results.multi_hand_landmarks and results.multi_handedness:
                        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                            self.mp_drawing.draw_landmarks(
                                image_flipped,
                                hand_landmarks,
                                self.mp_hands.HAND_CONNECTIONS,
                                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                                self.mp_drawing_styles.get_default_hand_connections_style()
                            )
                            landmarks = hand_landmarks.landmark
                            self.gesture = self.detect_gestures(landmarks)
                            match handedness.classification[0].label:
                                case "Left":
                                    self.left_gesture = self.gesture
                                    self.left_orientation = self.gesture.orientation if self.gesture.orientation is not None else "unknown"
                                    image_flipped = cv2.putText(image_flipped, self.left_gesture.name, (50, 50),
                                                                self.font,
                                                                1, (255, 0, 255),
                                                                2, cv2.LINE_AA)
                                case "Right":
                                    self.right_gesture = self.gesture
                                    self.right_orientation = self.gesture.orientation if self.gesture.orientation is not None else "unknown"

                                    image_flipped = cv2.putText(image_flipped, self.right_gesture.name, (400, 50),
                                                                self.font, 1,
                                                                (255, 0, 255),
                                                                2, cv2.LINE_AA)

                        # at this point we have all the correct data to send across the api
                        # it will be added into an array and sent so that it can be handled

                        #
                        # print(self.left_gesture.name)
                        # print(self.right_gesture.name)
                        # print(self.left_orientation)
                        # print(self.right_orientation)

                        self.left_orientation = "unknown" if self.left_orientation is None else self.left_orientation
                        self.right_orientation = "unknown" if self.right_orientation is None else self.right_orientation

                        dictNotJson = self.convert_to_serializable(results.multi_hand_landmarks)

                        data = [
                            [self.left_orientation, self.right_orientation],  # Value 1: Left and Right orientation
                            dictNotJson,  # Value 2: Tracking Points
                            [self.left_gesture.name, self.right_gesture.name]  # Value 3: Gestures
                        ]
                        websocket_client.send_message(json.dumps(data))

                    cv2.imshow("preview", image_flipped)

                self.rval, self.frame = self.vc.read()
                key = cv2.waitKey(20)
                if key == 27:  # exit on ESC
                    break

        cv2.destroyWindow("preview")
        self.vc.release()


async def main(websocket_client):
    # this like initialises the camera and stuff. U can change the camera index it uses in here
    handTrackManager = HandTrackingMain()

    # this does the actual tracking and the tracking interval is the delay between tracking frames. I think 0.01 is min
    tracking_interval = 0.1
    await handTrackManager.mainloop(websocket_client, tracking_interval)
