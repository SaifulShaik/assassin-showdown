import pygame
import sys
import random
import math

import os
from os.path import join
from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.button import Button
from scripts.levels import Levels

class Game:
    def __init__(self):

        # Initialize Pygame and window
        pygame.init()
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        self.frame_update = 60
        pygame.display.set_caption('Assassin Showdown')
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.display = pygame.Surface((self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2))
        self.clock = pygame.time.Clock()

        self.movement = [False, False]
        # Assets to load
        self.assets = {
            'decor': load_images(join('tiles', 'decor')),
            'grass': load_images(join('tiles', 'grass')),
            'large_decor': load_images(join('tiles', 'large_decor')),
            'stone': load_images(join('tiles', 'stone')),
            'player': load_image(join('player.png')),
            'background/game': load_image(join('background_game.png')),
            'clouds': load_images(join('clouds')),
            'enemy/idle': Animation(load_images(join('enemy', 'idle')), img_dur=6),
            'enemy/run': Animation(load_images(join('enemy', 'run')), img_dur=4),
            'player/idle': Animation(load_images(join('player', 'idle')), img_dur=6),
            'player/run': Animation(load_images(join('player', 'run')), img_dur=4),
            'player/jump': Animation(load_images(join('player', 'jump'))),
            'player/slide': Animation(load_images(join('player', 'slide'))),
            'player/wall_slide': Animation(load_images(join('player', 'wall_slide'))),
            'particle/leaf': Animation(load_images(join('particles', 'leaf')), img_dur=10, loop=False),
            'particle/particle': Animation(load_images(join('particles', 'particle')), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),

            # Main UI Assets
            'background/menu': load_image(join('UI/front/background/background_menu.png')),
            "title": load_image("UI/front/title.png"),
            "start/default": load_image("UI/front/buttons/Play/0.png"),
            "start/hover": load_image("UI/front/buttons/Play/1.png"), 
            "options/default": load_image("UI/front/buttons/Options/0.png"),
            "options/hover": load_image("UI/front/buttons/Options/1.png"),
            "quit/default": load_image("UI/front/buttons/Quit/0.png"),
            "quit/hover": load_image("UI/front/buttons/Quit/1.png"),
            #"level_button" : load_images("button/level"), 
            #"help_button" : load_images("button/help"), 
        }

        self.level_assets = {
            "layout" : load_image("UI/front/level/level_page.png"),
        }
        self.assets_options = {
            #"layout" : load_image("UI/front/layout.png"),
            "back/default" : load_image("UI/front/Options/Back/0.png"),
            "back/hover" : load_image("UI/front/Options/Back/1.png"),

        }


        self.sfx = {
            'jump': pygame.mixer.Sound('data/assets/audio/jump.wav'),
            'dash': pygame.mixer.Sound('data/assets/audio/dash.wav'),
            'shoot': pygame.mixer.Sound('data/assets/audio/shoot.wav'),
            'hit': pygame.mixer.Sound('data/assets/audio/hit.wav'),
            'death': pygame.mixer.Sound('data/assets/audio/hit.wav'),
            'ambience': pygame.mixer.Sound('data/assets/audio/ambience.wav'),
        }

        # volume control
        self.sfx['ambience'].set_volume(0.1)
        self.sfx['shoot'].set_volume(0.3)
        self.sfx['hit'].set_volume(0.7)
        self.sfx['death'].set_volume(0.7)
        self.sfx['dash'].set_volume(0.2)
        self.sfx['jump'].set_volume(0.6)

        # Initialize game objects
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)

        self.setup_buttons()

        self.level = 0

        self.load_level(self.level)

        self.screenshake = 0
        
    # Load Level
    def load_level(self, map_id):
        self.tilemap.load('data/assets/entities/maps/' + str(map_id) + '.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
            
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
            
        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

    # Setup Buttons to display on the main menu and other UI pages
    def setup_buttons(self):
        """Initialize buttons."""
        button_width, button_height = 160 / 1.5, 83 / 1.5
        self.buttons = {
            "start": Button(
                x=self.SCREEN_WIDTH / 4 - button_width / 2,
                y=self.SCREEN_HEIGHT / 4 - button_height / 1.5,
                images=[
                    pygame.transform.scale(self.assets['start/default'], (button_width, button_height)),
                    pygame.transform.scale(self.assets['start/hover'], (button_width, button_height)),
                ],
                change=self.run,
            ),
            "options": Button(
                x=self.SCREEN_WIDTH / 4 - button_width / 2,
                y=self.SCREEN_HEIGHT / 4 + button_height - button_height/3,
                images=[
                    pygame.transform.scale(self.assets['options/default'], (button_width, button_height)),
                    pygame.transform.scale(self.assets['options/hover'], (button_width, button_height)),
                ],
                change=self.options,
            ),
            "quit": Button(
                x=self.SCREEN_WIDTH / 4 - button_width / 2,
                y=self.SCREEN_HEIGHT / 4 + button_height * 2,
                images = [
                    pygame.transform.scale(self.assets['quit/default'], (button_width, button_height)),
                    pygame.transform.scale(self.assets['quit/hover'], (button_width, button_height)),
                ],
                change = self.quit,
            ),
            "back": Button(
                x=20,
                y=20,
                images = [
                    self.assets_options['back/default'],
                    self.assets_options['back/hover'],
                ],
                change = None,
            )
        }


    # Start with main menu
    def main_menu(self):
        """Display the main menu."""
        while True:
            self.display.fill((0, 0, 0))
            self.display.blit(self.assets['background/menu'], (0, 0))

            # Scale the title image
            title_width = self.SCREEN_WIDTH / 6
            title_height = self.SCREEN_HEIGHT / 5
            title = pygame.transform.scale(self.assets['title'], (int(title_width), int(title_height)))

            # Calculate position for top-center alignment
            title_x = (self.SCREEN_WIDTH / 2 - title_width / 2) / 2.5
            title_y = 0
            self.display.blit(title, (title_x, title_y))

            mouse_pos = pygame.mouse.get_pos()
            scaled_mouse_pos = (mouse_pos[0] / 2, mouse_pos[1] / 2)
            click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click = True

            # Render and check button interactions
            for button_name, button in self.buttons.items():
                if button_name != "back":
                    button.render(scaled_mouse_pos, click, self.display)

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(self.frame_update)


    # Check if mouse is over button
    def is_mouse_over_button(self, button, mouse_pos):
        return button.x + button.size[0] >= mouse_pos[0] >= button.x and button.y + button.size[1] >= mouse_pos[1] >= button.y
         

    # Options/settings Window
    def options(self):
        """Display the options menu with a blur transition."""
        blur_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        blur_alpha = 0 
        blur_increment = 10

        # Transition in
        while blur_alpha < 255:
            blur_alpha += blur_increment
            blur_alpha = min(blur_alpha, 255)
            blur_surface.fill((0, 0, 0, int(blur_alpha)))
            self.display.fill((47, 44, 47))
            self.display.blit(self.assets['background/menu'], (0, 0))

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            self.screen.blit(blur_surface, (0, 0))
            pygame.display.update()
            self.clock.tick(self.frame_update)

        # Main options menu loop
        back_button_clicked = False
        while not back_button_clicked:
            self.display.fill((0, 0, 0))
            self.display.blit(self.assets['background/menu'], (0, 0))

            mouse_pos = pygame.mouse.get_pos()
            scaled_mouse_pos = (mouse_pos[0] / 2, mouse_pos[1] / 2)
            click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click = True

            self.buttons['back'].render(scaled_mouse_pos, click, self.display)

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(self.frame_update)

            if self.buttons['back'].clicked:
                break

        # Transition out
        blur_alpha = 255
        while blur_alpha > 0:
            blur_alpha -= blur_increment
            blur_alpha = max(blur_alpha, 0)
            blur_surface.fill((0, 0, 0, int(blur_alpha)))
            self.display.fill((0, 0, 0))
            self.display.blit(self.assets['background/menu'], (0, 0))

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            self.screen.blit(blur_surface, (0, 0))
            pygame.display.update()
            self.clock.tick(self.frame_update)

        self.main_menu()
    

    def help(self):
        pass


    def level_page(self):
        back_button_clicked = False
        while not back_button_clicked:
            self.display.fill((0, 0, 0))
            self.display.blit(self.assets['background/menu'], (0, 0))
            middle_x = self.SCREEN_WIDTH / 4
            middle_y = self.SCREEN_HEIGHT / 4
            self.display.blit(self.level_assets['layout'], (middle_x, middle_y))

            mouse_pos = pygame.mouse.get_pos()
            scaled_mouse_pos = (mouse_pos[0] / 2, mouse_pos[1] / 2)
            click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click = True

            self.buttons['back'].render(scaled_mouse_pos, click, self.display)

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(self.frame_update)

            if self.buttons['back'].clicked:
                break
            


    # Quit game function
    def quit(self):
        pygame.quit()
        sys.exit()

    # Run the main game
    def run(self):
        pygame.mixer.music.load('data/assets/audio/music.wav')
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

        self.sfx['ambience'].play(-1)

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets['background/game'], (0, 0))
            self.screenshake = max(0, self.screenshake - 1)
            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/assets/entities/maps'))-1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.load_level(self.level)
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            
            self.clouds.update()
            self.clouds.render(self.display_2, offset=render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
            
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)
            
            # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for _ in range(2):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['death'].play()
                        self.screenshake = max(16, self.screenshake) 
                        for _ in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                        
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)
            
            display_mask = pygame.mask.from_surface(self.display)
            display_silhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                self.display_2.blit(display_silhouette, offset)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_q:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            #  Pause UI page needs to be added here

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))


            self.display_2.blit(self.display, (0, 0))
            screenshake_offset = (random.random()* self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            scaled_surface = pygame.transform.scale(self.display_2, self.screen.get_size())
            self.screen.blit(scaled_surface, screenshake_offset)
            pygame.display.update()
            self.clock.tick(self.frame_update)

# Run the main menu so user has options before playing the game
Game().main_menu()