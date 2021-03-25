from math import cos, sin, radians, atan2, pi

import pygame
from settings import *
from random import choice, randint

pygame.init()


class Sprite(pygame.sprite.Sprite):
    hurt_sound = pygame.mixer.Sound('data/sounds/hurt.wav')

    def __init__(self, img, x, y, *groups):
        super().__init__(*groups)
        self.image = img.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(Sprite):
    stand_image = pygame.image.load('data/img/mc_stand.png')
    move_right_image = pygame.image.load('data/img/mc_move_right.png')
    move_left_image = pygame.image.load('data/img/mc_move_left.png')
    stand_images = []
    for i in range(0, 27, 9):
        sub_image = stand_image.subsurface((i, 0), (9, 18))
        stand_images.append(pygame.transform.scale2x(sub_image))
    move_right_images = []
    for i in range(0, 27, 9):
        sub_image = move_right_image.subsurface((i, 0), (9, 18))
        move_right_images.append(pygame.transform.scale2x(sub_image))
    move_left_images = []
    for i in range(0, 27, 9):
        sub_image = move_left_image.subsurface((i, 0), (9, 18))
        move_left_images.append(pygame.transform.scale2x(sub_image))

    jump_sound = pygame.mixer.Sound('data/sounds/jump.wav')

    def __init__(self, x, y, *groups, blocks=None, health=5):
        super().__init__(Player.stand_images[0], x, y, *groups)
        self.speed = PLAYER_SPEED
        self.hp = health
        self.in_air_timer = 0
        self.all_sprites = groups[0]
        self.falling_speed = 0
        self.number_of_image = 0
        if blocks is not None:
            self.collide_list = blocks
        else:
            self.collide_list = groups[0]
        self.call_down_to_the_next_image = CALL_DOWN_TO_THE_NEXT_IMAGE_PLAYER
        self.is_standing = True
        self.is_moving_right = False
        self.is_moving_left = False

    def set_image(self):
        if self.is_standing:
            if self.call_down_to_the_next_image < 0:
                self.number_of_image = (self.number_of_image + 1) % len(Player.stand_images)
                self.image = self.stand_images[self.number_of_image]
                self.call_down_to_the_next_image = CALL_DOWN_TO_THE_NEXT_IMAGE_PLAYER
        elif self.is_moving_right:
            if self.call_down_to_the_next_image < 0:
                self.number_of_image = (self.number_of_image + 1) % len(Player.move_right_images)
                self.image = self.move_right_images[self.number_of_image]
                self.call_down_to_the_next_image = CALL_DOWN_TO_THE_NEXT_IMAGE_PLAYER
        elif self.is_moving_left:
            if self.call_down_to_the_next_image < 0:
                self.number_of_image = (self.number_of_image + 1) % len(Player.move_left_images)
                self.image = self.move_left_images[self.number_of_image]
                self.call_down_to_the_next_image = CALL_DOWN_TO_THE_NEXT_IMAGE_PLAYER

    def update(self, *args, **kwargs) -> None:
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
        keys = pygame.key.get_pressed()
        move_set = [0, 0]
        delta = self.speed / FPS

        if keys[pygame.K_a] or keys[pygame.K_d]:
            if keys[pygame.K_a]:
                if not self.is_moving_left:
                    self.number_of_image = 0
                    self.call_down_to_the_next_image = 0
                self.is_moving_right = False
                self.is_moving_left = True
                self.is_standing = False
                move_set[0] -= delta
            if keys[pygame.K_d]:
                if not self.is_moving_right:
                    self.number_of_image = 0
                    self.call_down_to_the_next_image = 0
                self.is_moving_right = True
                self.is_moving_left = False
                self.is_standing = False
                move_set[0] += delta
        else:
            if not self.is_standing:
                self.number_of_image = 0
                self.call_down_to_the_next_image = 0
            self.is_moving_right = False
            self.is_moving_left = False
            self.is_standing = True

        self.call_down_to_the_next_image -= 1000 / FPS
        self.set_image()

        self.falling_speed += 0.25
        if self.falling_speed > FALLING_SPEED_MAX:
            self.falling_speed = FALLING_SPEED_MAX

        move_set[1] += self.falling_speed

        if move_set[0] != 0:
            self.move_x(move_set[0])
            for tile in self.get_collision_list():
                if move_set[0] > 0:
                    self.rect.right = tile.left
                    collision_types['right'] = True
                elif move_set[0] < 0:
                    self.rect.left = tile.right
                    collision_types['left'] = True

        if move_set[1] != 0:
            self.move_y(move_set[1])
            for tile in self.get_collision_list():
                if move_set[1] > 0:
                    self.rect.bottom = tile.top
                    collision_types['bottom'] = True
                elif move_set[1] < 0:
                    self.rect.top = tile.bottom
                    collision_types['top'] = True

        if collision_types['bottom']:
            self.falling_speed = 0
            self.in_air_timer = 0
        else:
            self.in_air_timer += 1

        if collision_types['top']:
            self.falling_speed = 0

    def jump(self):
        if self.in_air_timer < IN_AIR_TIMER:
            Player.jump_sound.play()
            self.falling_speed -= JUMP_SPEED

    def move_x(self, val):
        self.rect.x += val

    def move_y(self, val):
        self.rect.y += val

    def get_collision_list(self):
        collisions = []
        for r in [spr.rect for spr in self.collide_list]:
            if self.rect.colliderect(r):
                collisions.append(r)
        return collisions


