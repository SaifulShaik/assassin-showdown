class Button:
    def __init__(self, x, y, images, change):
        self.x = x
        self.y = y
        self.images = images
        self.change = change
        self.size = self.images[0].get_size()
        self.clicked = False

    def render(self, mouse_pos, click, surf):
        if self.x + self.size[0] >= mouse_pos[0] >= self.x and self.y + self.size[1] >= mouse_pos[1] >= self.y:
            surf.blit(self.images[1], (self.x, self.y))
            if click and not self.clicked:
                self.clicked = True
                if self.change:
                    self.change()
        else:
            surf.blit(self.images[0], (self.x, self.y)) 
        if not click:
            self.clicked = False