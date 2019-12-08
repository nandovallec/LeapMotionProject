import this
from math import atan2

import numpy as np
import Leap, sys, thread, time
from math import acos
from Tkinter import *
from PIL import ImageTk, Image
import random

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
        interaction_box = frame.interaction_box
        hands = frame.hands
        global cursor_right_X, cursor_right_Y, cursor_left_X, cursor_left_Y, right_hand_zoom, left_hand_zoom

        if(len(frame.hands) == 0):
            cursor_right_X = 0
            cursor_right_Y = 0
            cursor_left_X = 0
            cursor_left_Y = 0
            right_hand_zoom = False
            left_hand_zoom = False

        if(len(frame.hands) == 1):
            vec1 = hands[0].fingers[0].direction  # Thumb
            vec2 = hands[0].fingers[1].direction  # Index
            angle1 = acos(max(-1.0, min(1.0, vec1.dot(vec2))))
            leap_position = hands[0].palm_position
            leap_position.x *= .5
            leap_position.z *= 0.5

            right_hand_zoom = False
            left_hand_zoom = False

            normalized_point = interaction_box.normalize_point(leap_position, True)

            if(hands[0].is_right):
                cursor_right_X = normalized_point.x * 1100
                cursor_right_Y = normalized_point.z * 1000
            else:
                cursor_left_X = normalized_point.x * 1100
                cursor_left_Y = normalized_point.z * 1000
            #print "POS " + str(cursor_right_X) + "   " + str(cursor_right_Y)




        if(len(frame.hands) >= 2):


            #Move the cursors
            if(hands[0].is_left):
                left_hand = hands[0]
                right_hand = hands[1]
            else:
                left_hand = hands[1]
                right_hand = hands[0]

            leap_position_left = left_hand.palm_position
            leap_position_left.x *= .5
            leap_position_left.z *= 0.5

            leap_position_right = right_hand.palm_position
            leap_position_right.x *= .5
            leap_position_right.z *= 0.5

            normalized_point_right = interaction_box.normalize_point(leap_position_right, True)
            normalized_point_left = interaction_box.normalize_point(leap_position_left, True)

            cursor_left_X = normalized_point_left.x * 1100
            cursor_left_Y = normalized_point_left.z * 1000

            cursor_right_X = normalized_point_right.x * 1100
            cursor_right_Y = normalized_point_right.z * 1000

            print str(cursor_right_X) + "           " + str(cursor_left_X)

            # Let's check if both hands have only the thumb and index extended

            two_up_left = True
            two_up_right = True
            for i in range(0, 1):
                two_up_left = two_up_left and left_hand.fingers[i].is_extended
                two_up_right = two_up_right and right_hand.fingers[i].is_extended

            for i in range(2, 4):
                two_up_left = two_up_left and not left_hand.fingers[i].is_extended
                two_up_right = two_up_right and not right_hand.fingers[i].is_extended

            left_hand_zoom = two_up_left
            right_hand_zoom = two_up_right

            if two_up_left and two_up_right:
                vec1 = left_hand.fingers[0].direction    # Thumb
                vec2 = left_hand.fingers[1].direction    # Index
                #angle1 = vec1.angle_to(vec2) * Leap.RAD_TO_DEG             # Angle
                angle1 = acos(max(-1.0, min(1.0, vec1.dot(vec2))))* Leap.RAD_TO_DEG

                vec1 = right_hand.fingers[0].direction    # Thumb
                vec2 = right_hand.fingers[1].direction    # Index
                #angle2 = vec1.angle_to(vec2) * Leap.RAD_TO_DEG          # Angle
                angle2 = acos(max(-1.0, min(1.0, vec1.dot(vec2))))* Leap.RAD_TO_DEG


                #print angle1 * Leap.RAD_TO_DEG
                # if(angle1 > 0.75):
                #     print "FIRST  " + str(angle1) + "     " + str(angle2)
                # if(angle2 > 0.75):
                #     print "SECOND" + str(angle1) + "     " + str(angle2)

                if(angle1 > 60 and angle2 > 60):
                    print "BOTH " + str(hands[0].stabilized_palm_position) + "   " + str(hands[1].stabilized_palm_position)
                    print "Distance: " + str(hands[0].stabilized_palm_position.distance_to(hands[1].stabilized_palm_position))


root = Tk()
root.title("lol")
x, y = str(400), str(0)
loc = "1100x1000+" + x + '+' + y
root.geometry(loc)

photo = ImageTk.PhotoImage(Image.open("example.jpg"))
label = Label(root, image=photo)
label.place(x=0, y=0)


photo2 = ImageTk.PhotoImage(Image.open("cursorR.png").resize((50,50)))
photo2_zoom = ImageTk.PhotoImage(Image.open("cursorZR.png").resize((50,50)))
lab_right = Label(root, image=photo2)
lab_right.place(x=0, y=0)

photo3 = ImageTk.PhotoImage(Image.open("cursorL.png").resize((50,50)))
photo3_zoom = ImageTk.PhotoImage(Image.open("cursorZL.png").resize((50,50)))
lab_left = Label(root, image=photo3)
lab_left.place(x=0, y=0)


cursor_right_X = 0
cursor_right_Y = 0

cursor_left_X = 0
cursor_left_Y = 0

left_hand_zoom = False
right_hand_zoom = False

image_X = 400
image_Y = 400

def move_me():
    global cursor_right_X, cursor_right_Y,cursor_left_X, cursor_left_Y, image_X, image_Y, label,e

    label.place(x=image_X, y=image_Y)
    if cursor_right_X == 0 and cursor_right_Y == 0:
        cursor_right_X = -100
        cursor_right_Y = -100
    if cursor_left_X == 0 and cursor_left_Y == 0:
        cursor_left_X = -100
        cursor_left_Y = -100
    lab_right.place(x=cursor_right_X, y=cursor_right_Y)
    lab_left.place(x=cursor_left_X, y=cursor_left_Y)

    if not move_me.loaded_left_zoom and left_hand_zoom:
        lab_left.configure(image=photo3_zoom)
        lab_left.image=photo3_zoom
        move_me.loaded_left_zoom = True

    if not move_me.loaded_right_zoom and right_hand_zoom:
        lab_right.configure(image=photo2_zoom)
        lab_right.image = photo2_zoom
        move_me.loaded_right_zoom = True

    if move_me.loaded_left_zoom and not left_hand_zoom:
        lab_left.configure(image=photo3)
        lab_left.image=photo3
        move_me.loaded_left_zoom = False

    if move_me.loaded_right_zoom and not right_hand_zoom:
        lab_right.configure(image=photo2)
        lab_right.image = photo2
        move_me.loaded_right_zoom = False


    root.after(50, move_me)
    root["bg"] = "yellow"

move_me.loaded_left_zoom = False
move_me.loaded_right_zoom = False

def main():
    listener = LeapMotionListener()
    controller = Leap.Controller()

    controller.add_listener(listener)



    move_me()
    root.mainloop()

    print "Enter to finish"
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()