import pygame
import math

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (0, 0)
        self.flip = False
        self.set_action('idle')
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
        
    def update(self, movement=(0, 0)):
        self.pos[0] += movement[0]
        self.pos[1] += movement[1]

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(
            pygame.transform.flip(self.animation.img(), self.flip, False),
            (
                self.pos[0] - offset[0] + self.anim_offset[0],
                self.pos[1] - offset[1] + self.anim_offset[1]
            )
        )
        
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.max_health = 100
        self.health = 100
        self.damage_timer = 0
    
    def update(self, movement=(0, 0)):
        super().update(movement=movement)

        if self.damage_timer > 0:
            self.damage_timer -= 1

        bg = self.game.assets['background']

        self.pos[0] = max(
            0,
            min(
                self.pos[0],
                bg.get_width() - self.size[0]
            )
        )

        self.pos[1] = max(
            0,
            min(
                self.pos[1],
                bg.get_height() - self.size[1]
            )
        )

        if movement[0] != 0 or movement[1] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

class Enemy:
    def __init__(self, game, pos, enemy_type='basic'):
        self.game = game
        self.pos = list(pos)
        self.enemy_type = enemy_type
        self.flip = False
        self.stun_timer = 0

        if enemy_type == 'fast':
            self.image_key = 'enemy_fast'
            self.size = (19, 29)
            self.speed = 0.8
            self.max_health = 2

        elif enemy_type == 'tank':
            self.image_key = 'enemy_tank'
            self.size = (19, 29)
            self.speed = 0.4
            self.max_health = 15

        else:
            self.image_key = 'enemy'
            self.size = (19, 29)
            self.speed = 0.4
            self.max_health = 3

        self.health = self.max_health

    def rect(self):
        return pygame.Rect(
            self.pos[0],
            self.pos[1],
            self.size[0],
            self.size[1]
        )

    def update(self):
        if self.stun_timer > 0:
            self.stun_timer -= 1
            return
        player_rect = self.game.player.rect()
        player_x = player_rect.centerx
        player_y = player_rect.centery 

        enemy_rect = self.rect()
        enemy_x = enemy_rect.centerx
        enemy_y = enemy_rect.centery

        dx = player_x - enemy_x
        dy = player_y - enemy_y 

        if dx > 0:
            self.flip = True
        if dx < 0:
            self.flip = False

        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance != 0:
            dx /= distance
            dy /= distance

            self.pos[0] += dx * self.speed
            self.pos[1] += dy * self.speed

    def render(self, surf, offset=(0, 0)):
        img = pygame.transform.flip(
            self.game.assets[self.image_key],
            self.flip,
            False
        )
        surf.blit(
            img,
            (
                self.pos[0] - offset[0],
                self.pos[1] - offset[1]
            )
        )
        if self.health < self.max_health:
            bar_w = 24
            bar_h = 4

            x = self.pos[0] - offset[0]
            y = self.pos[1] - offset[1] - 8

            health_ratio = self.health / self.max_health

            pygame.draw.rect(
                surf,
                (60, 60, 60),
                (x, y, bar_w, bar_h)
            )

            pygame.draw.rect(
                surf,
                (200, 0, 0),
                (x, y, int(bar_w * health_ratio), bar_h)
            )

class SlashAttack:
    def __init__(self, game, pos, flip=False):
        self.game = game
        self.pos = list(pos)
        self.flip = flip
        self.animation = self.game.assets['slash'].copy()
        self.done = False
        self.hit_enemies = set()

    def update(self):
        self.animation.update()

        if self.animation.done:
            self.done = True

    def render(self, surf, offset=(0, 0)):
        hitbox = self.rect()

        base_img = self.animation.img()

        base_w = 80
        base_h = 36

        scale_x = self.game.weapon_stats['hitbox_w'] / base_w
        scale_y = self.game.weapon_stats['hitbox_h'] / base_h

        img = pygame.transform.scale(
            base_img,
            (
                int(base_img.get_width() * scale_x*1.7),
                int(base_img.get_height() * scale_y)
            )
        )

        if self.flip:
            img = pygame.transform.flip(img, True, False)

        if self.flip:
            draw_x = hitbox.centerx - img.get_width() // 2 + 10
        else:
            draw_x = hitbox.centerx - img.get_width() // 2 - 10

        draw_y = hitbox.centery - img.get_height() // 2 

        surf.blit(
            img,
            (
                draw_x - offset[0],
                draw_y - offset[1]
            )
        )
    def rect(self):
        w = self.game.weapon_stats['hitbox_w']
        h = self.game.weapon_stats['hitbox_h']

        base_w = 80
        base_h = 36

        extra_w = w - base_w
        extra_h = h - base_h

        if self.flip:
            return pygame.Rect(
                self.pos[0] - 12,
                self.pos[1] + 3 - extra_h // 2,
                w,
                h
            )
        else:
            return pygame.Rect(
                self.pos[0] - 20 - extra_w,
                self.pos[1] + 2 - extra_h // 2,
                w,
                h
            )



