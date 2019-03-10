import arcade
import os
import math
from fighter import *

WIDTH = 1600
HEIGHT = 900

SCALE = 0.8
SPEED = 5

PLATFORM_SCALE = 1

BLUE = arcade.color.ALICE_BLUE

LEFT = arcade.key.LEFT
RIGHT = arcade.key.RIGHT

JUMP_SPEED = 17
GRAVITY = 0.5
# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 240
RIGHT_MARGIN = 150

TILE_SIZE = 128
SCALED_TILE_SIZE = TILE_SIZE * PLATFORM_SCALE
MAP_HEIGHT = 7

def get_map(filename):
    """
    This function loads an array based on a map stored as a list of
    numbers separated by commas.
    """

    # Open the file
    map_file = open(filename)

    # Create an empty list of rows that will hold our map
    map_array = []

    # Read in a line from the file
    for line in map_file:

        # Strip the whitespace, and \n at the end
        line = line.strip()

        # This creates a list by splitting line everywhere there is a comma.
        map_row = line.split(",")

        # The list currently has all the numbers stored as text, and we want it
        # as a number. (e.g. We want 1 not "1"). So loop through and convert
        # to an integer.
        for index, item in enumerate(map_row):
            map_row[index] = int(item)

        # Now that we've completed processing the row, add it to our map array.
        map_array.append(map_row)

    # Done, return the map.
    return map_array

class Window(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)

        path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(path)

        self.player_list = None
        self.player = None
        self.wall_list = None

        # Set up the player
        self.player_sprite = None

        # Physics engine
        self.physics_engine = None

        # Used for scrolling map
        self.view_left = 0
        self.view_bottom = 0

    def on_draw(self):
        arcade.start_render()
        self.player_list.draw()
        self.wall_list.draw()

    def setup_player(self):
        self.player_list = arcade.SpriteList()
        self.player = Fighter()
        self.player.stand_left = []
        self.player.stand_right = []
        self.player.walk_right = []
        self.player.walk_left = []
        self.player.run_right = []
        self.player.run_left = []
        self.player.dead_right = []
        self.player.dead_left = []
        self.player.jump_right = []
        self.player.jump_left = []

        self.player.stand_right.append(arcade.load_texture('images/stand/0.png', scale=SCALE))
        self.player.stand_left.append(arcade.load_texture('images/stand/0.png', scale=SCALE, mirrored=True))

        for i in range(10):
            self.player.walk_right.append(arcade.load_texture('images/walk/' + str(i) + '.png', scale=SCALE))
            self.player.walk_left.append(arcade.load_texture('images/walk/' + str(i) + '.png', scale=SCALE, mirrored=True))

        for i in range(12):
            self.player.jump_right.append(arcade.load_texture('images/jump/' + str(i) + '.png', scale=SCALE))
            self.player.jump_left.append(arcade.load_texture('images/jump/' + str(i) + '.png', scale=SCALE, mirrored=True))

        for i in range(8):
            self.player.run_right.append(arcade.load_texture('images/run/' + str(i) + '.png', scale=SCALE))
            self.player.run_left.append(arcade.load_texture('images/run/' + str(i) + '.png', scale=SCALE, mirrored=True))
            self.player.dead_right.append(arcade.load_texture('images/die/' + str(i) + '.png', scale=SCALE))
            self.player.dead_left.append(arcade.load_texture('images/die/' + str(i) + '.png', scale=SCALE, mirrored=True))

        self.player.delta_distance = 20
        self.player.center_x = WIDTH//2
        self.player.center_y = HEIGHT//2
        self.player.scale = SCALE
        self.player.speed = SPEED
        self.player.gravity_constant = 0.9
        self.player_list.append(self.player)

    def setup(self):
        arcade.set_background_color(BLUE)
        self.setup_player()
        self.wall_list = arcade.SpriteList()
        # Get a 2D array made of numbers based on the map
        map_array = get_map("map.csv")

        # Now that we've got the map, loop through and create the sprites
        for row_index in range(len(map_array)):
            for column_index in range(len(map_array[row_index])):

                item = map_array[row_index][column_index]

                # For this map, the numbers represent:
                # -1 = empty
                # 0  = grass left edge
                # 1  = grass middle
                # 2  = grass right edge
                # 3  = grass left bottom edge
                # 4  = grass middle bottom
                # 5  = grass right bottom edge
                # 6  = water top
                # 7  = water bottom

                if item >= 0:
                    wall = arcade.Sprite("images/map/" + str(item) + ".png", PLATFORM_SCALE)
                    # Calculate where the sprite goes
                    wall.left = column_index * SCALED_TILE_SIZE
                    wall.top = (MAP_HEIGHT - row_index) * SCALED_TILE_SIZE

                    # Add the sprite
                    self.wall_list.append(wall)

        # Create out platformer physics engine with gravity
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY)


        # Set the view port boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

    def update(self, delta_time):
        self.player.update()
        self.player.update_animation()
        """ Movement and game logic """

        self.physics_engine.update()

        # --- Manage Scrolling ---

        # Track if we need to change the view port

        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_MARGIN
        if self.player.left < left_bndry:
            self.view_left -= left_bndry - self.player.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + WIDTH - RIGHT_MARGIN
        if self.player.right > right_bndry:
            self.view_left += self.player.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + HEIGHT - VIEWPORT_MARGIN
        if self.player.top > top_bndry:
            self.view_bottom += self.player.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN
        if self.player.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player.bottom
            changed = True

        # If we need to scroll, go ahead and do it.
        if changed:
            arcade.set_viewport(self.view_left,
                                WIDTH + self.view_left,
                                self.view_bottom,
                                HEIGHT + self.view_bottom)

    def on_key_press(self, key, mods):
        if key == RIGHT:
            self.player.change_x = SPEED
        if key == LEFT:
            self.player.change_x = -SPEED
        if key == RIGHT and mods == arcade.key.MOD_SHIFT:
            self.player.change_x = SPEED * 1.5
            self.player.run = True
        if key == LEFT and mods == arcade.key.MOD_SHIFT:
            self.player.change_x = -SPEED * 1.5
            self.player.run = True
        if key == arcade.key.A:
            self.player.dead = True
        if key == arcade.key.SPACE:
            # This line below is new. It checks to make sure there is a platform underneath
            # the player. Because you can't jump if there isn't ground beneath your feet.
            if self.physics_engine.can_jump():
                self.player.change_y = JUMP_SPEED
                self.player.jump = True

    def on_key_release(self, key, mods):
        if key == RIGHT or key == LEFT:
            self.player.change_x = 0
            self.player.run = False
            self.player.cur_index = 0
        if mods == arcade.key.MOD_SHIFT:
            self.player.run = False

def main():
    window = Window(WIDTH, HEIGHT)
    window.setup()
    arcade.run()

if __name__ == '__main__':
    main()
