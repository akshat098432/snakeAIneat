import os
import math
import pickle
import numpy as np

pop_data_file = 'data/population.dat'
pickle_file = 'data/best_gen_instances.pickle'
config_file = 'config'

field_color = 0x000000
snake_color = 0xFFFFFF
blockSize = 16        # size of blocks in pixels
field_width = 16      # size of field width in blocks
field_height = 16
screenSize = (field_width * blockSize, field_height * blockSize)

renderdelay = 10
rendering = True
debug_on = False

EVENT_DURATION = 1  # Every mill secs there will be an event

NEAR_SCORE = 1
FOOD_SCORE = 10
LOOP_SCORE = 3
FAR_SCORE = 2
ALIVE_SCORE = 0.1
FOOD_CALORIES = 100

# =======================================================================================
# Method declarations
# =======================================================================================
# Extract RGB components from the color value
def extractRGB(color):
    r = (color & 0xFF0000) >> 16
    g = (color & 0x00FF00) >> 8
    b = (color & 0x0000FF)

    return (r, g, b)

def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def load_object(filename):
    with open(filename, 'rb') as f:
        obj = pickle.load(f)
    return obj

def save_best_generation_instance(instance, filename=pickle_file):
    instances = []

    if os.path.isfile(filename):
        instances = load_object(filename)

    instances.append(instance)
    save_object(instances, filename)

def left(orientation):
    (dx, dy) = orientation
    if (dx, dy) == (-1, 0):
        dx, dy = 0, -1
    elif (dx, dy) == (1, 0):
        dx, dy = 0, 1
    elif (dx, dy) == (0, 1):
        dx, dy = -1, 0
    elif (dx, dy) == (-1, 0):
        (dx, dy) = (1, 0)

    return (dx, dy)

def right(orientation):
    (dx, dy) = orientation
    if (dx, dy) == (-1, 0):
        dx, dy = 0, 1
    elif (dx, dy) == (1, 0):
        dx, dy = 0, -1
    elif (dx, dy) == (0, 1):
        dx, dy = 1, 0
    elif (dx, dy) == (0, -1):
        (dx, dy) = (-1, 0)

    return (dx, dy)

# =======================================================================================
# Get all inputs
# =======================================================================================
def get_safety_inputs(headPostion, fieldSize, orientation):
    # input parameters to be generated
    # index 0 - is it clear straight ahead
    # index 1 - is it clear to the left
    # index 2 - is it clear to the right
    # index 3 - distance to the wall

    # create list initialized with 0s
    inputs = [0] * 4

    (hx, hy) = headPostion
    (width, height) = fieldSize
    dist = 0

    if orientation == (-1, 0):    # moving left
        # dist = hx/width
        dist = hx

        # is it safe straight, left and right
        if hx > 0:
            inputs[0] = 1
        if hy > 0:
            inputs[1] = 1
        if hy < (height - 1):
            inputs[2] = 1

    elif orientation == (1, 0):   # moving right
        # dist = (width - hx) / width
        dist = (width - hx)

        # is it safe straight, left and right
        if hx < (width - 1):
            inputs[0] = 1
        if hy < (height - 1):
            inputs[1] = 1
        if hy > 0:
            inputs[2] = 1

    elif orientation == (0, 1):   # moving up
        # dist = (height - hy)/height
        dist = (height - hy)

        # is it safe straight, left and right
        if hy < (height -1):
            inputs[0] = 1
        if hx > 0:
            inputs[1] = 1
        if hx < (width -1):
            inputs[2] = 1

    elif orientation == (0, -1):   # moving down
        # dist = hy/height
        dist = hy

        # is it safe straight, left and right
        if (hy > 0):
            inputs[0] = 1
        if hx < (width -1):
            inputs[1] = 1
        if hx > 0:
            inputs[2] = 1

        inputs[3] = dist

    # will return 4 inputs
    return inputs

# generate inputs based on the snake current postion, food postion, and the walls
def get_food_inputs(headPostion, foodPosition, fieldSize, orientation):
    # will generate five inputs
    # in which direction the food is (four direction)
    # distance to the food

    # create list initialized with 0s
    inputs = [0] * 5

    (hx, hy) = headPostion
    (fx, fy) = foodPosition
    (w, h) = fieldSize

    # moving up
    if orientation == (0, 1):
        if fx == hx and fy >= hy:    # ahead
            inputs[0] = 1
        elif fx == hx and fy < hy:   # behind
            inputs[1] = 1
        elif fx < hx:                # left
            inputs[2] = 1
        elif fx > hx:                # right
            inputs[3] = 1
    # moving down
    elif orientation == (0, -1):
        if fx == hx and fy <= hy:    # ahead
            inputs[0] = 1
        elif fx == hx and fy > hy:   # behind
            inputs[1] = 1
        elif fx > hx:                # left
            inputs[2] = 1
        elif fx < hx:                # right
            inputs[3] = 1
    # moving left
    elif orientation == (-1, 0):
        if fx <= hx and hy == fy:    # ahead
            inputs[0] = 1
        elif fx > hx and hy == fy:   # behind
            inputs[1] = 1
        elif fy < hy:                # left
            inputs[2] = 1
        elif fy > hy:                # right
            inputs[3] = 1
    # moving right
    elif orientation == (1, 0):
        if fx >= hx and fy == hy:    # ahead
            inputs[0] = 1
        elif fx < hx and fy == hy:   # behind
            inputs[1] = 1
        elif fy > hy:                # left
            inputs[2] = 1
        elif fy < hy:                # right
            inputs[3] = 1

        # get distance to the food and normalize it
        dist = math.sqrt((hx - fx) ** 2 + (hy - fy) ** 2)
        wd = math.sqrt(w ** 2 + h ** 2)
        # inputs[4] = dist / wd
        inputs[4] = dist

    # will return 5 elements
    return inputs

def get_inputs(headPostion, foodPosition, fieldSize, orientation):
    food_inputs = get_food_inputs(headPostion, foodPosition, fieldSize, orientation)
    safety_inputs = get_safety_inputs(headPostion, fieldSize, orientation)
    inputs = safety_inputs + food_inputs

    return inputs
