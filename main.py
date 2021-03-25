from math import pi, tan, atan2

import pygame
import sys
from settings import *
from sprites import *
from camera import *
from random import choice, randint


def load_map(level_map, player_hp=5):
    global player, height_lvl, width_lvl, door
    door_img = pygame.image.load('data/img/door.png')
    with open(level_map, mode='r') as file:
        data = list(file.readlines())
        height_lvl = len(data) * 32
        width_lvl = len(data[0].split()) * 32
        for row, line in enumerate(data):
            for col, block in enumerate(line.split()):
                if block in ['1', '2', '3', '4']:
                    Wall(col * WIDTH_BLOCK, row * HEIGHT_BLOCK,
                         all_sprites, blocks, key=block)
                if block in ['5', '6', '7', '8']:
                    Wall(col * WIDTH_BLOCK, row * HEIGHT_BLOCK,
                         all_sprites, blocks, key=block, is_angle=True)
                if block == '9':
                    Wall(col * WIDTH_BLOCK, row * HEIGHT_BLOCK,
                         all_sprites, blocks, is_send=True)
                if block == '10':
                    player = Player(col * WIDTH_BLOCK, row * HEIGHT_BLOCK,
                                    all_sprites, blocks=blocks, health=player_hp)
                    if '1' not in level_map:
                        Sprite(pygame.transform.scale2x(door_img), col * WIDTH_BLOCK,
                               row * HEIGHT_BLOCK, all_sprites)
                if block == '11':
                    Mob(col * WIDTH_BLOCK, row * HEIGHT_BLOCK,
                        all_sprites, enemies, blocks=blocks, bullets=bullets)
                if block == '12':
                    Rune(col * WIDTH_BLOCK, row * HEIGHT_BLOCK, runes, all_sprites)
                if block == '13':
                    door = Sprite(pygame.transform.scale2x(door_img), col * WIDTH_BLOCK,
                                  row * HEIGHT_BLOCK, all_sprites)
                elif block == ' ':
                    pass

    for i in range(-32 * 8, 0, 32):
        for j in range(-32 * 8, width_lvl + 32 * 8, 32):
            if randint(1, 15) == 8:
                Sprite(choice(treasures), j, i, all_sprites)

    for i in range(0, height_lvl, 32):
        for j in range(-32 * 8, 0, 32):
            if randint(1, 15) == 10:
                Sprite(choice(treasures), j, i, all_sprites)

    for i in range(height_lvl, height_lvl + 32 * 8, 32):
        for j in range(0, width_lvl, 32):
            if randint(1, 15) == 10:
                Sprite(choice(treasures), j, i, all_sprites)

    for i in range(0, height_lvl + 32 * 8, 32):
        for j in range(width_lvl, width_lvl + 32 * 8, 32):
            if randint(1, 15) == 10:
                Sprite(choice(treasures), j, i, all_sprites)


def draw_hp():
    for i in range(5):
        if player.hp > i:
            screen.blit(heart_img, (20 + i * (heart_img.get_width() + 2), 20))
        else:
            screen.blit(dead_heart_img, (20 + i * (dead_heart_img.get_width() + 2), 20))


def draw_count_of_runes():
    text = font.render(f'{picked_runes} / {count_of_runes}', True, (255, 255, 255))
    x = 20
    y = 60
    screen.blit(text, (x, y))
    x1 = (text.get_width() - rune_img.get_width()) // 2 + x
    screen.blit(rune_img, (x1, y + 20))


def draw_dialog():
    if picked_runes == count_of_runes:
        screen.blit(e_btn, (door.rect.x + 42, door.rect.y))
    else:
        text = font.render("you didn't collect all the runes", True, (255, 255, 255))
        x = (32 - text.get_width()) // 2 + door.rect.x
        y = door.rect.y - text.get_height() - 10
        screen.blit(text, (x, y))


def next_level(count):
    for sprite in all_sprites:
        sprite.kill()
    if player.hp > 0:
        load_map(f'data/lvls/lvl_{count}.txt', player_hp=player.hp)
    else:
        load_map(f'data/lvls/lvl_{count}.txt')


