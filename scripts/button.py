class Button:
    def __init__(self, x, y, images, change):
        self.x = x
        self.y = y
        self.images = images
        self.change = change
        # Assuming all images are the same size
        self.size = self.images[0].get_size()  # Width and height of the button

    def render(self, mouse_pos, click, surf):
        # Check if mouse is over the button
        if self.x + self.size[0] >= mouse_pos[0] >= self.x and self.y + self.size[1] >= mouse_pos[1] >= self.y:
            surf.blit(self.images[1], (self.x, self.y))  # Highlight image
            if click:
                return self.change()  # Call the change function
        else:
            surf.blit(self.images[0], (self.x, self.y))  # Default image