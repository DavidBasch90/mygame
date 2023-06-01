import pygame
import sys
import logging
from classes import *

# Configure logging settings
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(),
                              logging.FileHandler('./output/game.log', mode='w')])


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





# Create game objects



move1 = Battle.Move("Tackle", 10, 0.95)
move2 = Battle.Move("Scratch", 8, 0.9)
move3 = Battle.Move("Tail Whip", 5, 1.0)

# Create monster instances
player_monster1 = Monster(100, 100, pygame.image.load("./assets/images/player_monster1.png"), "Player Monster 1", 1, 20, 10, [move1, move2, move3])
player_monster2 = Monster(200, 100, pygame.image.load("./assets/images/player_monster2.png"), "Player Monster 2", 1, 20, 10,[move1, move2, move3])

npc_monster1 = Monster(300, 100, pygame.image.load("./assets/images/npc_monster1.png"), "NPC Monster 1", 1000, 200, 10,[move1, move2, move3])
npc_monster2 = Monster(400, 100, pygame.image.load("./assets/images/npc_monster2.png"), "NPC Monster 2", 1000, 200, 10,[move1, move2, move3])

# Create game objects
player = Player(400, 300)
player.team = [player_monster1, player_monster2]  # Add monsters to the player's team

npcs = pygame.sprite.Group()
npcs.add(NPC(200, 200, "Hello! How are you?","You're decent...", [npc_monster1], logging))
npcs.add(NPC(600, 400, "Welcome to our town!", "You suck!", [npc_monster2], logging))

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Map")

# Set up the clock
clock = pygame.time.Clock()

# Game loop
running = True
battle_active = False
interacting_npc = None
battle_npc = None
WHITE = (255, 255, 255)
game_over = False

game_clock = GameClock()  # Game time clock
while running:
    clock.tick(FPS)
    #dt = clock.tick(FPS) / 1000  # Amount of seconds since last frame
    #game_clock.update(dt)


    # In your game loop:
    current_time = game_clock.get_time()



    keys = pygame.key.get_pressed()
    # Handle events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            logging.info('QUIT GAME')
            running = False
        if event.type == pygame.KEYDOWN:
            logging.info('keydown')
            if game_over:

                running = False

            if interacting_npc:
                print(interacting_npc.dialogue_state)
            if interacting_npc and interacting_npc.dialogue_state == "defeated":
                interacting_npc.key_pressed_after_defeat = True
                interacting_npc = None

            if event.key == pygame.K_z and not battle_active:
                logging.info('non battle key press: z')
                print(interacting_npc)
                if interacting_npc is None:
                    collided_npcs = pygame.sprite.spritecollide(player, npcs, False)
                    print(collided_npcs)
                    for npc in collided_npcs:
                        interacting_npc = npc
                        logging.info('npc interacting with player')
                        print('a npc is interacting')
                        interacting_npc.interact(player, screen, font)

            if interacting_npc:
                if interacting_npc:
                    if event.key == pygame.K_y:
                        logging.info('player says yes to battle')
                        if interacting_npc.dialogue_state == "wait_for_answer":
                            interacting_npc.dialogue_state = "battle"
                            battle = interacting_npc.interact(player, screen, font)
                            if battle:
                                battle_active = True
                                battle_npc = interacting_npc

                    if event.key == pygame.K_n:
                        logging.info('player says no to battle')
                        if interacting_npc.dialogue_state == "wait_for_answer":
                            interacting_npc.dialogue_state = "ask"
                            interacting_npc = None  # Add this line

    # Update game objects
    if not battle_active:
        player.update(keys)

    if game_over:
        screen.fill((255, 255, 255))  # Fill the screen with white color
        game_over_text = font.render("GAME OVER", True, (0, 0, 0))  # Create a "GAME OVER" text
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))  # Draw the "GAME OVER" text in the center of the screen
        pygame.display.flip()  # Update the display to show the "GAME OVER" message

        continue  # Skip the rest of the loop
    if battle_active:
        battle.handle_input(events)
        battle_done = battle.update(events)

        if battle_done is True:
            logging.info('ending battle')
            battle_active = False
            if not battle.npc_team:  # Check if the NPC team is empty
                logging.info('empty team for npc')
                battle.display_end_battle_message(screen, font, "You Win!")
                if battle_npc is not None:  # Check if battle_npc is not None
                    logging.info('npc defeated check')
                    battle_npc.defeated = True
                    battle_npc.dialogue_state = "defeated"
                battle_npc = None  # Reset battle_npc to None

                if interacting_npc is not None:  # Add this check
                    logging.info('npc defeated check')
                    interacting_npc.defeated = True
                    interacting_npc.dialogue_state = "defeated"
                    interacting_npc.end_interaction()
                    interacting_npc = None
            else:

                battle.display_end_battle_message(screen, font, "You Lose!")  # Display losing message

                game_over = True  # Set the game state to 'game over'


    # Draw everything
    if not battle_active:
        screen.blit(map_img, (0, 0))
        screen.blit(player.image, player.rect)
        npcs.draw(screen)




        if interacting_npc:
            state_text = font.render(f"Dialogue State: {interacting_npc.dialogue_state}", True, WHITE)

            if interacting_npc.dialogue_state == "wait_for_answer":
                interacting_npc.render_text(screen,
                                            interacting_npc.current_message + " Do you want to battle? (Y/N)")
            elif interacting_npc.dialogue_state == "ask" or interacting_npc.dialogue_state == "defeated":
                interacting_npc.render_text(screen, interacting_npc.current_message)


    else:
        battle.draw(screen)

    # Update the display
    time_text = font.render(str(game_clock.get_time()), True, (255, 255, 255))  # Render the time as white text
    screen.blit(time_text, (WIDTH - time_text.get_width(), 0))  # Draw the text at the top right of the screen

    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()

