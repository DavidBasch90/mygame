import pygame
import sys

# Initialize Pygame
pygame.init()
# Initialize Pygame Font
pygame.font.init()
font = pygame.font.Font(None, 36)

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 30

# Load Images
player_img = pygame.image.load("./assets/images/player.png")
npc_img = pygame.image.load("./assets/images/npc.png")
map_img = pygame.image.load("./assets/images/map.png")
#import the images
player_img = pygame.image.load("./assets/images/player.png")
npc_img = pygame.image.load("./assets/images/npc.png")
map_img = pygame.image.load("./assets/images/map.png")


class GameClock:
    def __init__(self):
        self.start_time = pygame.time.get_ticks()

    def get_time(self):
        return (pygame.time.get_ticks() - self.start_time) / 1000  # Time in seconds




class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, image, name, health, attack, defense, moves):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.moves = moves



# Player and NPC classes
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.team = []

    def update(self, keys):
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, message, defeated_message, team,logger):
        super().__init__()
        self.image = npc_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.message = message
        self.defeated_message = defeated_message  # Add this line
        self.dialogue_state = "ask"
        self.current_message = None
        self.team = team
        self.defeated = False
        self.logger = logger
        self.key_pressed_after_defeat = False

    def interact(self, player, screen, font):
        self.logger.info(f'Interact method called. Current dialogue state: {self.dialogue_state}')
        if self.dialogue_state == "defeated":
            self.render_text(screen, self.defeated_message)
            return
        if self.dialogue_state == "ask":
            if self.defeated:
                if self.current_message is None:
                    self.current_message = self.defeated_message
                else:
                    self.current_message = None
                    self.key_pressed_after_defeat = False
            else:
                self.current_message = self.message
                self.dialogue_state = "wait_for_answer"
                self.logger.info('npc dialogue: wait for answer')
        elif self.dialogue_state == "battle":
            return self.start_battle(player, screen, font)
            self.logger.info('battle starting')
        elif self.dialogue_state == "defeated":
            if self.current_message is None:
                self.current_message = self.defeated_message
            else:
                self.current_message = None
                self.key_pressed_after_defeat = False
        self.logger.info(f'Interact method finished. Final dialogue state: {self.dialogue_state}')

    def end_interaction(self):
        self.interacting = False

    def interactbackup(self,player,screen,font):
        print(self.dialogue_state)
        if self.dialogue_state == "ask":
            if self.defeated:
                self.current_message = "You're pretty good..."
                self.dialogue_state = "defeated"
            else:
                self.current_message = self.message
                self.dialogue_state = "wait_for_answer"
                self.logger.info('npc dialogue: wait for answer')
        elif self.dialogue_state == "wait_for_answer":
            self.dialogue_state = "battle"
            self.logger.info('npc dialogue: battle')
        elif self.dialogue_state == "battle":
            return self.start_battle(player, screen, font)
            self.logger.info('battle starting')
        elif self.dialogue_state == "defeated":
            self.dialogue_state = "ask"


    def start_battle(self, player,screen,font):
        return Battle(player.team, self.team, screen, font)

    def render_text(self, screen, text):
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (50, 50))

