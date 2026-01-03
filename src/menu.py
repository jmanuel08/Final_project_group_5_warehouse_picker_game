"""
Menu system for the warehouse picker game.
Handles title screen, main menu, and settings menu.
"""

import pygame

class Button:
    """A clickable button for the menu."""
    
    def __init__(self, x, y, width, height, text, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (70, 130, 180)  # Default blue color
        self.hover_color = (100, 160, 210)
        self.click_color = (50, 100, 150)
        self.current_color = self.color
        self.is_hovered = False
        self.is_clicked = False
        self.was_clicked = False  # Track if button was clicked in this frame
        
        # Text
        self.font = pygame.font.Font(None, font_size)
        self.text_color = (255, 255, 255)
        self.text_surface = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def update(self, mouse_pos, mouse_pressed, mouse_clicked):
        """Update button state based on mouse position and clicks."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.was_clicked = False
        
        if self.is_hovered and mouse_clicked:  # Mouse was clicked this frame
            self.is_clicked = True
            self.current_color = self.click_color
            self.was_clicked = True
        elif self.is_hovered:
            self.is_clicked = False
            self.current_color = self.hover_color
        else:
            self.is_clicked = False
            self.current_color = self.color
        
        return self.was_clicked
    
    def draw(self, screen):
        """Draw the button on screen."""
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (30, 30, 30), self.rect, 3, border_radius=10)
        screen.blit(self.text_surface, self.text_rect)


class Slider:
    """A slider for volume control."""
    
    def __init__(self, x, y, width, height, min_value=0, max_value=100, initial_value=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.slider_rect = pygame.Rect(x, y, 20, height + 10)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.dragging = False
        
        # Calculate initial slider position
        self._update_slider_pos()
    
    def _update_slider_pos(self):
        """Update slider position based on current value."""
        value_range = self.max_value - self.min_value
        if value_range > 0:
            percentage = (self.value - self.min_value) / value_range
            self.slider_rect.centerx = self.rect.x + percentage * self.rect.width
    
    def update(self, mouse_pos, mouse_pressed):
        """Update slider value based on mouse interaction."""
        if mouse_pressed[0]:  # Left mouse button
            if self.slider_rect.collidepoint(mouse_pos):
                self.dragging = True
            elif self.rect.collidepoint(mouse_pos):
                # Clicked on bar, jump to that position
                self.dragging = True
        
        if self.dragging:
            if mouse_pressed[0]:
                # Constrain x position to slider bounds
                new_x = max(self.rect.left, min(mouse_pos[0], self.rect.right))
                self.slider_rect.centerx = new_x
                
                # Calculate value based on position
                percentage = (new_x - self.rect.left) / self.rect.width
                self.value = int(self.min_value + percentage * (self.max_value - self.min_value))
            else:
                self.dragging = False
        
        return self.value
    
    def draw(self, screen):
        """Draw the slider on screen."""
        # Draw slider bar
        pygame.draw.rect(screen, (80, 80, 80), self.rect, border_radius=5)
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2, border_radius=5)
        
        # Draw slider handle
        pygame.draw.rect(screen, (200, 200, 200), self.slider_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), self.slider_rect, 2, border_radius=5)
        
        # Draw value text
        font = pygame.font.Font(None, 24)
        value_text = font.render(f"{self.value}%", True, (255, 255, 255))
        value_rect = value_text.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
        screen.blit(value_text, value_rect)


class Menu:
    """Main menu system with title screen and settings."""
    
    def __init__(self, screen_width, screen_height, asset_loader, audio_manager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.asset_loader = asset_loader
        self.audio_manager = audio_manager
        
        # Game state
        self.current_state = "title"  # title, main_menu, settings
        
        # Load background image
        self.title_background = asset_loader.get_asset("title_background")
        if self.title_background:
            # Scale background to screen size if needed
            if self.title_background.get_size() != (screen_width, screen_height):
                self.title_background = pygame.transform.scale(self.title_background, (screen_width, screen_height))
        
        # Colors
        self.bg_color = (40, 40, 60)
        self.title_color = (255, 255, 100)
        self.text_color = (255, 255, 255)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.settings_font = pygame.font.Font(None, 36)
        
        # Create buttons for main menu
        button_width = 300
        button_height = 60
        center_x = screen_width // 2
        
        self.play_button = Button(
            center_x - button_width // 2, 
            screen_height // 2 - 40, 
            button_width, 
            button_height, 
            "Play",
            font_size=36
        )
        
        self.settings_button = Button(
            center_x - button_width // 2, 
            screen_height // 2 + 40, 
            button_width, 
            button_height, 
            "Settings",
            font_size=36
        )
        
        self.back_button = Button(
            50, 
            screen_height - 80, 
            150, 
            50, 
            "Back",
            font_size=28
        )
        
        # Create sliders for settings
        self.music_slider = Slider(
            center_x - 150,
            screen_height // 2 - 60,
            300,
            20,
            initial_value=int(audio_manager.music_volume * 100)
        )
        
        self.sfx_slider = Slider(
            center_x - 150,
            screen_height // 2 + 20,
            300,
            20,
            initial_value=int(audio_manager.sfx_volume * 100)
        )
        
        # Toggle buttons for settings
        self.fullscreen_button = Button(
            center_x - 150,
            screen_height // 2 + 100,
            300,
            50,
            "Windowed",
            font_size=28
        )
        
        self.music_toggle_button = Button(
            center_x + 170,
            screen_height // 2 - 60,
            150,
            50,
            "ON" if audio_manager.is_music_enabled else "OFF",
            font_size=24
        )
        
        self.sfx_toggle_button = Button(
            center_x + 170,
            screen_height // 2 + 20,
            150,
            50,
            "ON" if audio_manager.is_sfx_enabled else "OFF",
            font_size=24
        )
        
        # Mouse state tracking
        self.mouse_clicked = False
        self.mouse_was_pressed = False
    
    def update(self, mouse_pos, mouse_pressed):
        """Update menu state based on mouse input."""
        # Detect mouse click (button down this frame)
        self.mouse_clicked = mouse_pressed[0] and not self.mouse_was_pressed
        self.mouse_was_pressed = mouse_pressed[0]
        
        result = None
        
        if self.current_state == "main_menu":
            # Update buttons
            if self.play_button.update(mouse_pos, mouse_pressed, self.mouse_clicked):
                self.audio_manager.play_sound("button_click")
                result = "play"
            
            if self.settings_button.update(mouse_pos, mouse_pressed, self.mouse_clicked):
                self.audio_manager.play_sound("button_click")
                self.current_state = "settings"
                result = "settings"
        
        elif self.current_state == "settings":
            # Update back button
            if self.back_button.update(mouse_pos, mouse_pressed, self.mouse_clicked):
                self.audio_manager.play_sound("button_click")
                self.current_state = "main_menu"
                # Save settings when leaving settings menu
                self.audio_manager.save_settings()
                result = "back"
            
            # Update sliders
            music_volume = self.music_slider.update(mouse_pos, mouse_pressed)
            sfx_volume = self.sfx_slider.update(mouse_pos, mouse_pressed)
            
            # Update audio manager with new values
            self.audio_manager.set_music_volume(music_volume / 100.0)
            self.audio_manager.set_sfx_volume(sfx_volume / 100.0)
            
            # Update fullscreen button
            current_display = pygame.display.get_surface()
            is_fullscreen = current_display.get_flags() & pygame.FULLSCREEN
            button_text = "Fullscreen" if not is_fullscreen else "Windowed"
            self.fullscreen_button.text = button_text
            self.fullscreen_button.text_surface = self.fullscreen_button.font.render(
                button_text, True, self.fullscreen_button.text_color
            )
            
            if self.fullscreen_button.update(mouse_pos, mouse_pressed, self.mouse_clicked):
                self.audio_manager.play_sound("button_click")
                result = "toggle_fullscreen"
            
            # Update music toggle button
            music_toggle_text = "ON" if self.audio_manager.is_music_enabled else "OFF"
            self.music_toggle_button.text = music_toggle_text
            self.music_toggle_button.text_surface = self.music_toggle_button.font.render(
                music_toggle_text, True, self.music_toggle_button.text_color
            )
            
            if self.music_toggle_button.update(mouse_pos, mouse_pressed, self.mouse_clicked):
                self.audio_manager.play_sound("button_click")
                is_enabled = self.audio_manager.toggle_music()
                self.music_toggle_button.text = "ON" if is_enabled else "OFF"
                self.music_toggle_button.text_surface = self.music_toggle_button.font.render(
                    self.music_toggle_button.text, True, self.music_toggle_button.text_color
                )
            
            # Update SFX toggle button
            sfx_toggle_text = "ON" if self.audio_manager.is_sfx_enabled else "OFF"
            self.sfx_toggle_button.text = sfx_toggle_text
            self.sfx_toggle_button.text_surface = self.sfx_toggle_button.font.render(
                sfx_toggle_text, True, self.sfx_toggle_button.text_color
            )
            
            if self.sfx_toggle_button.update(mouse_pos, mouse_pressed, self.mouse_clicked):
                self.audio_manager.play_sound("button_click")
                is_enabled = self.audio_manager.toggle_sfx()
                self.sfx_toggle_button.text = "ON" if is_enabled else "OFF"
                self.sfx_toggle_button.text_surface = self.sfx_toggle_button.font.render(
                    self.sfx_toggle_button.text, True, self.sfx_toggle_button.text_color
                )
        
        return result
    
    def handle_events(self, events):
        """Handle events for the current menu state."""
        for event in events:
            if self.current_state == "title":
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.audio_manager.play_sound("button_click")
                    self.current_state = "main_menu"
                    return "title_continue"
        
        return None
    
    def draw_title_screen(self, screen):
        """Draw the title screen."""
        if self.title_background:
            screen.blit(self.title_background, (0, 0))
        else:
            screen.fill(self.bg_color)
            # Draw title
            title_text = self.title_font.render("WAREHOUSE PICKER", True, self.title_color)
            title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
            screen.blit(title_text, title_rect)
            
            # Draw instruction
            instruction_font = pygame.font.Font(None, 36)
            instruction = instruction_font.render("Press any key or click to continue", True, self.text_color)
            instruction_rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height * 2 // 3))
            screen.blit(instruction, instruction_rect)
    
    def draw_main_menu(self, screen):
        """Draw the main menu."""
        screen.fill(self.bg_color)
        
        # Draw title
        title_text = self.title_font.render("MAIN MENU", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        screen.blit(title_text, title_rect)
        
        # Draw buttons
        self.play_button.draw(screen)
        self.settings_button.draw(screen)
    
    def draw_settings(self, screen):
        """Draw the settings menu."""
        screen.fill(self.bg_color)
        
        # Draw title
        title_text = self.title_font.render("SETTINGS", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 6))
        screen.blit(title_text, title_rect)
        
        # Draw music volume label and slider
        music_label = self.settings_font.render("Music Volume:", True, self.text_color)
        music_rect = music_label.get_rect(midright=(self.screen_width // 2 - 160, self.music_slider.rect.centery))
        screen.blit(music_label, music_rect)
        
        self.music_slider.draw(screen)
        self.music_toggle_button.draw(screen)
        
        # Draw SFX volume label and slider
        sfx_label = self.settings_font.render("SFX Volume:", True, self.text_color)
        sfx_rect = sfx_label.get_rect(midright=(self.screen_width // 2 - 160, self.sfx_slider.rect.centery))
        screen.blit(sfx_label, sfx_rect)
        
        self.sfx_slider.draw(screen)
        self.sfx_toggle_button.draw(screen)
        
        # Draw fullscreen toggle
        fullscreen_label = self.settings_font.render("Display Mode:", True, self.text_color)
        fullscreen_rect = fullscreen_label.get_rect(midright=(self.screen_width // 2 - 160, self.fullscreen_button.rect.centery))
        screen.blit(fullscreen_label, fullscreen_rect)
        
        self.fullscreen_button.draw(screen)
        
        # Draw back button
        self.back_button.draw(screen)
    
    def draw(self, screen):
        """Draw the current menu screen."""
        if self.current_state == "title":
            self.draw_title_screen(screen)
        elif self.current_state == "main_menu":
            self.draw_main_menu(screen)
        elif self.current_state == "settings":
            self.draw_settings(screen)