# Main Application
import random
import tomllib

with open("./secrets.toml", "rb")as toml_file:
    secrets = tomllib.load(toml_file)

msg = secrets["personal"]["gender"]
print(msg)


import sys
import pygame

from utils import load_image, load_images, Animation
from entities import Player, Enemy, SlashAttack, XPOrb, FireColumnAttack, Fireball, HeartPickup



class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('awp')

       
        self.screen = pygame.display.set_mode((960, 540))

     
        self.display = pygame.Surface((960, 540))

        self.clock = pygame.time.Clock()

        self.movement = {
            'left': False,
            'right': False,
            'up': False,
            'down': False,
        }

        self.assets = {
            'title_screen': pygame.transform.scale(
                load_image('title.png'),
                (960, 540)
            ),
            'player': load_image('entities/player.png'),
            'background': load_image('base_background.png'),  # should be 1280x720
            'xp_orb': load_image('particles/xp.png'),
            'heart': pygame.transform.scale(
                load_image('particles/heart.png'),
                (20, 20)
            ),
            'enemy': load_image('entities/enemy.png'),
            'enemy_fast': load_image('entities/enemy_fast.png'),
            'enemy_tank': load_image('entities/enemy_tank.png'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'slash': Animation(load_images('attacks/slash'), img_dur=3, loop=False),
            'fire_column': Animation(load_images('particles/fire'), img_dur=4, loop=False),
            'fireball': Animation(load_images('particles/fireball'), img_dur=2),
        }


        self.player = Player(self, (480, 270), (24, 39))

        self.scroll = [0, 0]

        self.game_state = "title"
        
        self.enemy_kills = 0

        self.hearts = []

        self.enemies = []

        self.attacks = []
        
        self.enemy_spawn_timer = 0

        self.attack_timer = 0

        self.attack_cooldown = 90

        self.xp_orbs = []

        self.xp = 0

        self.level = 1

        self.xp = 0

        self.xp_needed = 5

        self.font = pygame.font.Font(None, 24)
    
        self.upgrade_font = pygame.font.Font(None, 16)   

        self.leveling_up = False

        self.level_up_choices = []

        self.fire_attacks = []

        self.fire_timer = 0

        self.fire_cooldown = 180

        self.fire_unlocked = False

        self.game_time = 0

        self.enemy_spawn_timer = 0

        self.enemy_spawn_cooldown = 120

        self.upgrade_counts = {}

        self.fire_stats = {
            'cooldown': 180, #180   
            'damage': 2, #2
            'hitbox_w': 50, #50
            'hitbox_h': 120, #120
            'scale_y': 1.3, 
            'stun': 10, #10 
        }

        self.fireballs = []

        self.fireball_timer = 0

        self.fireball_unlocked = False

        self.fireball_stats = {
            'cooldown': 180,
            'damage': 0.5,
            'speed': 2,
            'amount': 1,
        }

        self.upgrade_pool = [
            {'name': 'Bigger Slash', 'desc': '+31% slash width', 'stat': 'hitbox_w', 'amount': 25,  'max': 180},
            {'name': 'Taller Slash', 'desc': '+42% slash height', 'stat': 'hitbox_h', 'amount': 15,  'max': 90},
            {'name': 'Faster Attack', 'desc': '+17% attack speed', 'stat': 'cooldown', 'amount': -15, 'min': 45},
            {'name': 'Sharpened Slash', 'desc': '+50% slash damage', 'stat': 'damage', 'amount': 0.5, 'max': 7.5},

            {'name': 'Unlock Fire Column', 'desc': 'Gain a new fire attack', 'type': 'unlock_fire'},
            {'name': 'Stronger Fire', 'desc': '+25% fire damage', 'type': 'fire_stat', 'stat': 'damage', 'amount': 0.5,  'max': 15},
            {'name': 'Wider Fire', 'desc': '+20% fire width', 'type': 'fire_stat', 'stat': 'hitbox_w', 'amount': 10,  'max': 100},
            {'name': 'Taller Fire', 'desc': '+17% fire height', 'type': 'fire_stat', 'stat': 'hitbox_h', 'amount': 20,  'max': 240},
            {'name': 'Faster Fire', 'desc': '+11% fire rate', 'type': 'fire_stat', 'stat': 'cooldown', 'amount': -20,  'min': 60},
            {'name': 'Lingering Flames', 'desc': '+0.08s fire stun', 'type': 'fire_stat', 'stat': 'stun', 'amount': 5,  'max': 25},

            {'name': 'Unlock Fireball', 'desc': 'Gain a homing fireball attack', 'type': 'unlock_fireball'},
            {'name': 'Stronger Fireball', 'desc': '+50% fireball damage', 'type': 'fireball_stat', 'stat': 'damage', 'amount': 0.25, 'max': 1.5},
            {'name': 'Faster Fireball', 'desc': '+25% fireball speed', 'type': 'fireball_stat', 'stat': 'speed', 'amount': 0.5,  'max': 5},
            {'name': 'Extra Fireball', 'desc': '+1 fireball per attack', 'type': 'fireball_stat', 'stat': 'amount', 'amount': 1,  'max': 4},
            {'name': 'Rapid Fireball', 'desc': '+11% fireball fire rate', 'type': 'fireball_stat', 'stat': 'cooldown', 'amount': -20,  'min': 60},

            {'name': 'Vitality','desc': '+20 max hp','stat': 'max_health','amount': 20,'max': 200},
        ]

        self.weapon_stats = {
            'hitbox_w': 80, #80
            'hitbox_h': 36, #36
            'cooldown': 90, #90
            'damage': 1, #1
        }

    def spawn_enemy(self):

        px, py = self.player.pos

        spawn_w = 1050
        spawn_h = 650

        left = px - spawn_w // 2
        right = px + spawn_w // 2
        top = py - spawn_h // 2
        bottom = py + spawn_h // 2

        side = random.choice(['top', 'bottom', 'left', 'right'])

        if side == 'top':
            x = random.randint(int(left), int(right))
            y = int(top)
        elif side == 'bottom':
            x = random.randint(int(left), int(right))
            y = int(bottom)
        elif side == 'left':
            x = int(left)
            y = random.randint(int(top), int(bottom))
        else:
            x = int(right)
            y = random.randint(int(top), int(bottom))

        enemy_type = self.choose_enemy_type()
        self.enemies.append(Enemy(self, (x, y), enemy_type))

    def choose_enemy_type(self):
        seconds = self.game_time / 60

        if seconds < 1:
            return 'basic'

        elif seconds < 2:
            return random.choice(['basic', 'basic', 'fast', 'fast'])

        elif seconds < 3:
            return random.choice(['basic','fast', 'fast', 'tank'])

        else:
            return random.choice(['basic','fast', 'fast','tank', 'tank'])

    def get_nearest_enemy(self):
        nearest_enemy = None
        nearest_dist = float('inf')

        player_rect = self.player.rect()
        px = player_rect.centerx
        py = player_rect.centery

        for enemy in self.enemies:
            enemy_rect = enemy.rect()
            dx = enemy_rect.centerx - px
            dy = enemy_rect.centery - py
            dist = dx * dx + dy * dy

            if dist < nearest_dist:
                nearest_dist = dist
                nearest_enemy = enemy

        return nearest_enemy

    def upgrade_is_maxed(self, upgrade):
        stat = upgrade.get('stat')

        if stat is None:
            return False

        upgrade_type = upgrade.get('type')

        if upgrade_type == 'fire_stat':
            current = self.fire_stats[stat]

        elif upgrade_type == 'fireball_stat':
            current = self.fireball_stats[stat]

        else:
            if stat == 'max_health':
                current = self.player.max_health
            else:
                current = self.weapon_stats[stat]

        if 'max' in upgrade and current >= upgrade['max']:
            return True

        if 'min' in upgrade and current <= upgrade['min']:
            return True

        return False

    def start_level_up(self):
        self.leveling_up = True

        possible_upgrades = []

        for upgrade in self.upgrade_pool:

            if self.upgrade_is_maxed(upgrade):
                continue

            if upgrade.get('type') == 'unlock_fire':
                if self.level >= 5 and not self.fire_unlocked:
                    possible_upgrades.append(upgrade)

            elif upgrade.get('type') == 'fire_stat':
                if self.fire_unlocked:
                    possible_upgrades.append(upgrade)

            elif upgrade.get('type') == 'unlock_fireball':
                if self.level >= 5 and not self.fireball_unlocked:
                    possible_upgrades.append(upgrade)

            elif upgrade.get('type') == 'fireball_stat':
                if self.fireball_unlocked:
                    possible_upgrades.append(upgrade)

            else:
                possible_upgrades.append(upgrade)

        self.level_up_choices = random.sample(
            possible_upgrades,
            min(3, len(possible_upgrades))
        )

    def select_upgrade(self, index):
        upgrade = self.level_up_choices[index]
        upgrade_name = upgrade['name']

        if upgrade_name not in self.upgrade_counts:
            self.upgrade_counts[upgrade_name] = 0

        self.upgrade_counts[upgrade_name] += 1

        if upgrade.get('type') == 'unlock_fire':
            self.fire_unlocked = True

        elif upgrade.get('type') == 'fire_stat':
            stat = upgrade['stat']
            self.fire_stats[stat] += upgrade['amount']

            if self.fire_stats['cooldown'] < 40:
                self.fire_stats['cooldown'] = 40

        elif upgrade.get('type') == 'unlock_fireball':
            self.fireball_unlocked = True

        elif upgrade.get('type') == 'fireball_stat':
            stat = upgrade['stat']
            self.fireball_stats[stat] += upgrade['amount']

            if self.fireball_stats['cooldown'] < 30:
                self.fireball_stats['cooldown'] = 30

        else:
            stat = upgrade['stat']

            if stat == 'max_health':
                self.player.max_health += upgrade['amount']
                self.player.health += upgrade['amount']

                if self.player.health > self.player.max_health:
                    self.player.health = self.player.max_health

            else:
                self.weapon_stats[stat] += upgrade['amount']

            if self.weapon_stats['cooldown'] < 8:
                self.weapon_stats['cooldown'] = 8

        self.leveling_up = False
        self.level_up_choices = []

    def get_upgrade_display(self, upgrade):
        label_map = {
            'Bigger Slash': 'size',
            'Taller Slash': 'size',
            'Faster Attack': 'speed',
            'Sharpened Slash': 'dmg',

            'Stronger Fire': 'dmg',
            'Wider Fire': 'size',
            'Taller Fire': 'size',
            'Faster Fire': 'rate',
            'Lingering Flames': 'stun',

            'Stronger Fireball': 'dmg',
            'Faster Fireball': 'speed',
            'Extra Fireball': 'amt',
            'Rapid Fireball': 'rate',

            'Vitality': 'hp',   
        }

        count = self.upgrade_counts.get(upgrade['name'], 0)

        if count == 0:
            return None

        label = label_map[upgrade['name']]

        if label == 'amt':
            text = f"amt +{count}"

        elif label == 'hp':
            text = f"hp +{count * 20}"

        elif label == 'stun':
            text = f"stun +{count * 0.08:.1f}s"

        elif '%' in upgrade['desc']:
            percent = int(
                upgrade['desc'].split('%')[0]
                .replace('+', '')
                .replace('-', '')
            )

            text = f"{label} +{percent * count}%"

        else:
            text = f"{label} x{count}"

        if self.upgrade_is_maxed(upgrade):
            text += " MAX"

        return text

    def render_upgrade_gui(self):
        x = 860
        y = 10
        font = self.upgrade_font

        categories = {
            'SLASH': ['Bigger Slash', 'Taller Slash', 'Faster Attack', 'Sharpened Slash'],
            'FIRE': ['Stronger Fire', 'Wider Fire', 'Taller Fire', 'Faster Fire', 'Lingering Flames'],
            'FIREBALL': ['Stronger Fireball', 'Faster Fireball', 'Extra Fireball', 'Rapid Fireball'],
        }

        line_y = y

        for category, upgrades in categories.items():
            header = font.render(category, True, (255, 220, 80))
            self.display.blit(header, (x, line_y))
            line_y += 14

            if category == 'FIRE' and not self.fire_unlocked:
                txt = font.render("Not Unlocked", True, (120, 120, 120))
                self.display.blit(txt, (x + 8, line_y))
                line_y += 22
                continue

            if category == 'FIREBALL' and not self.fireball_unlocked:
                txt = font.render("Not Unlocked", True, (120, 120, 120))
                self.display.blit(txt, (x + 8, line_y))
                line_y += 22
                continue

            for upgrade in self.upgrade_pool:
                if upgrade['name'] not in upgrades:
                    continue

                text = self.get_upgrade_display(upgrade)
                if not text:
                    continue

                color = (220, 220, 220)
                if self.upgrade_is_maxed(upgrade):
                    color = (120, 255, 120)

                rendered = font.render(text, True, color)
                self.display.blit(rendered, (x + 8, line_y))
                line_y += 14

            line_y += 10
    


        

    def render_level_up_screen(self):
        overlay = pygame.Surface((960, 540))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.display.blit(overlay, (0, 0))

        title = self.font.render("LEVEL UP!", True, (255, 255, 255))
        self.display.blit(title, (420, 120))

        for i, upgrade in enumerate(self.level_up_choices):
            x = 220
            y = 190 + i * 80

            pygame.draw.rect(self.display, (60, 60, 60), (x, y, 520, 60))
            pygame.draw.rect(self.display, (255, 255, 255), (x, y, 520, 60), 2)

            text = self.font.render(f"{i + 1}. {upgrade['name']}", True, (255, 255, 255))
            desc = self.font.render(upgrade['desc'], True, (200, 200, 200))

            self.display.blit(text, (x + 20, y + 10))
            self.display.blit(desc, (x + 20, y + 35))

    
        
    def add_xp(self, amount):
        self.xp += amount

        while self.xp >= self.xp_needed:
            self.xp -= self.xp_needed
            self.level += 1
            self.xp_needed = int(self.xp_needed * 1.4)
            self.start_level_up()

    def render_title_screen(self):
        self.display.blit(
            self.assets['title_screen'],
            (0, 0)
        )

        text = self.font.render(
            "PRESS ENTER",
            True,
            (255, 255, 255)
        )

        self.display.blit(
            text,
            (
                400,
                500
            )
        )

    def render_death_screen(self):
        overlay = pygame.Surface((960, 540))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.display.blit(overlay, (0, 0))

        title = self.font.render("GAME OVER", True, (255, 80, 80))
        level_text = self.font.render(f"Level Reached: {self.level}", True, (255, 255, 255))
        kills_text = self.font.render(f"Enemies Killed: {self.enemy_kills}", True, (255, 255, 255))
        restart_text = self.font.render("Press ENTER to restart", True, (200, 200, 200))

        self.display.blit(title, (410, 190))
        self.display.blit(level_text, (390, 230))
        self.display.blit(kills_text, (390, 260))
        self.display.blit(restart_text, (380, 310))

    def render_pause_screen(self):
        overlay = pygame.Surface((960, 540))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.display.blit(overlay, (0, 0))

        title = self.font.render(
            "PAUSED",
            True,
            (255, 255, 255)
        )

        level_text = self.font.render(
            f"Level {self.level}",
            True,
            (220, 220, 220)
        )

        resume_text = self.font.render(
            "Press ENTER to Resume",
            True,
            (200, 200, 200)
        )

        self.display.blit(title, (430, 210))
        self.display.blit(level_text, (440, 250))
        self.display.blit(resume_text, (350, 310))



    def run(self):
        while True:
            bg = self.assets['background']
            # background and camera --------------------------------------------------------------------------
            # camera follows player
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 15
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 15

            # stop camera from going outside background
            self.scroll[0] = max(0, min(self.scroll[0], bg.get_width() - self.display.get_width()))
            self.scroll[1] = max(0, min(self.scroll[1], bg.get_height() - self.display.get_height()))

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # draw only the visible part of the 1280x720 background
            self.display.blit(
                bg,
                (0, 0),
                (render_scroll[0], render_scroll[1], self.display.get_width(), self.display.get_height())
            )

            dx = self.movement['right'] - self.movement['left']
            dy = self.movement['down'] - self.movement['up']


            # updates ------------------------------------------------------------------------------

            if self.game_state == "playing"and not self.leveling_up:

                self.game_time += 1

                

              #fireball
                if self.fireball_unlocked:
                    self.fireball_timer += 1

                    if self.fireball_timer >= self.fireball_stats['cooldown']:
                        self.fireball_timer = 0

                        count = self.fireball_stats['amount']
                        for i in range(count):
                            target = self.get_nearest_enemy()

                            if target:
                                fireball_pos = (
                                    self.player.rect().centerx,
                                    self.player.rect().centery
                                )

                                fireball_pos = (
                                    fireball_pos[0],
                                    fireball_pos[1] + (i - count // 2) * 8
                                )

                                self.fireballs.append(
                                    Fireball(
                                        self,
                                        fireball_pos,
                                        target,
                                        spread_index=i,
                                        spread_count=count
                                    )
                                )
              

                for fireball in self.fireballs[:]:
                    fireball.update()

                    if fireball.done:
                        self.fireballs.remove(fireball)

                for fireball in self.fireballs[:]:
                    for enemy in self.enemies[:]:
                        if fireball.rect().colliderect(enemy.rect()):
                            enemy.health -= self.fireball_stats['damage']
                            fireball.done = True

                            if enemy.health <= 0:
                                self.enemies.remove(enemy)
                                self.xp_orbs.append(
                                    XPOrb(self, enemy.pos)
                                )
                                self.enemy_kills += 1

                                if random.random() < 0.10:
                                    self.hearts.append(
                                        HeartPickup(self, enemy.pos)
                                    )

                            break

                #fire pillar


                if self.fire_unlocked:
                    self.fire_timer += 1

                    if self.fire_timer >= self.fire_stats['cooldown']:
                        self.fire_timer = 0

                        fire_pos = (
                            self.player.rect().centerx,
                            self.player.rect().centery
                        )

                        self.fire_attacks.append(
                            FireColumnAttack(self, fire_pos)
                        )

                for fire in self.fire_attacks[:]:
                    fire.update()

                    if fire.done:
                        self.fire_attacks.remove(fire)


                for fire in self.fire_attacks:
                    # pygame.draw.rect(
                    #     self.display,
                    #     (255, 0, 255),
                    #     (
                    #         fire.rect().x - render_scroll[0],
                    #         fire.rect().y - render_scroll[1],
                    #         fire.rect().width,
                    #         fire.rect().height
                    #     ),
                    #     1
                    # )
                    for enemy in self.enemies[:]:
                        if enemy in fire.hit_enemies:
                            continue

                        if fire.rect().colliderect(enemy.rect()):
                            fire.hit_enemies.add(enemy)

                            enemy.health -= self.fire_stats['damage']
                            enemy.stun_timer = self.fire_stats['stun']

                            if enemy.health <= 0:
                                self.enemies.remove(enemy)
                                self.xp_orbs.append(
                                    XPOrb(self, enemy.pos)
                                )
                                self.enemy_kills += 1

                                if random.random() < 0.10:
                                    self.hearts.append(
                                        HeartPickup(self, enemy.pos)
                                    )


                #slash attack

                self.attack_timer += 1

                if self.attack_timer >= self.weapon_stats['cooldown']:
                    self.attack_timer = 0

                    if self.player.flip:
                        slash_pos = (
                            self.player.pos[0] - 32,
                            self.player.pos[1] + 0
                        )
                        slash_flip = False
                    else:
                        slash_pos = (
                            self.player.pos[0] + 10,
                            self.player.pos[1] + 0
                        )
                        slash_flip = True
                        

                    self.attacks.append(
                        SlashAttack(
                            self,
                            slash_pos,
                            flip=slash_flip
                        )
                    )
                
                
                # UPDATE ATTACKS HERE
                for attack in self.attacks[:]:
                    attack.update()
                    # pygame.draw.rect(
                    #     self.display,
                    #     (255, 255, 0),
                    #     (
                    #         attack.rect().x - render_scroll[0],
                    #         attack.rect().y - render_scroll[1],
                    #         attack.rect().width,
                    #         attack.rect().height
                    #     ),
                    #     1
                    # )

                    if attack.done:
                        self.attacks.remove(attack)
                #attack collsion with enemy

                for attack in self.attacks:
                    for enemy in self.enemies[:]:
                        if enemy in attack.hit_enemies:
                            continue

                        if attack.rect().colliderect(enemy.rect()):

                            attack.hit_enemies.add(enemy)

                            enemy.health -= self.weapon_stats['damage']

                            if enemy.health <= 0:
                                self.enemies.remove(enemy)
                                self.xp_orbs.append(
                                    XPOrb(self, enemy.pos)
                                )
                                self.enemy_kills += 1

                                if random.random() < 0.10:
                                    self.hearts.append(
                                        HeartPickup(self, enemy.pos)
                                    )

                # enemies -----------------------------------------------------------------------------
                # spawn enemies

                seconds = self.game_time / 60

                if seconds >= 480:
                    extra_time = seconds - 480
                    self.enemy_spawn_cooldown = max(15, 60 - int(extra_time / 10))
                else:
                    self.enemy_spawn_cooldown = 60

                self.enemy_spawn_timer += 1

                if self.enemy_spawn_timer >= self.enemy_spawn_cooldown:
                    self.spawn_enemy()
                    self.enemy_spawn_timer = 0

                # update enemies

            
                for enemy in self.enemies:
                    enemy.update()
                    pygame.draw.rect(
                        self.display,
                        (0, 255, 0),
                        (
                            enemy.rect().x - render_scroll[0],
                            enemy.rect().y - render_scroll[1],
                            enemy.rect().width,
                            enemy.rect().height
                        ),
                        1
                    )
                    if enemy.rect().colliderect(self.player.rect()):
                        if self.player.damage_timer <= 0:
                            self.player.health -= 10
                            self.player.damage_timer = 30
                # xp orbs -------------------------------------------------------------------
                for orb in self.xp_orbs[:]:
                    collected = orb.update()

                    if collected:
                        self.xp_orbs.remove(orb)

                self.player.update((dx, dy))


                #hearts
                for heart in self.hearts[:]:
                    collected = heart.update()

                    if collected:
                        self.hearts.remove(heart)
                #death
                if self.player.health <= 0:
                    self.game_state = "game_over"

            

            # rendering ---------------------------------------------------------------

            entities = self.enemies + [self.player]
            entities.sort(key=lambda entity: entity.pos[1])

            for fire in self.fire_attacks:
                fire.render(self.display, offset=render_scroll)

            for orb in self.xp_orbs:
                orb.render(self.display, offset=render_scroll)


            for heart in self.hearts:
                heart.render(self.display, offset=render_scroll)

            for entity in entities:
                entity.render(self.display, offset=render_scroll)

            # pygame.draw.rect(
            #     self.display,
            #     (0, 255, 255),
            #     (
            #         self.player.rect().x - render_scroll[0],
            #         self.player.rect().y - render_scroll[1],
            #         self.player.rect().width,
            #         self.player.rect().height
            #     ),
            #     1
            # )

            for attack in self.attacks:
                attack.render(self.display, offset=render_scroll)

            for fireball in self.fireballs:
                fireball.render(self.display, offset=render_scroll)

            #health bar

            health_bar_x = 20
            health_bar_y = 20
            health_bar_w = 200
            health_bar_h = 20

            pygame.draw.rect(
                self.display,
                (80, 80, 80),
                (health_bar_x, health_bar_y, health_bar_w, health_bar_h)
            )

            pygame.draw.rect(
                self.display,
                (200, 0, 0),
                (
                    health_bar_x,
                    health_bar_y,
                    int(health_bar_w * self.player.health / self.player.max_health),
                    health_bar_h
                )
            )

            health_text = self.font.render(
                f"{int(self.player.health)}/{int(self.player.max_health)}",
                True,
                (255, 255, 255)
            )

            self.display.blit(
                health_text,
                (
                    health_bar_x + health_bar_w + 8,
                    health_bar_y - 2
                )
            )

            #xp bar
            bar_x = 20
            bar_y = 500
            bar_w = 300
            bar_h = 18

            xp_ratio = self.xp / self.xp_needed

            pygame.draw.rect(self.display, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))

            pygame.draw.rect(
                self.display,
                (0, 120, 255),
                (bar_x, bar_y, int(bar_w * xp_ratio), bar_h)
            )

            level_text = self.font.render(f"Level {self.level}", True, (255, 255, 255))
            self.display.blit(level_text, (bar_x, bar_y - 24))

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.game_state == "title":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.game_state = "playing"
                    continue

                

        

                if self.game_state == "game_over":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.__init__()
                    continue

                if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_n:
                           self.start_level_up()
                           self.level += 1
                                  

                if event.type == pygame.KEYDOWN:
                    if self.leveling_up:
                        if event.key == pygame.K_1:
                            self.select_upgrade(0)
                        if event.key == pygame.K_2:
                            self.select_upgrade(1)
                        if event.key == pygame.K_3:
                            self.select_upgrade(2)

                if self.game_state == "paused":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.game_state = "playing"
                    continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "paused"
                    if event.key == pygame.K_a:
                        self.movement['left'] = True
                    if event.key == pygame.K_d:
                        self.movement['right'] = True
                    if event.key == pygame.K_w:
                        self.movement['up'] = True
                    if event.key == pygame.K_s:
                        self.movement['down'] = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement['left'] = False
                    if event.key == pygame.K_d:
                        self.movement['right'] = False
                    if event.key == pygame.K_w:
                        self.movement['up'] = False
                    if event.key == pygame.K_s:
                        self.movement['down'] = False
            

            if self.game_state == "title":
                self.render_title_screen()

            elif self.game_state == "paused":
                self.render_pause_screen()

            elif self.game_state == "game_over":
                self.render_death_screen()

            if self.leveling_up:
                self.render_level_up_screen()

            self.render_upgrade_gui()


            self.screen.blit(self.display, (0, 0))
            pygame.display.update()
            self.clock.tick(60)


Game().run()