class FireColumnAttack:
    def __init__(self, game, pos):
        self.game = game
        self.pos = list(pos)
        self.animation = self.game.assets['fire_column'].copy()
        self.done = False
        self.hit_enemies = set()

    def rect(self):
        w = self.game.fire_stats['hitbox_w']
        h = self.game.fire_stats['hitbox_h']

        return pygame.Rect(
            self.pos[0] - w // 2,
            self.pos[1] - h // 2,
            w,
            h
        )

    def update(self):
        self.animation.update()

        if self.animation.done:
            self.done = True

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()

        base_w = 50
        base_h = 120

        scale_x = self.game.fire_stats['hitbox_w'] / base_w
        scale_y = self.game.fire_stats['hitbox_h'] / base_h

        img = pygame.transform.scale(
            img,
            (
                int(img.get_width() * scale_x),
                int(img.get_height() * scale_y * self.game.fire_stats['scale_y'])
            )
        )

        surf.blit(
            img,
            (
                self.pos[0] - img.get_width() // 2 - offset[0],
                self.pos[1] - img.get_height() // 2 - offset[1]
            )
        )

class Fireball:
    def __init__(self, game, pos, target, spread_index=0, spread_count=1):
        self.game = game
        self.pos = list(pos)
        self.target = target
        self.animation = self.game.assets['fireball'].copy()
        self.done = False
        self.spread_index = spread_index
        self.spread_count = spread_count

    def rect(self):
        return pygame.Rect(
            self.pos[0] - 8,
            self.pos[1] - 4,
            16,
            8
        )

    def update(self):
        self.animation.update()

        if self.target not in self.game.enemies:
            self.target = self.game.get_nearest_enemy()

            if self.target is None:
                self.done = True
                return

        target_rect = self.target.rect()

        dx = target_rect.centerx - self.pos[0]
        dy = target_rect.centery - self.pos[1]

        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance != 0:
            dx /= distance
            dy /= distance

            if self.spread_count > 1:

                angle = math.atan2(dy, dx)

                spread = math.radians(10)

                offset = (
                    self.spread_index
                    - (self.spread_count - 1) / 2
                ) * spread

                angle += offset

                dx = math.cos(angle)
                dy = math.sin(angle)

            self.pos[0] += dx * self.game.fireball_stats['speed']
            self.pos[1] += dy * self.game.fireball_stats['speed']

        player_rect = self.game.player.rect()

        if abs(self.pos[0] - player_rect.centerx) > 900:
            self.done = True
        if abs(self.pos[1] - player_rect.centery) > 700:
            self.done = True

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()

        if self.target:
            target_rect = self.target.rect()
            if target_rect.centerx > self.pos[0]:
                img = pygame.transform.flip(img, True, False)

        surf.blit(
            img,
            (
                self.pos[0] - img.get_width() // 2 - offset[0],
                self.pos[1] - img.get_height() // 2 - offset[1]
            )
        )
class XPOrb:
    def __init__(self, game, pos, value=1):
        self.game = game
        self.pos = list(pos)
        self.value = value
        self.size = self.game.assets['xp_orb'].get_size()
        self.speed = 3

    def rect(self):
        return pygame.Rect(
            self.pos[0],
            self.pos[1],
            self.size[0],
            self.size[1]
        )

    def update(self):
        player_rect = self.game.player.rect()

        if self.rect().colliderect(player_rect):
            self.game.add_xp(self.value)
            return True

        return False

    def render(self, surf, offset=(0, 0)):
        surf.blit(
            self.game.assets['xp_orb'],
            (
                self.pos[0] - offset[0],
                self.pos[1] - offset[1]
            )
        )

class HeartPickup:
    def __init__(self, game, pos):
        self.game = game
        self.pos = list(pos)

        self.size = self.game.assets['heart'].get_size()

    def rect(self):
        return pygame.Rect(
            self.pos[0],
            self.pos[1],
            self.size[0],
            self.size[1]
        )

    def update(self):
        if self.rect().colliderect(
            self.game.player.rect()
        ):
            self.game.player.health = min(
                self.game.player.max_health,
                self.game.player.health + 20
            )

            return True

        return False

    def render(self, surf, offset=(0, 0)):
        surf.blit(
            self.game.assets['heart'],
            (
                self.pos[0] - offset[0],
                self.pos[1] - offset[1]
            )
        )