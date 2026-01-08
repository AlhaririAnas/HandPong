import sys
import time
import pygame
import config

from src.UI.ui_elements import MenuOption, ConfirmationDialog


def get_current_pose_from_keys():
    keys = pygame.key.get_pressed()
    # number keys 0-9
    for i in range(10):
        if keys[getattr(pygame, f'K_{i}')]:
            return str(i)
    # open / fist emulation
    if keys[pygame.K_o]:
        return "open"
    if keys[pygame.K_f]:
        return "fist"
    return ""


def main():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("HandPong - UI Preview")
    clock = pygame.time.Clock()

    # Create some menu options
    options = [
        MenuOption("NEW GAME", 1, 250, "new_game"),
        MenuOption("OPTIONS", 2, 380, "options"),
        MenuOption("EXIT", 3, 510, "exit"),
    ]

    active_dialog = None
    selected_option = None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        current_pose = get_current_pose_from_keys()

        # If a dialog is active, update it
        if active_dialog:
            res = active_dialog.update(current_pose, dt)
            if res == 'yes':
                if selected_option and selected_option.action_code == 'exit':
                    running = False
                active_dialog = None
                selected_option = None
            elif res == 'no':
                active_dialog = None
                selected_option = None

        else:
            # Update menu options
            for opt in options:
                chosen = opt.update(current_pose, dt)
                if chosen:
                    # show confirmation dialog for this option
                    selected_option = opt
                    active_dialog = ConfirmationDialog(f"Select {opt.text} ?")
                    break

        # Draw
        screen.fill(config.COLOR_BG)

        for opt in options:
            opt.draw(screen)

        if active_dialog:
            active_dialog.draw(screen)

        # Help text
        small = pygame.font.Font(None, 28)
        help_text = small.render("Press keys 1-3 or hold 'o' (open) / 'f' (fist). ESC to quit.", True, config.COLOR_TEXT_DIM)
        screen.blit(help_text, (40, config.WINDOW_HEIGHT - 40))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