class Wall(Sprite):
    images = [
        pygame.transform.scale2x(pygame.image.load('data/img/wall_2.png')),
        pygame.transform.scale2x(pygame.image.load('data/img/wall_1.png')),
        pygame.transform.scale2x(pygame.image.load('data/img/wall_3.png')),
        pygame.transform.scale2x(pygame.image.load('data/img/angle.png')),
        pygame.transform.scale2x(pygame.image.load('data/img/send.png'))
    ]

    images = {
        '1': [
            images[0].copy(),
            images[1].copy(),
            images[2].copy()
        ],
        '2': [
            pygame.transform.rotate(images[0].copy(), 90),
            pygame.transform.rotate(images[1].copy(), 90),
            pygame.transform.rotate(images[2].copy(), 90),
        ],
        '3': [
            pygame.transform.rotate(images[0].copy(), -90),
            pygame.transform.rotate(images[1].copy(), -90),
            pygame.transform.rotate(images[2].copy(), -90),
        ],
        '4': [
            pygame.transform.rotate(images[0].copy(), 180),
            pygame.transform.rotate(images[1].copy(), 180),
            pygame.transform.rotate(images[2].copy(), 180),
        ],
        '5': images[3].copy(),
        '6': pygame.transform.rotate(images[3].copy(), 90),
        '7': pygame.transform.rotate(images[3].copy(), -90),
        '8': pygame.transform.rotate(images[3].copy(), 180),
        '9': images[4]
    }

    def __init__(self, x, y, *groups, key='1', is_angle=False, is_send=False):
        image = choice(Wall.images[key]) if not is_angle else Wall.images[key]
        if is_send:
            image = Wall.images['9']
        super(Wall, self).__init__(image, x, y, *groups)


class Mob(Sprite):
    stand_image = pygame.image.load('data/img/mob_stand.png')
    stand_images = []

    shot = pygame.mixer.Sound('data/sounds/enemy_shot.wav')

    for i in range(0, 18, 9):
        sub_image = stand_image.subsurface((i, 0), (9, 18))
        stand_images.append(pygame.transform.scale2x(sub_image))

    def __init__(self, x, y, *groups, blocks=None, bullets=None, health=3):
        super().__init__(Mob.stand_images[0], x, y, *groups)
        self.call_down_for_the_bullet = randint(1500, 3000)
        self.in_air_timer = 0
        self.all_sprites = groups[0]
        self.hp = health
        self.max_hp = health
        self.falling_speed = 0
        self.number_of_image = 0
        self.bullets = bullets
        if blocks is not None:
            self.collide_list = blocks
        else:
            self.collide_list = groups[0]
        self.player = [i for i in self.all_sprites if isinstance(i, Player)][0]
        self.call_down_to_the_next_image = CALL_DOWN_TO_THE_NEXT_IMAGE_MOB
        self.is_standing = True
        self.is_moving_right = False
        self.is_moving_left = False

        for tile in self.get_collision_list():
            self.rect.bottom = tile.top

    def update(self, *args, **kwargs) -> None:
        if self.call_down_for_the_bullet < 0:
            if self.on_the_line():
                Mob.shot.play()
                rot = 180 / pi * atan2(- 1 * (self.rect.y - self.player.rect.centery),
                                       (self.rect.centerx - self.player.rect.centerx)) - 180
                Bullet(self.rect.centerx, self.rect.y, rot, self.bullets,
                       self.all_sprites, enemies=[self.player],
                       blocks=self.collide_list, is_enemy=True)
                self.call_down_for_the_bullet = 1000

        self.call_down_for_the_bullet -= 1000 / FPS

        if self.hp <= 0:
            self.kill()
        self.call_down_to_the_next_image -= 1000 / FPS
        self.set_image()

    def get_collision_list(self):
        collisions = []
        for r in [spr.rect for spr in self.collide_list]:
            if self.rect.colliderect(r):
                collisions.append(r)
        return collisions

    def on_the_line(self):
        dest_x = self.player.rect.centerx
        dest_y = self.player.rect.centery
        rect = pygame.rect.Rect(self.rect.centerx, self.rect.centery, 10, 10)
        list_rects = [i.rect for i in self.collide_list]
        flag = False
        for i in range(min(rect.centery, dest_y), max(dest_y, rect.centery) + 10, 20):
            for j in range(min(rect.centerx, dest_x), max(dest_x, rect.centerx) + 10, 20):
                rect.centery = i
                rect.centerx = j
                if rect.collidelist(list_rects) != -1:
                    flag = True
        return not flag

    def set_image(self):
        if self.is_standing:
            if self.call_down_to_the_next_image < 0:
                self.number_of_image = (self.number_of_image + 1) % len(Mob.stand_images)
                self.image = self.stand_images[self.number_of_image]
                self.call_down_to_the_next_image = CALL_DOWN_TO_THE_NEXT_IMAGE_MOB