if __name__ == '__main__':

    pygame.init()
    pygame.display.set_caption('Soul in the pyramid')
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.mouse.set_visible(False)

    shot_cd = 300

    all_sprites = pygame.sprite.Group()
    blocks = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    runes = pygame.sprite.Group()

    font = pygame.font.Font('data/fonts/font.TTF', 20)

    treasures = [
        pygame.image.load('data/img/red_rubin.png'),
        pygame.image.load('data/img/green_rubin.png'),
        pygame.image.load('data/img/blue_rubin.png'),
        pygame.image.load('data/img/coins_4.png'),
        pygame.image.load('data/img/stick.png')
    ]

    music = pygame.mixer.Sound('data/sounds/music.wav')

    mouse_img = pygame.transform.scale(pygame.image.load('data/img/mouse.png'), (18, 18))
    heart_img = pygame.transform.scale2x(pygame.image.load('data/img/heart.png'))
    dead_heart_img = pygame.transform.scale2x(pygame.image.load('data/img/dead_heart.png'))
    rune_img = pygame.transform.scale2x(pygame.image.load('data/img/rune.png'))
    e_btn = pygame.image.load('data/img/e.png')

    shot = pygame.mixer.Sound('data/sounds/shot.wav')
    next_level_snd = pygame.mixer.Sound('data/sounds/next_level.wav')

    game_over_surf = pygame.surface.Surface(SCREEN_SIZE)
    text = 'Press any key to restart'
    text_rend = font.render(text, True, (255, 255, 255))
    text_pos = ((SCREEN_WIDTH - text_rend.get_width()) // 2,
                (SCREEN_HEIGHT - text_rend.get_height()) // 2)
    text_win = 'Congratulations! You completed the game!'
    text_win_rend = font.render(text_win, True, (255, 255, 255))
    text_win_pos = ((SCREEN_WIDTH - text_win_rend.get_width()) // 2,
                (SCREEN_HEIGHT - text_win_rend.get_height()) // 2 - text_rend.get_height() - 5)
    text_ng = 'Press any key to start new game'
    text_ng_rend = font.render(text_ng, True, (255, 255, 255))
    text_ng_pos = ((SCREEN_WIDTH - text_ng_rend.get_width()) // 2,
                (SCREEN_HEIGHT - text_ng_rend.get_height()) // 2 + 5)
    rect_game_over_surf = game_over_surf.get_rect()
    rect_game_over_surf.x = - SCREEN_WIDTH

    instr = pygame.image.load('data/img/instruction.png')
    rect_instr = instr.get_rect()
    rect_instr.x = 700
    rect_instr.y = 110

    win_sound = pygame.mixer.Sound('data/sounds/game_over.wav')
    is_playing = False

    camera = Camera()
    lvl_count = 1
    load_map(f'data/lvls/lvl_{lvl_count}.txt')
    lvl_rect = pygame.rect.Rect(0, 0, width_lvl, height_lvl)
    count_of_runes = len(runes)
    picked_runes = 0
    music.play(-1)
    max_lvl = 4
    end_game = False
    while running:

        if end_game:
            if not is_playing:
                win_sound.play(-1)
                is_playing = True
            music.stop()
            game_over_surf.fill((12, 12, 12))
            cpu_delay = clock.tick(FPS)
            cur_fps = clock.get_fps()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    win_sound.stop()
                    next_level_snd.play()
                    lvl_count = 1
                    player.hp = 0
                    next_level(lvl_count)
                    lvl_rect = pygame.rect.Rect(0, 0, width_lvl, height_lvl)
                    rect_instr.x = 700
                    rect_instr.y = 110
                    count_of_runes = len(runes)
                    picked_runes = 0
                    rect_game_over_surf.x = - SCREEN_WIDTH
                    music.play(-1)
                    end_game = False

            if rect_game_over_surf.right >= SCREEN_WIDTH:
                rect_game_over_surf.right = SCREEN_WIDTH
            else:
                rect_game_over_surf.x += 400 / FPS

            game_over_surf.blit(text_win_rend, text_win_pos)
            game_over_surf.blit(text_ng_rend, text_ng_pos)
            screen.blit(game_over_surf, (rect_game_over_surf.x, rect_game_over_surf.y))

            pygame.display.flip()

        else:
            if player.hp <= 0:
                music.stop()
                game_over_surf.fill((12, 12, 12))
                cpu_delay = clock.tick(FPS)
                cur_fps = clock.get_fps()

                for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        running = False

                    if event.type == pygame.KEYDOWN:
                        next_level_snd.play()
                        lvl_count = 1
                        next_level(lvl_count)
                        lvl_rect = pygame.rect.Rect(0, 0, width_lvl, height_lvl)
                        rect_instr.x = 700
                        rect_instr.y = 110
                        count_of_runes = len(runes)
                        picked_runes = 0
                        rect_game_over_surf.x = - SCREEN_WIDTH
                        music.play(-1)

                if rect_game_over_surf.right >= SCREEN_WIDTH:
                    rect_game_over_surf.right = SCREEN_WIDTH
                else:
                    rect_game_over_surf.x += 400 / FPS

                game_over_surf.blit(text_rend, text_pos)
                screen.blit(game_over_surf, (rect_game_over_surf.x, rect_game_over_surf.y))

                pygame.display.flip()
            else:

                screen.fill(SEND)

                cpu_delay = clock.tick(FPS)
                cur_fps = clock.get_fps()

                # rend = font.render('FPS ' + str(round(cur_fps)), True, DEEP_BLUE)

                shot_cd -= 1000 / FPS

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            player.jump()
                        if event.key == pygame.K_e:
                            if player.rect.colliderect(door.rect) and picked_runes == count_of_runes:
                                if lvl_count == max_lvl:
                                    end_game = True
                                else:
                                    next_level_snd.play()
                                    lvl_count += 1
                                    next_level(lvl_count)
                                    lvl_rect = pygame.rect.Rect(0, 0, width_lvl, height_lvl)
                                    count_of_runes = len(runes)
                                    picked_runes = 0
                        if event.key == pygame.K_f:
                            music.stop()
                            player.hp = 0
                            lvl_count = 1
                            next_level(lvl_count)
                            lvl_rect = pygame.rect.Rect(0, 0, width_lvl, height_lvl)
                            rect_instr.x = 700
                            rect_instr.y = 110
                            count_of_runes = len(runes)
                            picked_runes = 0
                            music.play(-1)

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and shot_cd < 0:
                        shot.play()
                        mouse_pos = [i + 9 for i in pygame.mouse.get_pos()]
                        rot = 180 / pi * atan2(- 1 * (mouse_pos[1] - player.rect.centery),
                                               (mouse_pos[0] - player.rect.centerx))
                        Bullet(player.rect.centerx, player.rect.centery - 10, rot, bullets, all_sprites,
                               blocks=blocks, enemies=enemies)
                        shot_cd = 300

                all_sprites.update(blocks)
                camera.update(player)

                for sprite in all_sprites:
                    camera.apply(sprite)

                lvl_rect.x += camera.dx
                lvl_rect.y += camera.dy

                rect_instr.x += camera.dx
                rect_instr.y += camera.dy

                pygame.draw.rect(screen, LIGHT_BLUE, lvl_rect)

                picked_runes = count_of_runes - len(runes)

                all_sprites.draw(screen)
                if lvl_count == 1:
                    screen.blit(instr, rect_instr)

                for enemy in enemies:
                    surf = pygame.surface.Surface((enemy.rect.width + 4, 4))
                    pygame.draw.rect(surf, (255, 255, 255), (0, 0, enemy.rect.width + 4, 4), 1)
                    rgb = [0, 0, 0]
                    if enemy.hp != 1:
                        rgb[1] = 255
                    if enemy.hp != 3:
                        rgb[0] = 255
                    if enemy.alive():
                        pygame.draw.rect(surf, rgb,
                                         (1, 1, (enemy.rect.width / enemy.max_hp * enemy.hp) + 3 if enemy.hp != enemy.max_hp else enemy.rect.width + 3,
                                          3), 1)
                        screen.blit(surf, (enemy.rect.x - 2, enemy.rect.y - 6))
                draw_hp()
                draw_count_of_runes()
                if player.rect.colliderect(door.rect):
                    draw_dialog()
                screen.blit(player.image, player.rect)
                screen.blit(mouse_img, (pygame.mouse.get_pos()))

            # screen.blit(rend, (0, 0))
            pygame.display.flip()

    pygame.quit()
