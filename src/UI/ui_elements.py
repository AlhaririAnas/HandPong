
import pygame
import time
import config


class MenuOption:
    """Single menu option with selection and confirmation timer."""
    
    def __init__(self, text, number, y_pos, action_code):
        self.text = text
        self.number = number
        self.y_pos = y_pos
        self.action_code = action_code
        
        # Selection state
        self.is_focused = False
        self.confirm_timer = 0.0
        self.is_confirmed = False
    
    def update(self, current_pose, dt):
        """
        Update menu option state.
        
        Returns: True if option was selected
        """
        # Check if this option matches the gesture
        gesture_number = current_pose if current_pose.isdigit() else None
        
        if gesture_number and int(gesture_number) == self.number:
            self.is_focused = True
            self.confirm_timer += dt
            
            # Check if held long enough to confirm
            if self.confirm_timer >= config.CONFIRM_HOLD_TIME:
                self.is_confirmed = True
                self.confirm_timer = 0.0
                return True
        else:
            self.is_focused = False
            self.confirm_timer = 0.0
            self.is_confirmed = False
        
        return False
    
    def draw(self, surface):
        """Draw menu option with visual feedback."""
        font_label = pygame.font.Font(None, 60)
        font_text = pygame.font.Font(None, 80)
        
        # Label (number)
        label = font_label.render(f"[{self.number}]", True, config.COLOR_TEXT_DIM)
        label_rect = label.get_rect(topleft=(400, self.y_pos))
        surface.blit(label, label_rect)
        
        # Option text
        color = config.COLOR_ACCENT_1 if self.is_focused else config.COLOR_TEXT
        text_surf = font_text.render(self.text, True, color)
        text_rect = text_surf.get_rect(topleft=(500, self.y_pos - 10))
        surface.blit(text_surf, text_rect)
        
        # Confirmation bar (countdown timer)
        if self.is_focused and self.confirm_timer > 0:
            bar_width = int((self.confirm_timer / config.CONFIRM_HOLD_TIME) * 300)
            bar_height = 8
            bar_x = 500
            bar_y = self.y_pos + 100
            
            # Background bar
            pygame.draw.rect(surface, config.COLOR_TEXT_DIM, (bar_x, bar_y, 300, bar_height))
            
            # Fill bar
            pygame.draw.rect(surface, config.COLOR_SUCCESS, (bar_x, bar_y, bar_width, bar_height))


class ConfirmationDialog:
    """Dialog for confirming critical actions."""
    
    def __init__(self, prompt_text):
        self.prompt_text = prompt_text
        self.yes_timer = 0.0
        self.no_timer = 0.0
        self.result = None  # 'yes', 'no', or None
    
    def update(self, current_pose, dt):
        """
        Update dialog state.
        
        current_pose: HandPose string (e.g., "open" for YES, "fist" for NO)
        Returns: 'yes', 'no', or None if not confirmed yet
        """
        # Check for YES gesture (open palm)
        if current_pose == "open" or current_pose == "5":
            self.yes_timer += dt
            self.no_timer = 0.0  # Reset NO timer
            
            if self.yes_timer >= config.CONFIRM_HOLD_TIME:
                self.result = 'yes'
                return 'yes'
        
        # Check for NO gesture (fist)
        elif current_pose == "fist" or current_pose == "0":
            self.no_timer += dt
            self.yes_timer = 0.0  # Reset YES timer
            
            if self.no_timer >= config.CONFIRM_HOLD_TIME:
                self.result = 'no'
                return 'no'
        
        else:
            # Gesture changed, reset timers
            self.yes_timer = 0.0
            self.no_timer = 0.0
        
        return None
    
    def draw(self, surface):
        """Draw confirmation dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_width = 600
        dialog_height = 400
        dialog_x = (config.WINDOW_WIDTH - dialog_width) // 2
        dialog_y = (config.WINDOW_HEIGHT - dialog_height) // 2
        
        pygame.draw.rect(surface, config.COLOR_UI_BG, (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(surface, config.COLOR_ACCENT_1, (dialog_x, dialog_y, dialog_width, dialog_height), 3)
        
        # Prompt text
        font_prompt = pygame.font.Font(None, 60)
        prompt_surf = font_prompt.render(self.prompt_text, True, config.COLOR_TEXT)
        prompt_rect = prompt_surf.get_rect(center=(config.WINDOW_WIDTH // 2, dialog_y + 80))
        surface.blit(prompt_surf, prompt_rect)
        
        # YES button (left)
        yes_color = config.COLOR_SUCCESS if self.yes_timer > 0 else config.COLOR_TEXT_DIM
        font_btn = pygame.font.Font(None, 50)
        yes_text = font_btn.render("YES", True, yes_color)
        yes_rect = yes_text.get_rect(center=(dialog_x + 150, dialog_y + 250))
        pygame.draw.rect(surface, yes_color, yes_rect.inflate(40, 40), 2)
        surface.blit(yes_text, yes_rect)
        
        # YES timer bar
        if self.yes_timer > 0:
            bar_width = int((self.yes_timer / config.CONFIRM_HOLD_TIME) * 200)
            pygame.draw.rect(surface, config.COLOR_SUCCESS, (dialog_x + 50, dialog_y + 320, bar_width, 10))
        
        # NO button (right)
        no_color = config.COLOR_WARNING if self.no_timer > 0 else config.COLOR_TEXT_DIM
        no_text = font_btn.render("NO", True, no_color)
        no_rect = no_text.get_rect(center=(dialog_x + 450, dialog_y + 250))
        pygame.draw.rect(surface, no_color, no_rect.inflate(40, 40), 2)
        surface.blit(no_text, no_rect)
        
        # NO timer bar
        if self.no_timer > 0:
            bar_width = int((self.no_timer / config.CONFIRM_HOLD_TIME) * 200)
            pygame.draw.rect(surface, config.COLOR_WARNING, (dialog_x + 350, dialog_y + 320, bar_width, 10))
        
        # Hand icons
        icon_font = pygame.font.Font(None, 40)
        yes_icon = icon_font.render("ðŸ‘‹", True, config.COLOR_SUCCESS)
        no_icon = icon_font.render("âœŠ", True, config.COLOR_WARNING)
        surface.blit(yes_icon, (dialog_x + 120, dialog_y + 340))
        surface.blit(no_icon, (dialog_x + 430, dialog_y + 340))
