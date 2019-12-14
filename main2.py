import this
from math import atan2

import numpy as np
import Leap, sys, thread, time
from math import acos

from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture


class LeapMotionListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(selfself, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Leap Device Connected"

        # We need the semicolons at the end, don't know why

        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(selfself, controller):
        print "Leap Device Disconnected"

    def on_exit(self, controller):
        print "Finalized"

    # # Main method
    # def on_frame(selfself, controller):
    #     frame = controller.frame()
    #
    #     # print "Frame ID: " + str(frame.id) + " nHand " + str(len(frame.hands)) + " nTool " + str(len(frame.tools)) + " nGest " + str(len(frame.gestures()))
    #
    #     for hand in frame.hands:
    #         handType = "Lefty" if hand.is_left else "Righty"
    #         #
    #         # print handType + " ID: " + str(hand.id) + " Pos: " + str(hand.palm_position)
    #
    #         # normal = hand.palm_normal
    #         # direction = hand.direction
    #         #
    #         # print "Normal: " + str(normal) + "   Direction: " + str(direction)
    #         # print "Pitch: " + str(direction.pitch * Leap.RAD_TO_DEG) + " Roll: " + str(normal.roll * Leap.RAD_TO_DEG) + " Yaw: " + str(direction.yaw * Leap.RAD_TO_DEG)
    #
    #
    #         if not two_up:
    #             print "BIEN " + str(handType)
    #         # for finger in hand.fingers:
    #         #
    #         #     print "Type: " + selfself.finger_names[finger.type] + "  Extended: " + str(finger.is_extended)
    #
    #             # for b in range(0, 4):
    #             #     bone = finger.bone(b)
    #             #     print "Bone: " + selfself.bone_names[bone.type] + " Dir: " + str(bone.direction)
    #         # print "Thumb Dir" + str(hand.fingers[0].direction)
    #         # print "Index Dir" + str(hand.fingers[1].direction)
    #         #print abs(hand.fingers[0].direction[0]- hand.fingers[1].direction[0])
    #         vec1 = hand.fingers[0].direction
    #         vec2 = hand.fingers[1].direction
    #         angle = vec1.angle_to(vec2)
    #         # Maybe check it for X frames before start zooming
    #         # print "Angle: " + str(angle * Leap.RAD_TO_DEG)
    #
    #         # The closer to 1 the closer the hand into a fist
    #
    #         strength = hand.grab_strength
    #         # print "Strength: " + str(strength)
    #
    #         #if(abs(hand.fingers[0].direction[0]- hand.fingers[1].direction[0]) > 0.8):
    #         # if(angle* Leap.RAD_TO_DEG > 72):
    #         #     print "SIGN " + str(handType)

    # # Main method
    def on_frame(selfself, controller):
        frame = controller.frame()
        hands = frame.hands

        if (len(frame.hands) == 1):
            vec1 = hands[0].fingers[0].direction  # Thumb
            vec2 = hands[0].fingers[1].direction  # Index
            angle1 = acos(max(-1.0, min(1.0, vec1.dot(vec2))))
            print angle1 * Leap.RAD_TO_DEG

        if (len(frame.hands) >= 2):

            # Let's check if both hands have only the thumb and index extended

            two_up = False
            for i in range(0, 1):
                two_up = two_up or not hands[0].fingers[i].is_extended
            for i in range(2, 4):
                two_up = two_up or hands[0].fingers[i].is_extended
            for i in range(0, 1):
                two_up = two_up or not hands[1].fingers[i].is_extended
            for i in range(2, 4):
                two_up = two_up or hands[1].fingers[i].is_extended

            if not two_up:
                vec1 = hands[0].fingers[0].direction  # Thumb
                vec2 = hands[0].fingers[1].direction  # Index
                # angle1 = vec1.angle_to(vec2) * Leap.RAD_TO_DEG             # Angle
                angle1 = acos(max(-1.0, min(1.0, vec1.dot(vec2)))) * Leap.RAD_TO_DEG

                vec1 = hands[1].fingers[0].direction  # Thumb
                vec2 = hands[1].fingers[1].direction  # Index
                # angle2 = vec1.angle_to(vec2) * Leap.RAD_TO_DEG          # Angle
                angle2 = acos(max(-1.0, min(1.0, vec1.dot(vec2)))) * Leap.RAD_TO_DEG

                # print angle1 * Leap.RAD_TO_DEG
                # if(angle1 > 0.75):
                #     print "FIRST  " + str(angle1) + "     " + str(angle2)
                # if(angle2 > 0.75):
                #     print "SECOND" + str(angle1) + "     " + str(angle2)

                if (angle1 > 60 and angle2 > 60):
                    print "BOTH " + str(hands[0].stabilized_palm_position) + "   " + str(
                        hands[1].stabilized_palm_position)
                    print "Distance: " + str(
                        hands[0].stabilized_palm_position.distance_to(hands[1].stabilized_palm_position))


def main():
    listener = LeapMotionListener()
    controller = Leap.Controller()

    controller.add_listener(listener)

    print "Enter to finish"
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()