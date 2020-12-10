import pygame
import game_utils as gu

class Snake:
    # A snake has a body that consists of several points
    # The body has a head (first point) and a tail (last point)
    headColor = (50, 255, 0)
    bodyColor = (0, 200, 0)
    damageColor = (255, 0, 0)

    # ===================================================================
    # constructor
    # ===================================================================
    def __init__(self, field, color, len = 5, x = 10, y = 10):
        # Start with a snake in a horizontal position
        self.field = field
        self.body = []
        self.growLength = 0

        for i in range(0, len):
            self.body.append((x - i, y))

        self.bodyColor = gu.extractRGB(color)
        self.headColor = gu.extractRGB(color)

    # ===================================================================
    # Return current position of head
    # ===================================================================
    def position(self):
        return self.body[0]

    def grow(self, length = 1):
        self.growLength += length

    # ===================================================================
    # Move the snake in the given direction and check if the move was valid or not
    # if snake hits any wall - is not valid
    # if snake head bumps into its own body - invalid move
    # it will return False for an invalid move, otherwise True
    # ===================================================================
    def move(self, dx, dy):
        # Move the snake in the given direction
        # either it will move one position on X axis or one position on Y axis
        # first get current position of head
        (x, y) = self.body[0]

        # calculate new position of head
        x += dx
        y += dy

        # Insert a new head position in the front
        self.body.insert(0, (x, y)) # insert new position of head

        if self.growLength > 0:
            # every next move will increase the length by growLength value
            # it will keep growing till growLength becomes 0
            self.growLength -= 1
        else:
            # otherwise just move the snake i.e. remove last element i.e. tail
            self.body.pop()

        # check if this new move makes the head clashing with its own body
        # return False if it collides its an invalid move
        if self.body[0] in self.body[1:]:
            return False
        elif x < 0 or x >= self.field.width or y < 0 or y >= self.field.height:
            # Does it hit any walls
            # if yes then it is also an invalid move
            return False
        else:
            # otherwise its a valid move
            return True

    # ===================================================================
    # Display the snake
    # ===================================================================
    def draw(self, damage = False):
        # Draw the body of the snake
        for i in range(0, len(self.body)):
            if damage:
                color = self.damageColor
            elif i == 0:
                color = self.headColor
            else:
                color = self.bodyColor

            (x, y) = self.body[i]
            size = self.field.blockSize
            rect = (x * size, y * size, size, size)
            pygame.draw.rect(self.field.screen, color, rect, 0)
