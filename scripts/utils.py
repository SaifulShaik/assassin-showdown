import pygame, os
from os.path import join

BASE_PATH_IMG = join('.', 'data', 'assets', 'entities/')

def load_image(path):
    full_path = join(BASE_PATH_IMG, path)
    try:
        img = pygame.image.load(full_path).convert()
        img.set_colorkey((0, 0, 0))
        return img
    except pygame.error as e:
        raise RuntimeError(f"Failed to load image at {full_path}: {e}")
    
def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_PATH_IMG + path)):
        images.append(load_image(path + '/' + img_name))
    return images

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.img_dur = img_dur
        self.done = False
        self.loop = loop
        self.frame = 0

    
    def copy(self):
        return Animation(self.images, self.img_dur, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame+1) % (self.img_dur*len(self.images))
        else:
            self.frame = min(self.frame+1, self.img_dur*len(self.images)-1)
            if self.frame >= self.img_dur*len(self.images)-1:
                self.done = True



    def img(self):
        return self.images[int(self.frame / self.img_dur)]
