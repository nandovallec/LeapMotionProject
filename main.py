import Leap, sys, thread, time
from math import acos
from Tkinter import *
from PIL import ImageTk, Image
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture


class LeapMotionListener(Leap.Listener):

    def on_init(selfself, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Leap Device Connected"

        # We need the semicolons at the end
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(selfself, controller):
        print "Leap Device Disconnected"

    def on_exit(self, controller):
        print "Finalized"

    # # Main method
    # I decided to not create auxiliary functions to speed up the process.
    # Usually it wouldn't be a problem but this particular function is called constantly and we are trying
    # to give the user a real-time experience.

    def on_frame(selfself, controller):
        frame = controller.frame()                      # Actual frame
        interaction_box = frame.interaction_box         # Interaction box in top of the device
        hands = frame.hands                             # Vector with the hands present in the frame

        # Global variables that we are using
        global cursor_right_X, cursor_right_Y, cursor_left_X, cursor_left_Y,\
            right_hand_zoom, left_hand_zoom, new_width, resizing, positioning, \
            image_pos_X, image_pos_Y, hand_origin_X, hand_origin_Y, \
            resetting, swiping

        # To improve the readability of the code, I will separate the 3 different paths that each frame
        #   is going to take according to the number of hands in the frame (0 hands, 1 hand, 2 or more hands)
        ################################################################################################################
        ################################################################################################################

        # If there is no hands in the frame, we can reset the variables
        if(len(frame.hands) == 0):
            cursor_right_X = 0
            cursor_right_Y = 0
            cursor_left_X = 0
            cursor_left_Y = 0
            right_hand_zoom = False
            left_hand_zoom = False
            resizing = False

        ################################################################################################################
        ################################################################################################################

        # If there is one hand in the frame
        if(len(frame.hands) == 1):
            leap_position = hands[0].palm_position          # We get the position of the palm
            resizing = False
            # Since the interaction box could be quite small, a solution proposed by the developers is to
            # reduce the position of the hands to decrease sensibility. Doing this, we will increase
            # the range that we can normalize.
            leap_position.x *= .5
            leap_position.z *= 0.5

            # We cannot zoom with one hand, so in case that we were zooming before, we reset the variables
            right_hand_zoom = False
            left_hand_zoom = False

            # We get the normalized position of the hand
            normalized_point = interaction_box.normalize_point(leap_position, True)

            # Update the position of the cursor
            if(hands[0].is_right):
                cursor_right_X = normalized_point.x * 1150 - 50
                cursor_right_Y = normalized_point.z * 1000
                cursor_left_X = 0
                cursor_left_Y = 0
            else:
                cursor_left_X = normalized_point.x * 1150 - 50
                cursor_left_Y = normalized_point.z * 1000
                cursor_right_X = 0
                cursor_right_Y = 0

            # Now that we have updated the position of the cursor, we will check there are any special gestures

            cursor_x = cursor_right_X if cursor_left_X == 0 else cursor_left_X
            cursor_y = cursor_right_Y if cursor_left_Y == 0 else cursor_left_Y

            # We create variable to control the state of the hand and set them appropriately
            closed_hand = True          # For grabbing
            open_hand = True            # For swiping
            for finger in hands[0].fingers:
                closed_hand = closed_hand and not finger.is_extended
                open_hand = open_hand and finger.is_extended

            # If the hand is close
            if (closed_hand and hands[0].grab_strength == 1.0):
                # Check if we were positioning already or we are starting
                if(not positioning):
                    # Check if the cursor is positioned over the photo
                    inside_range_x = image_pos_X - new_width/2 +25 <= cursor_x <= image_pos_X + new_width/2 -25
                    inside_range_y = image_pos_Y - new_height/2 +25 <= cursor_y <= image_pos_Y + new_height/2 -25

                if(cursor_x != -100 and cursor_y != -100 and label.place_info() != {}):     # Check is not an abnormal case and that the photo is loaded

                    if(positioning or (inside_range_x and inside_range_y)):     # Check if we can position or were already

                        if hand_origin_X == -100 and hand_origin_Y == -100:     # If we are starting to position
                            hand_origin_X = cursor_x
                            hand_origin_Y = cursor_y
                            positioning = True
                        else:                                                   # If we were positioning already
                            image_pos_X = image_pos_X + ((cursor_x - hand_origin_X) if cursor_x - hand_origin_X < 15 else 15)
                            image_pos_Y = image_pos_Y + ((cursor_y - hand_origin_Y) if cursor_y - hand_origin_Y < 15 else 15)
                            hand_origin_X = cursor_x
                            hand_origin_Y = cursor_y

                else:
                    # If photo is not loaded, we check the position of the cursor and load the photo
                    if (cursor_x >= 1100.0 * .75) and (cursor_y <= 1000.0 * .2):
                        resetting = True

            # If the hand is not closed we reset the positioning variables
            else:
                positioning = False
                hand_origin_X = -100
                hand_origin_Y = -100

            # If the user is doing some gestures
            if (len(frame.gestures()) != 0):
                # Check if the hand is completely open and the gesture is swiping
                if open_hand and (frame.gestures()[0].type == Leap.Gesture.TYPE_SWIPE):
                    swipe = SwipeGesture(frame.gestures()[0])
                    # Check that the main direction of the swipe is the x-axis (left or right)
                    if(abs (swipe.direction[0]) > 0.7):
                        swiping = True

        ################################################################################################################
        ################################################################################################################

        # If there are two or more hands in the frame
        # We decided two or more in case that the device detects a
        # sudden movement from someone else. We can assume that the
        # two hands that it's going to detect first are the owner's

        if(len(frame.hands) >= 2 ):

            # We detect the left and right hands
            if(hands[0].is_left):
                left_hand = hands[0]
                right_hand = hands[1]
            else:
                left_hand = hands[1]
                right_hand = hands[0]

            # Calculate the positions
            leap_position_left = left_hand.palm_position
            leap_position_left.x *= .5
            leap_position_left.z *= 0.5

            leap_position_right = right_hand.palm_position
            leap_position_right.x *= .5
            leap_position_right.z *= 0.5

            # Normalize the points
            normalized_point_right = interaction_box.normalize_point(leap_position_right, True)
            normalized_point_left = interaction_box.normalize_point(leap_position_left, True)

            # Move the cursors to their new positions
            cursor_left_X = normalized_point_left.x * 1150 - 50
            cursor_left_Y = normalized_point_left.z * 1000

            cursor_right_X = normalized_point_right.x * 1150 - 50
            cursor_right_Y = normalized_point_right.z * 1000

            # Now that we have updated the position of the cursor, we will check there are any special gestures (zoom)
            ################################################################################################

            # Let's check if both hands have only the thumb and index extended
            two_up_left = True
            two_up_right = True
            for i in range(0, 2):
                two_up_left = two_up_left and left_hand.fingers[i].is_extended
                two_up_right = two_up_right and right_hand.fingers[i].is_extended

            for i in range(2, 5):
                two_up_left = two_up_left and not left_hand.fingers[i].is_extended
                two_up_right = two_up_right and not right_hand.fingers[i].is_extended

            # Set the minimum angle between thumb and index to be considered zooming
            threshold_angle = 40

            # If they have the left index and thumb extended, we calculate the angle
            if two_up_left:
                vec1 = left_hand.fingers[0].direction    # Thumb
                vec2 = left_hand.fingers[1].direction    # Index
                angle1 = acos(max(-1.0, min(1.0, vec1.dot(vec2)))) * Leap.RAD_TO_DEG

                # Check if the angle is open enough
                if (angle1 > threshold_angle):
                    left_hand_zoom = True
                else:
                    left_hand_zoom = False
            else:
                left_hand_zoom = False

            # If they have the right index and thumb extended, we calculate the angle
            if two_up_right:
                vec1 = right_hand.fingers[0].direction    # Thumb
                vec2 = right_hand.fingers[1].direction    # Index
                angle2 = acos(max(-1.0, min(1.0, vec1.dot(vec2)))) * Leap.RAD_TO_DEG

                # Check if the angle is open enough
                if (angle2 > threshold_angle):
                    right_hand_zoom = True
                else:
                    right_hand_zoom = False
            else:
                right_hand_zoom = False

            # If both hands have only those fingers up we can proceed
            if two_up_left and two_up_right:
                # If the angle of the hands is over the threshold we start to resize
                if(angle1 > threshold_angle and angle2 > threshold_angle):
                    # The new width of the image will be the distance between the two hands in the X axis
                    new_width = abs(cursor_right_X - cursor_left_X)
                    resizing = True
                else:
                    resizing = False

        ################################################################################################################
        ################################################################################################################

# Create the global variables that we will be using
########################################################################################################################
# We create a window where we will be showing the process
root = Tk()
root.title("Leap Motion")
x, y = str(400), str(0)                 # Location on the screen
loc = "1100x1000+" + x + '+' + y        # Size (+ location)
root.geometry(loc)                      # Set the values

# Set the background image
background_photo = ImageTk.PhotoImage(Image.open("background.png"))
background_label = Label(root, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# We start with the initial picture and make a copy that we will resize
photo = ImageTk.PhotoImage(Image.open("MainPic.jpg"))
res_photo = photo
ori_width, ori_height = Image.open("MainPic.jpg").size      # Original sizes
new_width, new_height = ori_width, ori_height               # New sizes
label = Label(root, image=photo)                            # We create a label with the picture and assign it
label.place(x=550 - (new_width / 2), y=500 - (new_height / 2))  # Place it in the middle of the window


# We create the label that will hold the right cursor (normal and zoom)
photo2 = ImageTk.PhotoImage(Image.open("cursorR.png").resize((50,50)))
photo2_zoom = ImageTk.PhotoImage(Image.open("cursorZR.png").resize((50,50)))
lab_right = Label(root, image=photo2)
lab_right.place(x=-100, y=-100)

# We create the label that will hold the left cursor (normal and zoom)
photo3 = ImageTk.PhotoImage(Image.open("cursorL.png").resize((50,50)))
photo3_zoom = ImageTk.PhotoImage(Image.open("cursorZL.png").resize((50,50)))
lab_left = Label(root, image=photo3)
lab_left.place(x=-100, y=-100)

# These variables will keep the 2D coordinates of the right hand
cursor_right_X = -100
cursor_right_Y = -100

# These variables will keep the 2D coordinates of the left hand
cursor_left_X = -100
cursor_left_Y = -100

# These variables will keep if we are zooming with either hand
left_hand_zoom = False
right_hand_zoom = False

# This variable keeps track if we are doing any modifications to the photo
resizing = False
positioning = False
resetting = False
swiping = False

# The actual position of the image (the center)
image_pos_X = 550
image_pos_Y = 500

# Variables to control the movement while grabbing the photo
hand_origin_X = -100
hand_origin_Y = -100

########################################################################################################################


def move_me():
    global cursor_right_X, cursor_right_Y,cursor_left_X, cursor_left_Y, \
        image_pos_X, image_pos_Y, label, resizing, new_width, new_height,\
        res_photo, positioning, resetting, swiping

    # Set the position of the right cursor out of the screen if it is not necessary
    if cursor_right_X == 0 and cursor_right_Y == 0:
        cursor_right_X = -100
        cursor_right_Y = -100

    # Set the position of the left cursor out of the screen if it is not necessary
    if cursor_left_X == 0 and cursor_left_Y == 0:
        cursor_left_X = -100
        cursor_left_Y = -100

    # Set the cursors to their new position
    lab_right.place(x=cursor_right_X, y=cursor_right_Y)
    lab_left.place(x=cursor_left_X, y=cursor_left_Y)

    # Change the left cursor to the leftZoom cursor if it is not loaded
    if not move_me.loaded_left_zoom and left_hand_zoom:
        lab_left.configure(image=photo3_zoom)
        lab_left.image=photo3_zoom
        move_me.loaded_left_zoom = True

    # Change the right cursor to the rightZoom cursor if it is not loaded
    if not move_me.loaded_right_zoom and right_hand_zoom:
        lab_right.configure(image=photo2_zoom)
        lab_right.image = photo2_zoom
        move_me.loaded_right_zoom = True

    # Change the left cursor back to the original if we are not zooming
    if move_me.loaded_left_zoom and not left_hand_zoom:
        lab_left.configure(image=photo3)
        lab_left.image=photo3
        move_me.loaded_left_zoom = False

    # Change the right cursor back to the original if we are not zooming
    if move_me.loaded_right_zoom and not right_hand_zoom:
        lab_right.configure(image=photo2)
        lab_right.image = photo2
        move_me.loaded_right_zoom = False

    # Check if we need to resize the image
    if resizing:
        new_height = ori_height * (new_width/ori_width)             # Calculate the new height keeping the ratio

        if(new_width > 1.2*ori_width):    # If the zoom is over two times the original size, we load the detailed photo
            res_photo = ImageTk.PhotoImage( Image.open("detailedMainPic.jpg").resize((int(new_width), int(new_height))))  # Load the new resized photo
        else:
            res_photo = ImageTk.PhotoImage(Image.open("MainPic.jpg").resize((int(new_width), int(new_height))))     # Load the new resized photo

        label.place(x=image_pos_X-(new_width/2), y=image_pos_Y-(new_height/2))  # Keep the same center while resizing
        label.configure(image=res_photo)    # Load the new photo
        label.image = res_photo

    # Check if the photo need a change in position
    if positioning and label.place_info() != {}:
        label.place(x=image_pos_X-(new_width/2), y=image_pos_Y-(new_height/2))  # Change the position

    # If the user clicked, reset the photo to original settings or load it if it was not there
    if resetting:
        new_width, new_height = ori_width, ori_height  # Reset the sizes and position
        image_pos_X = 550
        image_pos_Y = 500

        res_photo = ImageTk.PhotoImage(
            Image.open("MainPic.jpg").resize((int(new_width), int(new_height))))  # Load the original photo
        label.place(x=image_pos_X - (new_width / 2),
                    y=image_pos_Y - (new_height / 2))  # Position it in the center
        label.configure(image=res_photo)  # Load the new photo
        label.image = res_photo

        resetting = False

    # Check for swiping and deletes the photo
    if swiping:
        label.place_forget()
        swiping = False

    root.after(50, move_me)     # Set the next time that this function is going to be called (in ms)


# In these variables we will keep if the cursor loaded at the moment is the original or the zoom one
move_me.loaded_left_zoom = False
move_me.loaded_right_zoom = False


def main():
    # We create the listener, the controller and associate them
    listener = LeapMotionListener()
    controller = Leap.Controller()

    controller.add_listener(listener)

    controller.config.set("Gesture.Swipe.MinVelocity", 1000000)

    # We create the window and start the looping method
    move_me()
    root.mainloop()

    # Exit method
    controller.remove_listener(listener)

if __name__ == "__main__":
    main()
