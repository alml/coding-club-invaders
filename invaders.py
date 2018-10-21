#!/usr/bin/python

import pygame
import random
import sys

# Initialize pygame.
pygame.init()
size = width, height = 640, 480
screen = pygame.display.set_mode(size)
pygame.mixer.init()

# Load images from disk.
player_image = pygame.image.load('player.gif')
player_image_rect = player_image.get_rect()
enemy_image = pygame.image.load('enemy.gif')
enemy_image_rect = enemy_image.get_rect()
player_bullet_image = pygame.image.load('player_bullet.gif')
player_bullet_image_rect = player_bullet_image.get_rect()
enemy_bullet_image = pygame.image.load('enemy_bullet.gif')
enemy_bullet_image_rect = enemy_bullet_image.get_rect()

# Load sounds from disk.
explosion_sound = pygame.mixer.Sound('explosion.wav')

# Player position on the screen.
player_rect = pygame.Rect(
        (int((width - player_image_rect.width) / 2), height - player_image_rect.height),
        player_image_rect.size)
player_x_speed = 1

# Screen styling.
background = 0, 0, 0

# Game speed limiter.
clock = pygame.time.Clock()
elapsed_sum = 0
timestep = 2

# How frequently the player can fire.
fire_interval = 50
fire_cooldown = 0

# Bullet properties.
bullet_speed = 1
bullets = []

# Enemy properties.
enemies = []


# Bullet represents both bullets fired by the player and by the enemies.
class Bullet(object):
    def __init__(self, x, y, down):
        self.down = down
        self.destroyed = False
        if down:
            self.image = enemy_bullet_image
            self.rect = pygame.Rect((x, y), enemy_bullet_image_rect.size)
        else:
            self.image = player_bullet_image
            self.rect = pygame.Rect((x, y), player_bullet_image_rect.size)

    def Draw(self):
        screen.blit(self.image, self.rect)

    def Update(self):
        if self.down:
            self.rect.move_ip(0, bullet_speed)
            if self.rect.top > height:
                self.destroyed = True
            # Check if the bullet kills the player.
            if self.rect.colliderect(player_rect):
                self.destroyed = True
                # TODO(alml): Decrement lives.
        else:
            self.rect.move_ip(0, -bullet_speed)
            if self.rect.bottom < 0:
                self.destroyed = True
            # Check if the bullet kills an enemy.
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    enemy.destroyed = True
                    self.destroyed = True
                    explosion_sound.play()


class Enemy(object):
    def __init__(self, x, y):
        # X and Y coordinates are local (relative to the swarm coordinates).
        self.x = x
        self.y = y
        self.destroyed = False
        self.rect = pygame.Rect(self.x, self.y, enemy_image_rect.width, enemy_image_rect.height)

    def Draw(self):
        screen.blit(enemy_image, self.rect)

    def Update(self, swarm_x):
        self.rect.x = self.x + swarm_x
        if random.random() < 0.0003:
            bullets.append(Bullet(
                self.rect.centerx - int(enemy_bullet_image_rect.width / 2),
                self.rect.bottom, down=True))

# Initialize the level with some enemies.
enemy_columns = 5
enemy_rows = 3
enemy_horizontal_interval = 100
enemy_vertical_interval = 50
enemy_swarm_width = enemy_columns * enemy_horizontal_interval
enemy_swarm_x = int(width / 2 - enemy_swarm_width / 2)
enemy_swarm_min_x = 0
enemy_swarm_max_x = width - enemy_swarm_width
enemy_swarm_x_speed = 1
for y in xrange(0, enemy_rows):
    for x in xrange(0, enemy_columns):
        enemies.append(Enemy(
            x * enemy_horizontal_interval + int(enemy_horizontal_interval / 2 - enemy_image_rect.width / 2),
            y * enemy_vertical_interval + 30))

while 1:
    # Prevent the main loop from running more than 60 times per second
    # and measures actually elapsed time since the previous frame.
    elapsed = clock.tick(60)
    elapsed_sum += elapsed

    # Update cooldown.
    if fire_cooldown > 0:
        fire_cooldown -= elapsed

    # Keyboard events.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Window is closed.
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Escape pressed.
                sys.exit()
            elif event.key == pygame.K_SPACE:
                # Fire control pressed.
                if fire_cooldown <= 0:
                    fire_cooldown = fire_interval
                    bullets.append(Bullet(
                        player_rect.centerx - int(player_bullet_image_rect.width / 2),
                        player_rect.top - player_bullet_image_rect.height, down=False))

    # Movement of the enemy swarm.
    enemy_swarm_x += enemy_swarm_x_speed
    if enemy_swarm_x_speed > 0 and enemy_swarm_x >= enemy_swarm_max_x:
        enemy_swarm_x = enemy_swarm_max_x
        enemy_swarm_x_speed *= -1
    if enemy_swarm_x_speed < 0 and enemy_swarm_x <= enemy_swarm_min_x:
        enemy_swarm_x = enemy_swarm_min_x
        enemy_swarm_x_speed *= -1

    # Handle keyboard states. For each elapsed "timestep" milliseconds handle
    # keyboard controls once.
    pressed = pygame.key.get_pressed()
    while elapsed_sum > timestep:
        elapsed_sum -= timestep
        if pressed[pygame.K_LEFT] and not pressed[pygame.K_RIGHT]:
            player_rect.move_ip(-player_x_speed, 0)
            if player_rect.left < 0:
                player_rect.left = 0
        elif pressed[pygame.K_RIGHT] and not pressed[pygame.K_LEFT]:
            player_rect.move_ip(player_x_speed, 0)
            if player_rect.right > width:
                player_rect.right = width
        for enemy in enemies:
            if not enemy.destroyed:
                enemy.Update(int(enemy_swarm_x))
        for bullet in bullets:
            if not bullet.destroyed:
                bullet.Update()

    # Remove destroyed bullets and enemies.
    bullets = [bullet for bullet in bullets if not bullet.destroyed]
    enemies = [enemy for enemy in enemies if not enemy.destroyed]

    # Frame draw.
    screen.fill(background)
    for bullet in bullets:
        bullet.Draw()
    for enemy in enemies:
        enemy.Draw()
    screen.blit(player_image, player_rect)
    pygame.display.flip()
