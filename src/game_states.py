"""
Game state management for the warehouse picker game.
Handles transitions between different game states.
"""

import pygame
import sys

class GameState:
    """Base class for game states."""
    
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.screen_width = game.SCREEN_WIDTH
        self.screen_height = game.SCREEN_HEIGHT
    
    def handle_events(self, events):
        """Handle events for this state."""
        pass
    
    def update(self, delta_time):
        """Update logic for this state."""
        pass
    
    def draw(self):
        """Draw this state."""
        pass


class TitleState(GameState):
    """Title screen state."""
    
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(None, 72)
        self.instruction_font = pygame.font.Font(None, 36)
        
        # Colors
        self.title_color = (255, 255, 100)
        self.text_color = (255, 255, 255)
        self.bg_color = (40, 40, 60)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # Play sound if available
                if hasattr(self.game, 'audio_manager'):
                    self.game.audio_manager.play_sound("button_click")
                return "main_menu"
        return None
    
    def draw(self):
        self.screen.fill(self.bg_color)
        
        # Draw title
        title_text = self.title_font.render("WAREHOUSE PICKER", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        self.screen.blit(title_text, title_rect)
        
        # Draw instruction
        instruction = self.instruction_font.render("Press any key or click to continue", True, self.text_color)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height * 2 // 3))
        self.screen.blit(instruction, instruction_rect)


class MenuState(GameState):
    """Main menu state."""
    
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 36)
        
        # Colors
        self.title_color = (255, 255, 100)
        self.button_color = (70, 130, 180)
        self.button_hover_color = (100, 160, 210)
        self.bg_color = (40, 40, 60)
        
        # Create buttons
        button_width = 300
        button_height = 60
        center_x = self.screen_width // 2
        
        self.play_button = pygame.Rect(
            center_x - button_width // 2, 
            self.screen_height // 2 - 40, 
            button_width, 
            button_height
        )
        
        self.settings_button = pygame.Rect(
            center_x - button_width // 2, 
            self.screen_height // 2 + 40, 
            button_width, 
            button_height
        )
        
        self.quit_button = pygame.Rect(
            center_x - button_width // 2, 
            self.screen_height // 2 + 120, 
            button_width, 
            button_height
        )
    
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button.collidepoint(mouse_pos):
                    if hasattr(self.game, 'audio_manager'):
                        self.game.audio_manager.play_sound("button_click")
                    return "play"
                elif self.settings_button.collidepoint(mouse_pos):
                    if hasattr(self.game, 'audio_manager'):
                        self.game.audio_manager.play_sound("button_click")
                    return "settings"
                elif self.quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
        
        return None
    
    def draw(self):
        self.screen.fill(self.bg_color)
        
        # Draw title
        title_text = self.title_font.render("MAIN MENU", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        self.screen.blit(title_text, title_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        
        # Play button
        play_color = self.button_hover_color if self.play_button.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, play_color, self.play_button, border_radius=10)
        pygame.draw.rect(self.screen, (30, 30, 30), self.play_button, 3, border_radius=10)
        play_text = self.button_font.render("Play", True, (255, 255, 255))
        play_text_rect = play_text.get_rect(center=self.play_button.center)
        self.screen.blit(play_text, play_text_rect)
        
        # Settings button
        settings_color = self.button_hover_color if self.settings_button.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, settings_color, self.settings_button, border_radius=10)
        pygame.draw.rect(self.screen, (30, 30, 30), self.settings_button, 3, border_radius=10)
        settings_text = self.button_font.render("Settings", True, (255, 255, 255))
        settings_text_rect = settings_text.get_rect(center=self.settings_button.center)
        self.screen.blit(settings_text, settings_text_rect)
        
        # Quit button
        quit_color = self.button_hover_color if self.quit_button.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, quit_color, self.quit_button, border_radius=10)
        pygame.draw.rect(self.screen, (30, 30, 30), self.quit_button, 3, border_radius=10)
        quit_text = self.button_font.render("Quit", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)