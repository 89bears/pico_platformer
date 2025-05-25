"""
Picosystem Platform Game
A simple 2D platformer game for the Picosystem

Controls:
- Left/Right: Move player
- A Button: Jump
- X Button: Restart level
"""

import picosystem
import math
import random
import time

# Game constants
SCREEN_WIDTH = 120
SCREEN_HEIGHT = 120
GRAVITY = 0.5
JUMP_STRENGTH = -8
PLAYER_SPEED = 2

# Colors
BLACK = (0, 0, 0)        # 0
WHITE = (15, 15, 15)     # 15
RED = (15, 0, 0)         # 2
GREEN = (0, 15, 0)       # 3
BLUE = (0, 0, 15)        # 4
YELLOW = (15, 15, 0)     # 5
GRAY = (8, 8, 8)         # 7 (approximate mid-gray)
BROWN = (8, 4, 0)        # 9 (approximate brown)

class Player:
    """Player character with physics and controls"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.start_x = x
        self.start_y = y
    
    def update(self, platforms):
        """Update player physics and handle input"""
        # Handle input
        if picosystem.button(picosystem.LEFT):
            self.vel_x = -PLAYER_SPEED
        elif picosystem.button(picosystem.RIGHT):
            self.vel_x = PLAYER_SPEED
        else:
            self.vel_x = 0
        
        # Jump
        if picosystem.pressed(picosystem.A) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
        
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        #print("Player position:", self.x, self.y, "Velocity:", self.vel_x, self.vel_y, end='\r')
        
        # Handle collisions
        self.handle_collisions(platforms)
        
        # Keep player on screen horizontally
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
    
    def handle_collisions(self, platforms):
        """Handle collision detection with platforms"""
        player_rect = (self.x, self.y, self.width, self.height)
        self.on_ground = False
        
        for platform in platforms:
            if self.rect_collision(player_rect, platform.get_rect()):
                # Determine collision direction
                if self.vel_y > 0:  # Falling down
                    if self.y < platform.y:  # Landing on top
                        self.y = platform.y - self.height
                        self.vel_y = 0
                        self.on_ground = True
                elif self.vel_y < 0:  # Moving up
                    if self.y > platform.y:  # Hitting from below
                        self.y = platform.y + platform.height
                        self.vel_y = 0
    
    def rect_collision(self, rect1, rect2):
        """Check if two rectangles collide"""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        return (x1 < x2 + w2 and x1 + w1 > x2 and 
                y1 < y2 + h2 and y1 + h1 > y2)
    
    def reset(self):
        """Reset player to starting position"""
        self.x = self.start_x
        self.y = self.start_y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
    
    def draw(self):
        """Draw the player"""
        picosystem.pen(*RED)
        picosystem.frect(int(self.x), int(self.y), self.width, self.height)
        
        # Draw eyes
        picosystem.pen(*WHITE)
        picosystem.pixel(int(self.x + 2), int(self.y + 2))
        picosystem.pixel(int(self.x + 5), int(self.y + 2))


class Platform:
    """A platform that the player can stand on"""
    
    def __init__(self, x, y, width, height, color=BROWN):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def get_rect(self):
        """Get rectangle representation for collision detection"""
        return (self.x, self.y, self.width, self.height)
    
    def draw(self):
        """Draw the platform"""
        picosystem.pen(*self.color)
        picosystem.frect(self.x, self.y, self.width, self.height)


class Collectible:
    """Collectible items for the player to gather"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 6
        self.height = 6
        self.collected = False
        self.bob_offset = 0
        self.tick_counter = 0  # Add tick counter for animation
    
    def update(self):
        """Update collectible animation using ticks"""
        self.tick_counter += 1
        # Use sine wave with tick counter for smooth bobbing
        # Divide by larger number for slower animation, smaller for faster
        self.bob_offset = math.sin(self.tick_counter * 0.1) * 2
    
    def get_rect(self):
        """Get rectangle for collision detection"""
        return (self.x, self.y + self.bob_offset, self.width, self.height)
    
    def draw(self):
        """Draw the collectible"""
        if not self.collected:
            picosystem.pen(*YELLOW)
            y_pos = int(self.y + self.bob_offset)
            picosystem.frect(self.x, y_pos, self.width, self.height)
            
            # Draw shine effect
            picosystem.pen(*WHITE)
            picosystem.pixel(self.x + 1, y_pos + 1)


