import pygame
import sys
import random
import math

from os.path import join
from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle

class Game:
    def __init__(self):
        pygame.init()

        SCREEN_WIDTH = 640
        SCREEN_HEIGHT = 480
        self.frame_update = 60
        pygame.display.set_caption('Assassin Showdown')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display = pygame.Surface((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.clock = pygame.time.Clock()

        self.movement = [False, False]
        self.assets = {
            'decor': load_images(join('tiles', 'decor')),
            'grass': load_images(join('tiles', 'grass')),
            'large_decor': load_images(join('tiles', 'large_decor')),
            'stone': load_images(join('tiles', 'stone')),
            'player': load_image(join('player.png')),
            'background': load_image(join('background.png')),
            'clouds': load_images(join('clouds')),
            'player/idle': Animation(load_images(join('player', 'idle')), img_dur=6),
            'player/run': Animation(load_images(join('player', 'run')), img_dur=4),
            'player/jump': Animation(load_images(join('player', 'jump'))),
            'player/slide': Animation(load_images(join('player', 'slide'))),
            'player/wall_slide': Animation(load_images(join('player', 'wall_slide'))),
            'particle/leaf': Animation(load_images(join('particles', 'leaf')), img_dur=20, loop=False),
            'particle/particle': Animation(load_images(join('particles', 'particle')), img_dur=6, loop=False),
        }
        
        self.clouds = Clouds(self.assets['clouds'], count=16)
        self.player = Player(self, (50, 50), (8, 15))
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load(join('data', 'assets', 'entities', 'maps', '0.json'))
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        self.particles = []
        self.scroll = [0, 0]

    def run(self):
        while True:
            self.display.blit(self.assets['background'], (0,0))
            lerp_factor = 0.08
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) * lerp_factor
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) * lerp_factor
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    if event.key == pygame.K_q:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
            scaled_surface = pygame.transform.scale(self.display, self.screen.get_size())
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.update()
            self.clock.tick(self.frame_update)

Game().run()