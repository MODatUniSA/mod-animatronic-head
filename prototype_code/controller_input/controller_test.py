import pygame

import libs.input.xbox360_controller as xbox360_controller

pygame.init()
REFRESH_RATE = 20

my_controller = xbox360_controller.Controller(0)

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()

# Game Loop
done = False

while done==False:
    # Event processing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()

    print("Number of joysticks: {}".format(joystick_count) )

    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        print("\n\n===RAW PYGAME===")
        print("Joystick {}".format(i) )

        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()
        print("Joystick name: {}".format(name) )

        # Usually axis run in pairs, up/down for one, and left/right for the other.
        axes = joystick.get_numaxes()
        print("Number of axes: {}".format(axes) )


        for i in range( axes ):
            axis = joystick.get_axis( i )
            print("Axis {} value: {:>6.3f}".format(i, axis) )

        buttons = joystick.get_numbuttons()
        print("Number of buttons: {}".format(buttons) )


        for i in range( buttons ):
            button = joystick.get_button( i )
            print("Button {:>2} value: {}".format(i,button) )

        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in a tuple.
        hats = joystick.get_numhats()
        print("Number of hats: {}".format(hats) )


        for i in range( hats ):
            hat = joystick.get_hat( i )
            print("Hat {} value: {}".format(i, str(hat)) )

    print("\n\n===CONTROLLER===")
    left_x, left_y = my_controller.get_left_stick()
    right_x, right_y = my_controller.get_right_stick()

    print("LEFT - X:{}, Y:{}".format(left_x, left_y))
    print("RIGHT - X:{}, Y:{}".format(right_x, right_y))
    print("BUTTONS {}".format(my_controller.get_buttons()))

    clock.tick(REFRESH_RATE)

pygame.quit ()
