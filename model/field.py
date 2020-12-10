import game_utils as gu

class Field():
    def __init__(self, screen, width, height, blockSize, color = gu.field_color):
        # visual display
        self.screen = screen
        self.fieldColor = gu.extractRGB(color)

        # width, heigt and blockSize being accessed from Food
        self.width = width
        self.height = height
        self.blockSize = blockSize

    def draw(self):
        self.screen.fill(self.fieldColor)
