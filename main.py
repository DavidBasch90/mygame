import pygame
import sys
import logging
from classes import *

# Configure logging settings
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(),
                              logging.FileHandler('./output/game.log', mode='w')])

TILESIZE = 16
# Initialize Pygame
pygame.init()
# Initialize Pygame Font
pygame.font.init()
font = pygame.font.Font(None, 36)

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 30

# Load Images
SCALE_FACTOR = 2
player_img = pygame.image.load("./assets/images/player.png")
player_img = pygame.transform.scale(player_img, (player_img.get_width() * SCALE_FACTOR, player_img.get_height() * SCALE_FACTOR))
npc_img = pygame.image.load("./assets/images/npc.png")
npc_img = pygame.transform.scale(npc_img, (npc_img.get_width() * SCALE_FACTOR, npc_img.get_height() * SCALE_FACTOR))
map_img = pygame.image.load("./assets/images/map.png")





# Create game objects



move1 = Battle.Move("Tackle", 10, 0.95)
move2 = Battle.Move("Scratch", 8, 0.9)
move3 = Battle.Move("Tail Whip", 5, 1.0)

# Create monster instances
player_monster1 = Monster(100, 100, pygame.image.load("./assets/images/player_monster1.png"), "Player Monster 1", 200, 20, 10, [move1, move2, move3])
player_monster2 = Monster(200, 100, pygame.image.load("./assets/images/player_monster2.png"), "Player Monster 2", 200, 20, 10,[move1, move2, move3])

npc_monster1 = Monster(300, 100, pygame.image.load("./assets/images/npc_monster1.png"), "NPC Monster 1", 200, 20, 10,[move1, move2, move3])
npc_monster2 = Monster(400, 100, pygame.image.load("./assets/images/npc_monster2.png"), "NPC Monster 2", 200, 20, 10,[move1, move2, move3])

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


# Load the sprite sheet
sprite_sheet = pygame.image.load('./assets/images/GRASS+.png')
village_sheet = pygame.image.load('./assets/images/SERENE_VILLAGE_REVAMPED/Serene_Village_16x16.png')

# Define the rectangle that corresponds to the location of the  sprite on the sprite sheet
# Replace x, y, width, and height with the actual values
grass_rect = pygame.Rect(167, 95, 16, 16)
stump_rect = pygame.Rect(160, 192, 16, 16)
flower_rect = pygame.Rect(96,192, 16,16)
house_rect = pygame.Rect(95,335,60,60)
pond_rect = pygame.Rect(176,0, 47,50)

# Extract the  sprite
grass_image = village_sheet.subsurface(grass_rect)
stump_image = sprite_sheet.subsurface(stump_rect)
stump_image = pygame.transform.scale(stump_image, (stump_image.get_width() * SCALE_FACTOR, stump_image.get_height() * SCALE_FACTOR))
flower_image = sprite_sheet.subsurface(flower_rect)
flower_image = pygame.transform.scale(flower_image, (flower_image.get_width() * SCALE_FACTOR, flower_image.get_height() * SCALE_FACTOR))
house_image = village_sheet.subsurface(house_rect)
house_image = pygame.transform.scale(house_image, (house_image.get_width() * SCALE_FACTOR, house_image.get_height() * SCALE_FACTOR))
pond_image = village_sheet.subsurface(pond_rect)
pond_image = pygame.transform.scale(pond_image, (pond_image.get_width() * SCALE_FACTOR, pond_image.get_height() * SCALE_FACTOR))

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
        # Assuming TILE_SIZE is the size of your grass sprite
        for y in range(0, HEIGHT, TILESIZE):
            for x in range(0, WIDTH, TILESIZE):
                screen.blit(grass_image, (x, y))

        log_positions = [(90, 89), (200, 300), (500, 400)]
        flower_positions = [(0, 100), (200, 100), (300, 100), (200, 200), (300, 200), (400, 200), (0, 300)]
        house_positions = [(0,100),(200,100),(100,200), (300,200)]
        # Blit each log at its position
        for pos in log_positions:
            screen.blit(stump_image, pos)
        for pos in flower_positions:
            screen.blit(flower_image, pos)
        for pos in house_positions:
            screen.blit(house_image, pos)
        screen.blit(pond_image, (200,330))

        screen.blit(player.image, player.rect)
        npcs.draw(screen)




        if interacting_npc:
            state_text = font.render(f"Dialogue State: {interacting_npc.dialogue_state}", True, WHITE)

            if interacting_npc.dialogue_state == "wait_for_answer":
                interacting_npc.render_text(screen,
                                            interacting_npc.current_message + " Do you want to battle? (Y/N)")
            elif interacting_npc.dialogue_state == "ask" or interacting_npc.dialogue_state == "defeated":
                interacting_npc.render_text(screen, interacting_npc.defeated_message)


    else:
        battle.draw(screen)

    # Update the display
    time_text = font.render(str(game_clock.get_time()), True, (255, 255, 255))  # Render the time as white text
    screen.blit(time_text, (WIDTH - time_text.get_width(), 0))  # Draw the text at the top right of the screen

    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()

