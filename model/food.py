import pygame
import random

# Draw food rectangle at a random position inside the field
class Food():
    foodColors = [
            (255, 255, 0),   # yellow
            (0, 255, 255),   # cyan
            (255, 0, 255),   # magenta
            (128, 128, 255)  # light blue
            ]

    def __init__(self, field):
        self.field = field
        self.x = random.randint(0, field.width - 1)
        self.y = random.randint(0, field.height - 1)
        self.color = random.choice(self.foodColors)

    # return current position of the food
    def position(self):
        return (self.x, self.y)

    def draw(self):
        size = self.field.blockSize
        rect = (self.x * size, self.y * size, size, size)
        pygame.draw.rect(self.field.screen, self.color, rect, 0)