import random
def render_text(screen, font, text, x, y, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

class Battle:
    def __init__(self, player_team, npc_team, screen, font):
        self.player_team = player_team
        self.npc_team = npc_team
        self.state = "waiting_for_input"
        self.current_monster = 0
        self.menu_state = "main"
        self.screen = screen
        self.font = font
        self.ui = BattleUI(font)
        self.main_menu = Menu(["Fight", "Items"], 200, 400, font)
        self.moves_menu = None
        self.player_selected_move = False

    def display_end_battle_message(self, screen, font, message):
        text = font.render(message, True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        pygame.display.update()
        pygame.time.wait(2000)  # Wait for 2 seconds so the player can read the message
    def is_npc_defeated(self):
        return len(self.npc_team) == 0

    def draw(self, screen):
        screen.fill((0, 0, 0))  # Fill the screen with black color

        if self.player_team:
            player_monster = self.player_team[0]
            screen.blit(player_monster.image, (100, 300))  # Draw player's active monster
            self.ui.draw_health_bar(screen, 100, 330, player_monster.health / 100)  # Draw player monster health bar

        if self.npc_team:
            npc_monster = self.npc_team[0]
            screen.blit(npc_monster.image, (500, 100))  # Draw NPC's active monster
            self.ui.draw_health_bar(screen, 500, 130, npc_monster.health / 100)  # Draw NPC monster health bar

        # Draw battle menu
        if self.state == "waiting_for_input":
            if self.menu_state == "main":
                self.main_menu.draw(screen)
            elif self.menu_state == "moves":
                if self.moves_menu is None:
                    moves = [move.name for move in self.player_team[0].moves]
                    self.moves_menu = Menu(moves, 200, 400, self.font)
                self.moves_menu.draw(screen)

    def use_move(self, attacker, move_name, defender):
        for move in attacker.moves:
            if move.name == move_name:
                damage = int(attacker.attack * move.power - defender.defense)
                defender.health = max(defender.health - damage, 0)
                break

    class Move:
        def __init__(self, name, power, accuracy):
            self.name = name
            self.power = power
            self.accuracy = accuracy

        def use(self, attacker, defender):
            if random.random() < self.accuracy:
                damage = int(attacker.attack * self.power - defender.defense)
                defender.health = max(defender.health - damage, 0)
            else:
                print(f"{attacker.name}'s attack missed!")

    def handle_input(self, events):
        # Iterate through the list of events
        for event in events:
            # Check if the event is a key press
            if event.type == pygame.KEYDOWN:
                # Check if the UP arrow key was pressed
                if event.key == pygame.K_UP:
                    # Navigate up in the current menu
                    menu = self.main_menu if self.menu_state == "main" else self.moves_menu
                    menu.navigate(-1)
                # Check if the DOWN arrow key was pressed
                elif event.key == pygame.K_DOWN:
                    # Navigate down in the current menu
                    menu = self.main_menu if self.menu_state == "main" else self.moves_menu
                    menu.navigate(1)

                # Check if the 'Z' key was pressed
                elif event.key == pygame.K_z:
                    # If the menu state is 'main'
                    if self.menu_state == "main":
                        selected_item = self.main_menu.get_selected_item()
                        # If the selected item is 'Fight', switch to the moves menu
                        if selected_item == "Fight":
                            self.menu_state = "moves"
                            moves = [move.name for move in self.player_team[0].moves]
                            self.moves_menu = Menu(moves, 200, 400, self.font)
                        # If the selected item is 'Items', handle item usage (not implemented yet)
                        elif selected_item == "Items":
                            pass
                    # If the menu state is 'moves'



                # Check if the 'X' key was pressed
                elif event.key == pygame.K_x:
                    # If the menu state is 'moves', go back to the main menu
                    if self.menu_state == "moves":
                        self.menu_state = "main"

    def update(self, events):
        battle_done = False
        if not self.player_team or not self.npc_team:
            if not self.npc_team:
                print("Player wins! WE ARE IN UPDATE")
            elif not self.player_team:
                print("NPC wins!")
            return True

        if self.state == "npc_turn":
            current_monster = self.npc_team[self.current_monster]
            move_name = random.choice(self.npc_team[0].moves).name
            self.use_move(current_monster, move_name, self.player_team[0])
            if self.player_team[0].health == 0:
                self.player_team.pop(0)
                print('player team:',)
                if not self.player_team:
                    print("NPC wins!")
                    return
                else:
                    self.state = "waiting_for_input"
            else:  # Add this else statement
                self.state = "waiting_for_input"



        elif self.state == "waiting_for_input":
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                    # Check if the menu state is 'moves'
                    if self.menu_state == "moves":
                        if not self.player_selected_move:
                            self.player_selected_move = True
                        else:
                            current_monster = self.player_team[self.current_monster]
                            selected_move = self.moves_menu.get_selected_item()
                            self.use_move(current_monster, selected_move, self.npc_team[0])

                            if self.npc_team[0].health == 0:
                                self.npc_team.pop(0)  # Remove defeated monster
                                print(self.npc_team)
                                if not self.npc_team:
                                    print("Player wins! WE ARE IN UPDATE2")
                                    return

                            self.state = "npc_turn"
                            self.player_selected_move = False

        return None


class Menu:
    def __init__(self, items, x, y, font):
        self.items = items
        self.x = x
        self.y = y
        self.font = font
        self.selected_item = 0

    def draw(self, screen):
        for i, item in enumerate(self.items):
            color = (255, 255, 255) if i != self.selected_item else (255, 255, 0)
            render_text(screen, self.font, item, self.x, self.y + i * 50, color)

    def navigate(self, direction):
        self.selected_item = (self.selected_item + direction) % len(self.items)

    def get_selected_item(self):
        return self.items[self.selected_item]

class BattleUI:
    def __init__(self, font):
        self.font = font

    def draw_health_bar(self, screen, x, y, health_percentage):
        pygame.draw.rect(screen, (255, 0, 0), (x, y, 100, 10))  # Red background
        pygame.draw.rect(screen, (0, 255, 0), (x, y, 100 * health_percentage, 10))  # Green health bar

    def draw_main_menu(self, screen, menu):
        menu.draw(screen)

    def draw_moves_menu(self, screen, menu):
        menu.draw(screen)