class Bullet(Sprite):
    image = pygame.image.load('data/img/bullet.png')
    image_for_enemy = pygame.image.load('data/img/enemy_bullet.png')

    sound_shot_wall = pygame.mixer.Sound('data/sounds/wall_shot.wav')

    def __init__(self, x, y, rot, *groups, enemies=None, blocks=None, is_enemy=False):
        if not is_enemy:
            image = pygame.transform.rotate(Bullet.image.copy(), rot)
        else:
            image = pygame.transform.rotate(Bullet.image_for_enemy.copy(), rot)
        super().__init__(image, x, y, *groups)
        self.all_sprites = groups[1]
        self.enemies = enemies
        self.collide_list = blocks
        self.rot = rot
        self.delta_x = cos(radians(self.rot)) * BULLET_SPEED
        self.delta_y = - sin(radians(self.rot)) * BULLET_SPEED

    def update(self, *args, **kwargs) -> None:
        self.create_particles()
        self.rect.x += self.delta_x
        self.rect.y += self.delta_y
        for block in self.collide_list:
            if self.rect.colliderect(block.rect):
                Bullet.sound_shot_wall.play()
                self.kill()

        for enemy in self.enemies:
            if self.rect.colliderect(enemy.rect):
                Sprite.hurt_sound.play()
                enemy.hp -= 1
                self.kill()

    def create_particles(self):
        ParticleBullet(self.image.copy(), self.rect.x,
                       self.rect.y, self.rot, self.all_sprites,
                       blocks=self.collide_list, enemies=self.enemies)


class ParticleBullet(Sprite):
    def __init__(self, image, x, y, rot, *groups, blocks=None, enemies=None):
        super().__init__(image, x, y, *groups)
        self.enemies = enemies
        self.rot = rot
        self.rad = 7
        self.blocks = blocks
        self.delta_x = cos(radians(self.rot)) * (BULLET_SPEED - 3)
        self.delta_y = - sin(radians(self.rot)) * (BULLET_SPEED - 3)

    def update(self, *args, **kwargs) -> None:
        self.rect.x += self.delta_x
        self.rect.y += self.delta_y
        if self.delta_x > 0:
            self.delta_x -= 1
        else:
            self.delta_x += 1

        for block in self.blocks:
            if self.rect.colliderect(block.rect):
                self.kill()
        for enemy in self.enemies:
            if self.rect.colliderect(enemy.rect):
                self.kill()
        self.rad -= 0.5
        if self.rad == 0:
            self.kill()
        self.image = pygame.transform.scale(self.image, (round(self.rad * 2), round(self.rad * 2)))
        self.rect = self.image.get_rect(center=self.rect.center)


class Rune(Sprite):
    image = pygame.transform.scale2x(pygame.image.load('data/img/rune.png'))
    pick_up = pygame.mixer.Sound('data/sounds/pick_up.wav')

    def __init__(self, x, y, *groups):
        super().__init__(Rune.image, x, y, *groups)
        self.player = [i.rect for i in groups[1] if isinstance(i, Player)][0]
        self.speed_up_down = 10
        self.is_downing = False
        self.delta = 0
        self.calldown = 100

    def update(self, *args, **kwargs) -> None:
        if self.player.colliderect(self.rect):
            Rune.pick_up.play()
            self.kill()

        self.calldown -= 1000 / FPS
        if self.calldown <= 0:
            if not self.is_downing:
                self.rect.y -= 2
                self.delta -= 2
                if self.delta < -self.speed_up_down:
                    self.is_downing = True
                    self.delta = 0
            else:
                self.rect.y += 2
                self.delta += 2
                if self.delta > self.speed_up_down:
                    self.is_downing = False
                    self.delta = 0
            self.calldown = 100