class Game:
    """Main game class"""
    
    def __init__(self):
        self.player = Player(20, 80)
        self.platforms = []
        self.collectibles = []
        self.score = 0
        self.setup_level()
    
    def setup_level(self):
        """Create the level layout"""
        # Ground platforms
        self.platforms.append(Platform(0, 110, 40, 10, GREEN))
        self.platforms.append(Platform(60, 110, 60, 10, GREEN))
        
        # Mid-level platforms
        self.platforms.append(Platform(30, 90, 20, 8))
        self.platforms.append(Platform(70, 80, 25, 8))
        self.platforms.append(Platform(15, 70, 20, 8))
        self.platforms.append(Platform(80, 60, 30, 8))
        
        # Upper platforms
        self.platforms.append(Platform(10, 50, 25, 8))
        self.platforms.append(Platform(50, 40, 30, 8))
        self.platforms.append(Platform(90, 30, 25, 8))
        
        # Top platform
        self.platforms.append(Platform(40, 20, 40, 8))
        
        # Add collectibles
        self.collectibles.append(Collectible(35, 82))
        self.collectibles.append(Collectible(78, 72))
        self.collectibles.append(Collectible(20, 62))
        self.collectibles.append(Collectible(88, 52))
        self.collectibles.append(Collectible(20, 42))
        self.collectibles.append(Collectible(65, 32))
        self.collectibles.append(Collectible(98, 22))
        self.collectibles.append(Collectible(55, 12))
    
    def update(self):
        """Update game state"""
        # Handle restart
        if picosystem.pressed(picosystem.X):
            self.restart_level()
            return
        
        # Update player
        self.player.update(self.platforms)
        
        # Update collectibles
        for collectible in self.collectibles:
            collectible.update()
            
            # Check collision with player
            if not collectible.collected:
                player_rect = (self.player.x, self.player.y, 
                             self.player.width, self.player.height)
                if self.player.rect_collision(player_rect, collectible.get_rect()):
                    collectible.collected = True
                    self.score += 10
        
        # Check if player fell off screen
        if self.player.y > SCREEN_HEIGHT + 20:
            self.restart_level()
    
    def restart_level(self):
        """Restart the current level"""
        self.player.reset()
        self.score = 0
        for collectible in self.collectibles:
            collectible.collected = False
    
    def draw(self):
        """Draw the game"""
        # Clear screen
        picosystem.pen(*BLUE)
        picosystem.clear()
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw()
        
        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw()
        
        # Draw player
        self.player.draw()
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        """Draw user interface elements"""
        # Draw score
        picosystem.pen(*WHITE)
        picosystem.text(f"Score: {self.score}", 2, 2)
        
        # Draw controls hint
        # picosystem.text("X: Restart", 2, SCREEN_HEIGHT - 10)
        
        # Check for level completion
        all_collected = all(c.collected for c in self.collectibles)
        if all_collected:
            picosystem.pen(*GREEN)
            picosystem.text("Level Complete!", 25, 60)
            picosystem.text("Press X to restart", 15, 70)


# Global game instance
game = Game()

def update(tick):
    """Main update function called by picosystem"""
    game.update()
    # Uncomment if you want to see a countdown
    #if tick % 10 == 0:
    #    print("Count down to auto quit: ", 1000 - tick, end='\r')

    # Auto quit after 1000 ticks
    if tick > 1000:
        quit()

def draw(tick):
    """Main draw function called by picosystem"""
    game.draw()



picosystem.start()
