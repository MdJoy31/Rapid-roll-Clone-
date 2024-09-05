import pygame
import random
import time
import sys
import os
import json

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Frames per second
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player properties
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5
PLAYER_JUMP_SPEED = 15
GRAVITY = 0.8

# Platform properties
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
PLATFORM_SPEED = 2
DISAPPEAR_DURATION = 5

# Obstacle properties
OBSTACLE_SIZE = 40

# Power-up properties
POWERUP_SIZE = 30
POWERUP_DURATION = 5  # seconds

# Asset paths
ASSET_DIR = 'assets/'
BACKGROUND_IMAGES = [
    os.path.join(ASSET_DIR, 'background1.png'),
    os.path.join(ASSET_DIR, 'background2.png'),
    os.path.join(ASSET_DIR, 'background3.png'),
    os.path.join(ASSET_DIR, 'background4.png')
]
PLAYER_IMAGE = os.path.join(ASSET_DIR, 'player_character.png')
PLATFORM_IMAGE = os.path.join(ASSET_DIR, 'platform.png')
LADDER_IMAGE = os.path.join(ASSET_DIR, 'ladder.png')
LEVEL_UP_IMAGE = os.path.join(ASSET_DIR, 'level_up.png')

# Obstacle images
OBSTACLE_IMAGES = {
    'spike': os.path.join(ASSET_DIR, 'spike.png'),
    'bomb': os.path.join(ASSET_DIR, 'bomb.png'),
    'moving_saw': os.path.join(ASSET_DIR, 'moving_saw.png'),
    'falling_rock': os.path.join(ASSET_DIR, 'falling_rock.png'),
    'rolling_barrel': os.path.join(ASSET_DIR, 'rolling_barrel.png'),
    'fireball': os.path.join(ASSET_DIR, 'fireball.png')
}

# Power-up images
POWERUP_IMAGES = {
    'extra_life': os.path.join(ASSET_DIR, 'extra_life.png'),
    'bonus_star': os.path.join(ASSET_DIR, 'bonus_star.png'),
    'power_ball': os.path.join(ASSET_DIR, 'power_ball.png'),
    'time_extension': os.path.join(ASSET_DIR, 'time_extension.png'),
    'shield': os.path.join(ASSET_DIR, 'shield.png'),
    'double_score': os.path.join(ASSET_DIR, 'double_score.png')
}

# Sound effects (optional)
JUMP_SOUND = os.path.join(ASSET_DIR, 'jump.wav')
POWERUP_SOUND = os.path.join(ASSET_DIR, 'powerup.wav')
GAME_OVER_SOUND = os.path.join(ASSET_DIR, 'game_over.wav')

# High Score file
HIGH_SCORE_FILE = 'high_scores.json'

# Font settings
FONT_NAME = pygame.font.match_font('arial')
FONT_SIZE = 24

def load_image(path, width=None, height=None):
    """Utility function to load and scale images."""
    try:
        image = pygame.image.load(path).convert_alpha()
        if width and height:
            image = pygame.transform.scale(image, (width, height))
        return image
    except pygame.error as e:
        print(f"Error loading image {path}: {e}")
        sys.exit(1)

def load_sound(path):
    """Utility function to load sound effects."""
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        print(f"Error loading sound {path}: {e}")
        return None

class Player(pygame.sprite.Sprite):
    """Class representing the player character."""
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image(PLAYER_IMAGE, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity_y = 0
        self.speed = PLAYER_SPEED
        self.jump_speed = PLAYER_JUMP_SPEED
        self.lives = 3
        self.score = 0
        self.powered_up = False
        self.power_up_time = 0
        self.shielded = False
        self.shield_time = 0
        self.double_score = False
        self.double_score_time = 0

        # Load sounds
        self.jump_sound = load_sound(JUMP_SOUND)
        self.powerup_sound = load_sound(POWERUP_SOUND)
        self.game_over_sound = load_sound(GAME_OVER_SOUND)

    def update(self, platforms):
        self.handle_input()
        self.apply_gravity()
        self.check_collisions(platforms)
        self.update_power_up_status()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_SPACE]:
            self.jump()

    def jump(self):
        self.rect.y += 1  # Move down slightly to check for platform
        hits = pygame.sprite.spritecollide(self, game.platforms, False)
        self.rect.y -= 1  # Move back to original position
        if hits:
            self.velocity_y = -self.jump_speed
            if self.jump_sound:
                self.jump_sound.play()

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        if self.rect.bottom > SCREEN_HEIGHT:
            self.lives -= 1
            self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.velocity_y = 0
            if self.lives <= 0 and self.game_over_sound:
                self.game_over_sound.play()

    def check_collisions(self, platforms):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and self.velocity_y > 0:
            self.rect.bottom = hits[0].rect.top
            self.velocity_y = 0

    def update_power_up_status(self):
        current_time = time.time()
        if self.powered_up and current_time - self.power_up_time > POWERUP_DURATION:
            self.powered_up = False
            self.speed = PLAYER_SPEED
        if self.shielded and current_time - self.shield_time > POWERUP_DURATION:
            self.shielded = False
        if self.double_score and current_time - self.double_score_time > POWERUP_DURATION:
            self.double_score = False

    def power_up(self, power_type):
        if power_type == 'extra_life':
            self.lives += 1
        elif power_type == 'bonus_star':
            self.score += 100 if not self.double_score else 200
        elif power_type == 'power_ball':
            self.powered_up = True
            self.power_up_time = time.time()
            self.speed = PLAYER_SPEED + 3
        elif power_type == 'time_extension':
            game.time_left += 30
        elif power_type == 'shield':
            self.shielded = True
            self.shield_time = time.time()
        elif power_type == 'double_score':
            self.double_score = True
            self.double_score_time = time.time()

class Platform(pygame.sprite.Sprite):
    """Class representing platforms."""
    def __init__(self, x, y, moving=False, direction=1, range=100, disappearing=False):
        super().__init__()
        self.image = load_image(PLATFORM_IMAGE, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.moving = moving
        self.direction = direction
        self.range = range
        self.start_x = x
        self.speed = PLATFORM_SPEED
        self.disappearing = disappearing
        self.disappear_start_time = None

    def update(self):
        if self.moving:
            self.rect.x += self.speed * self.direction
            if abs(self.rect.x - self.start_x) > self.range:
                self.direction *= -1
        if self.disappearing:
            if self.disappear_start_time is None:
                self.disappear_start_time = time.time()
            elif time.time() - self.disappear_start_time > DISAPPEAR_DURATION:
                self.kill()  # Platform disappears
class Obstacle(pygame.sprite.Sprite):
    """Class representing obstacles."""
    def __init__(self, x, y, obstacle_type):
        super().__init__()
        self.image = load_image(OBSTACLE_IMAGES[obstacle_type], OBSTACLE_SIZE, OBSTACLE_SIZE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = obstacle_type
        self.speed = random.randint(2, 5)
        self.direction = random.choice([-1, 1])

    def update(self):
        if self.type == 'moving_saw':
            self.rect.x += self.speed * self.direction
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.direction *= -1
        elif self.type == 'falling_rock':
            self.rect.y += self.speed
            if self.rect.top > SCREEN_HEIGHT:
                self.rect.y = random.randint(-100, -40)
                self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        elif self.type == 'rolling_barrel':
            self.rect.x += self.speed * self.direction
            if self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
                self.direction *= -1
        elif self.type == 'fireball':
            self.rect.y += self.speed
            if self.rect.top > SCREEN_HEIGHT:
                self.rect.y = random.randint(-100, -40)
                self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        elif self.type == 'bomb':
            self.rect.y += self.speed
            if self.rect.top > SCREEN_HEIGHT:
                self.rect.y = random.randint(-100, -40)
                self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        elif self.type == 'spike':
            pass  # Spikes are stationary

class PowerUp(pygame.sprite.Sprite):
    """Class representing power-ups."""
    def __init__(self, x, y, power_type):
        super().__init__()
        self.image = load_image(POWERUP_IMAGES[power_type], POWERUP_SIZE, POWERUP_SIZE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = power_type

    def update(self):
        pass  # Power-ups are stationary

class UIManager:
    """Class to manage UI elements."""
    def __init__(self):
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)

    def draw(self, screen, player, time_left):
        lives_text = self.font.render(f'Lives: {player.lives}', True, WHITE)
        score_text = self.font.render(f'Score: {player.score}', True, WHITE)
        time_text = self.font.render(f'Time Left: {int(time_left)}s', True, WHITE)
        shield_text = self.font.render(f'Shield: {"Active" if player.shielded else "Inactive"}', True, WHITE)
        double_score_text = self.font.render(f'Double Score: {"Active" if player.double_score else "Inactive"}', True, WHITE)
        screen.blit(lives_text, (10, 10))
        screen.blit(score_text, (10, 40))
        screen.blit(time_text, (10, 70))
        screen.blit(shield_text, (10, 100))
        screen.blit(double_score_text, (10, 130))

    def draw_level_up(self, screen, level):
        level_text = self.font.render(f'Level {level}!', True, WHITE)
        level_up_image = load_image(LEVEL_UP_IMAGE, 400, 100)
        screen.blit(level_up_image, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150))
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, SCREEN_HEIGHT // 2 - level_text.get_height() // 2))

    def draw_game_over(self, screen, score):
        game_over_text = self.font.render('GAME OVER', True, WHITE)
        final_score_text = self.font.render(f'Final Score: {score}', True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))

class HighScoreManager:
    """Class to manage high scores."""
    def __init__(self):
        self.scores = self.load_scores()

    def load_scores(self):
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as f:
                return json.load(f)
        else:
            return []

    def save_scores(self):
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(self.scores, f)

    def add_score(self, name, score):
        self.scores.append({'name': name, 'score': score})
        self.scores = sorted(self.scores, key=lambda x: x['score'], reverse=True)[:10]
        self.save_scores()

    def draw(self, screen):
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        title_text = font.render('High Scores', True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        for idx, score in enumerate(self.scores):
            score_text = font.render(f"{idx + 1}. {score['name']} - {score['score']}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 150 + idx * 30))
class Game:
    """Main game class."""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Rapid Roll Clone')
        self.clock = pygame.time.Clock()
        self.running = True
        self.level = 1
        self.time_left = 120  # seconds per level
        self.start_time = time.time()
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.ui_manager = UIManager()
        self.high_score_manager = HighScoreManager()
        self.backgrounds = [load_image(bg, SCREEN_WIDTH, SCREEN_HEIGHT) for bg in BACKGROUND_IMAGES]
        self.background = self.backgrounds[0]
        self.generate_level()
        self.state = 'playing'

    def generate_level(self):
        self.all_sprites.empty()
        self.platforms.empty()
        self.obstacles.empty()
        self.powerups.empty()
        self.all_sprites.add(self.player)
        # Generate platforms
        for i in range(10 + self.level * 2):
            x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT - PLATFORM_HEIGHT)
            moving = random.choice([True, False])
            disappearing = random.choice([True, False])
            platform = Platform(x, y, moving=moving, disappearing=disappearing)
            self.all_sprites.add(platform)
            self.platforms.add(platform)
        # Generate obstacles
        for i in range(5 + self.level):
            x = random.randint(0, SCREEN_WIDTH - OBSTACLE_SIZE)
            y = random.randint(-300, -40)
            obstacle_type = random.choice(list(OBSTACLE_IMAGES.keys()))
            obstacle = Obstacle(x, y, obstacle_type)
            self.all_sprites.add(obstacle)
            self.obstacles.add(obstacle)
        # Generate power-ups
        for i in range(3):
            x = random.randint(0, SCREEN_WIDTH - POWERUP_SIZE)
            y = random.randint(-300, -40)
            power_type = random.choice(list(POWERUP_IMAGES.keys()))
            powerup = PowerUp(x, y, power_type)
            self.all_sprites.add(powerup)
            self.powerups.add(powerup)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

    def update(self):
        if self.state == 'playing':
            self.player.update(self.platforms)
            self.platforms.update()
            self.obstacles.update()
            self.powerups.update()
            self.check_collisions()
            self.update_time()
            self.update_background()
            self.spawn_platforms_and_obstacles()
            if self.player.lives <= 0:
                self.state = 'game_over'

    def spawn_platforms_and_obstacles(self):
        # Check if the player is near the top of the screen and spawn new platforms and obstacles
        if self.player.rect.top <= SCREEN_HEIGHT / 2:
            # Adjust all sprites downwards to simulate upward movement
            for sprite in self.all_sprites:
                sprite.rect.y += PLAYER_SPEED

            # Generate new platforms and obstacles at the top of the screen
            if len(self.platforms) < 10 + self.level * 2:
                x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
                y = random.randint(-PLATFORM_HEIGHT, 0)
                platform = Platform(x, y, moving=random.choice([True, False]), disappearing=random.choice([True, False]))
                self.all_sprites.add(platform)
                self.platforms.add(platform)

            if len(self.obstacles) < 5 + self.level:
                x = random.randint(0, SCREEN_WIDTH - OBSTACLE_SIZE)
                y = random.randint(-OBSTACLE_SIZE, 0)
                obstacle = Obstacle(x, y, random.choice(list(OBSTACLE_IMAGES.keys())))
                self.all_sprites.add(obstacle)
                self.obstacles.add(obstacle)

    def update_background(self):
        # Change background based on the player's height (y-position)
        if self.player.rect.y < SCREEN_HEIGHT / 4:
            self.background = self.backgrounds[3]  # Highest level background
        elif self.player.rect.y < SCREEN_HEIGHT / 2:
            self.background = self.backgrounds[2]
        elif self.player.rect.y < 3 * SCREEN_HEIGHT / 4:
            self.background = self.backgrounds[1]
        else:
            self.background = self.backgrounds[0]  # Default background

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.all_sprites.draw(self.screen)
        self.ui_manager.draw(self.screen, self.player, self.time_left)
        if self.state == 'game_over':
            self.ui_manager.draw_game_over(self.screen, self.player.score)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.pause_menu()
                elif event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.reset_game()

    def reset_game(self):
        self.level = 1
        self.time_left = 120
        self.start_time = time.time()
        self.player.lives = 3
        self.player.score = 0
        self.generate_level()
        self.state = 'playing'

    def check_collisions(self):
        # Check obstacle collisions
        hits = pygame.sprite.spritecollide(self.player, self.obstacles, False)
        for hit in hits:
            if not self.player.shielded:
                self.player.lives -= 1
                hit.kill()  # Remove the obstacle that collided with the player

        # Check power-up collisions
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for hit in hits:
            self.player.power_up(hit.type)
            self.player.score += 50 if not self.player.double_score else 100

        # Increase score over time
        self.player.score += 1 if not self.player.double_score else 2

    def pause_menu(self):
        paused = True
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    paused = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        paused = False
                    elif event.key == pygame.K_q:
                        paused = False
                        self.running = False
            self.screen.fill(GRAY)
            pause_text = font.render('Game Paused', True, WHITE)
            resume_text = font.render('Press R to Resume', True, WHITE)
            quit_text = font.render('Press Q to Quit', True, WHITE)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.display.flip()
            self.clock.tick(30)

    def update_time(self):
        elapsed_time = time.time() - self.start_time
        self.time_left -= elapsed_time
        self.start_time = time.time()
        if self.time_left <= 0:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.time_left = 120
        self.generate_level()
        self.ui_manager.draw_level_up(self.screen, self.level)
        pygame.display.flip()
        pygame.time.delay(2000)
    def game_over(self):
        self.running = False
        name = self.get_player_name()
        self.high_score_manager.add_score(name, self.player.score)
        self.display_game_over()

    def get_player_name(self):
        name = ''
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 30)
        active = True
        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active = False
                    self.running = False
                    return 'Player'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode
            self.screen.fill(BLACK)
            prompt_text = font.render('Enter your name:', True, WHITE)
            self.screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            txt_surface = font.render(name, True, WHITE)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(self.screen, WHITE, input_box, 2)
            pygame.display.flip()
            self.clock.tick(30)
        return name if name else 'Player'

    def display_game_over(self):
        self.screen.fill(BLACK)
        self.ui_manager.draw_game_over(self.screen, self.player.score)
        pygame.display.flip()
        pygame.time.delay(3000)
        self.display_high_scores()

    def display_high_scores(self):
        displaying = True
        while displaying:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    displaying = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        displaying = False
            self.screen.fill(BLACK)
            self.high_score_manager.draw(self.screen)
            prompt_text = pygame.font.Font(FONT_NAME, FONT_SIZE).render('Press ENTER to Exit', True, WHITE)
            self.screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT - 100))
            pygame.display.flip()
            self.clock.tick(30)

    def settings_menu(self):
        in_settings = True
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        volume = 0.5  # Example setting
        while in_settings:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    in_settings = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        in_settings = False
                    elif event.key == pygame.K_UP:
                        volume = min(1.0, volume + 0.1)
                    elif event.key == pygame.K_DOWN:
                        volume = max(0.0, volume - 0.1)
            self.screen.fill(GRAY)
            settings_text = font.render('Settings', True, WHITE)
            volume_text = font.render(f'Volume: {int(volume * 100)}%', True, WHITE)
            back_text = font.render('Press BACKSPACE to Return', True, WHITE)
            self.screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(volume_text, (SCREEN_WIDTH // 2 - volume_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.display.flip()
            self.clock.tick(30)

    def level_selection_menu(self):
        selecting = True
        selected_level = self.level
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    selecting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_level = min(selected_level + 1, 5)  # Assuming 5 levels
                    elif event.key == pygame.K_UP:
                        selected_level = max(selected_level - 1, 1)
                    elif event.key == pygame.K_RETURN:
                        self.level = selected_level
                        selecting = False
            self.screen.fill(BLACK)
            title_text = font.render('Select Level:', True, WHITE)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
            for i in range(1, 6):
                level_text = font.render(f'Level {i}', True, WHITE if i != selected_level else RED)
                self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50 + (i - 1) * 30))
            pygame.display.flip()
            self.clock.tick(30)

    def main_menu(self):
        menu = True
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        while menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    menu = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        menu = False
                        self.level_selection_menu()
                        self.run()
                    elif event.key == pygame.K_q:
                        self.running = False
                        menu = False
            self.screen.fill(BLACK)
            title_text = font.render('Rapid Roll Clone', True, WHITE)
            start_text = font.render('Press ENTER to Start', True, WHITE)
            quit_text = font.render('Press Q to Quit', True, WHITE)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.display.flip()
            self.clock.tick(30)

    def start_game(self):
        self.main_menu()
        if self.running:
            self.run()

if __name__ == '__main__':
    game = Game()
    game.start_game()
# Sound Manager
class SoundManager:
    """Class to manage sound effects and background music."""
    def __init__(self):
        self.jump_sound = load_sound(JUMP_SOUND)
        self.powerup_sound = load_sound(POWERUP_SOUND)
        self.game_over_sound = load_sound(GAME_OVER_SOUND)
        self.background_music = os.path.join(ASSET_DIR, 'background_music.mp3')

    def play_jump(self):
        if self.jump_sound:
            self.jump_sound.play()

    def play_powerup(self):
        if self.powerup_sound:
            self.powerup_sound.play()

    def play_game_over(self):
        if self.game_over_sound:
            self.game_over_sound.play()

    def play_background_music(self):
        pygame.mixer.music.load(self.background_music)
        pygame.mixer.music.play(-1)  # Loop the background music

# Updated Player class to integrate SoundManager
class Player(pygame.sprite.Sprite):
    """Class representing the player character."""
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image(PLAYER_IMAGE, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity_y = 0
        self.speed = PLAYER_SPEED
        self.jump_speed = PLAYER_JUMP_SPEED
        self.lives = 3
        self.score = 0
        self.powered_up = False
        self.power_up_time = 0
        self.shielded = False
        self.shield_time = 0
        self.double_score = False
        self.double_score_time = 0
        self.sound_manager = SoundManager()  # New sound manager

    def update(self, platforms):
        self.handle_input()
        self.apply_gravity()
        self.check_collisions(platforms)
        self.update_power_up_status()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_SPACE]:
            self.jump()

    def jump(self):
        self.rect.y += 1  # Move down slightly to check for platform
        hits = pygame.sprite.spritecollide(self, game.platforms, False)
        self.rect.y -= 1  # Move back to original position
        if hits:
            self.velocity_y = -self.jump_speed
            self.sound_manager.play_jump()

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        if self.rect.bottom > SCREEN_HEIGHT:
            self.lives -= 1
            self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.velocity_y = 0
            if self.lives <= 0:
                self.sound_manager.play_game_over()

    def check_collisions(self, platforms):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and self.velocity_y > 0:
            self.rect.bottom = hits[0].rect.top
            self.velocity_y = 0

    def update_power_up_status(self):
        current_time = time.time()
        if self.powered_up and current_time - self.power_up_time > POWERUP_DURATION:
            self.powered_up = False
            self.speed = PLAYER_SPEED
        if self.shielded and current_time - self.shield_time > POWERUP_DURATION:
            self.shielded = False
        if self.double_score and current_time - self.double_score_time > POWERUP_DURATION:
            self.double_score = False

    def power_up(self, power_type):
        self.sound_manager.play_powerup()  # Play sound on power-up
        if power_type == 'extra_life':
            self.lives += 1
        elif power_type == 'bonus_star':
            self.score += 100 if not self.double_score else 200
        elif power_type == 'power_ball':
            self.powered_up = True
            self.power_up_time = time.time()
            self.speed = PLAYER_SPEED + 3
        elif power_type == 'time_extension':
            game.time_left += 30
        elif power_type == 'shield':
            self.shielded = True
            self.shield_time = time.time()
        elif power_type == 'double_score':
            self.double_score = True
            self.double_score_time = time.time()

# High Score Manager with player names and date-time
class HighScoreManager:
    """Class to manage high scores."""
    def __init__(self):
        self.scores = self.load_scores()

    def load_scores(self):
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as f:
                return json.load(f)
        else:
            return []

    def save_scores(self):
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(self.scores, f)

    def add_score(self, name, score):
        date_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.scores.append({'name': name, 'score': score, 'date_time': date_time})
        self.scores = sorted(self.scores, key=lambda x: x['score'], reverse=True)[:10]
        self.save_scores()

    def draw(self, screen):
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        title_text = font.render('High Scores', True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        for idx, score_entry in enumerate(self.scores):
            score_text = font.render(f"{idx + 1}. {score_entry['name']} - {score_entry['score']} ({score_entry['date_time']})", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 150 + idx * 30))

# New Power-Up: Slow Motion
class SlowMotionPowerUp(PowerUp):
    """Class representing a slow motion power-up."""
    def __init__(self, x, y):
        super().__init__(x, y, 'slow_motion')

    def apply_effect(self, player):
        player.game.slow_motion = True
        player.game.slow_motion_time = time.time()

# Applying Slow Motion Effect in the Game
class Game:
    """Main game class."""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Rapid Roll Clone')
        self.clock = pygame.time.Clock()
        self.running = True
        self.level = 1
        self.time_left = 120  # seconds per level
        self.start_time = time.time()
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.ui_manager = UIManager()
        self.high_score_manager = HighScoreManager()
        self.sound_manager = SoundManager()
        self.backgrounds = [load_image(bg, SCREEN_WIDTH, SCREEN_HEIGHT) for bg in BACKGROUND_IMAGES]
        self.background = self.backgrounds[0]
        self.slow_motion = False
        self.slow_motion_time = 0
        self.generate_level()
        self.state = 'playing'

    def run(self):
        self.sound_manager.play_background_music()
        while self.running:
            self.clock.tick(FPS // 2 if self.slow_motion else FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

    def update(self):
        if self.state == 'playing':
            self.player.update(self.platforms)
            self.platforms.update()
            self.obstacles.update()
            self.powerups.update()
            self.check_collisions()
            self.update_time()
            self.update_background()
            self.spawn_platforms_and_obstacles()
            if self.slow_motion and time.time() - self.slow_motion_time > 5:  # Slow motion lasts 5 seconds
                self.slow_motion = False
            if self.player.lives <= 0:
                self.state = 'game_over'

    def spawn_platforms_and_obstacles(self):
        # Check if the player is near the top of the screen and spawn new platforms and obstacles
        if self.player.rect.top <= SCREEN_HEIGHT / 2:
            # Adjust all sprites downwards to simulate upward movement
            for sprite in self.all_sprites:
                sprite.rect.y += PLAYER_SPEED

            # Generate new platforms and obstacles at the top of the screen
            if len(self.platforms) < 10 + self.level * 2:
                x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)
                y = random.randint(-PLATFORM_HEIGHT, 0)
                platform = Platform(x, y, moving=random.choice([True, False]), disappearing=random.choice([True, False]))
                self.all_sprites.add(platform)
                self.platforms.add(platform)

            if len(self.obstacles) < 5 + self.level:
                x = random.randint(0, SCREEN_WIDTH - OBSTACLE_SIZE)
                y = random.randint(-OBSTACLE_SIZE, 0)
                obstacle = Obstacle(x, y, random.choice(list(OBSTACLE_IMAGES.keys())))
                self.all_sprites.add(obstacle)
                self.obstacles.add(obstacle)

    def update_background(self):
        # Change background based on the player's height (y-position)
        if self.player.rect.y < SCREEN_HEIGHT / 4:
            self.background = self.backgrounds[3]  # Highest level background
        elif self.player.rect.y < SCREEN_HEIGHT / 2:
            self.background = self.backgrounds[2]
        elif self.player.rect.y < 3 * SCREEN_HEIGHT / 4:
            self.background = self.backgrounds[1]
        else:
            self.background = self.backgrounds[0]  # Default background

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.all_sprites.draw(self.screen)
        self.ui_manager.draw(self.screen, self.player, self.time_left)
        if self.state == 'game_over':
            self.ui_manager.draw_game_over(self.screen, self.player.score)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.pause_menu()
                elif event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.reset_game()

    def reset_game(self):
        self.level = 1
        self.time_left = 120
        self.start_time = time.time()
        self.player.lives = 3
        self.player.score = 0
        self.generate_level()
        self.state = 'playing'

    def pause_menu(self):
        paused = True
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    paused = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        paused = False
                    elif event.key == pygame.K_q:
                        paused = False
                        self.running = False
            self.screen.fill(GRAY)
            pause_text = font.render('Game Paused', True, WHITE)
            resume_text = font.render('Press R to Resume', True, WHITE)
            quit_text = font.render('Press Q to Quit', True, WHITE)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.display.flip()
            self.clock.tick(30)

    def update_time(self):
        elapsed_time = time.time() - self.start_time
        self.time_left -= elapsed_time
        self.start_time = time.time()
        if self.time_left <= 0:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.time_left = 120
        self.generate_level()
        self.ui_manager.draw_level_up(self.screen, self.level)
        pygame.display.flip()
        pygame.time.delay(2000)
    def display_high_scores(self):
        displaying = True
        while displaying:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    displaying = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        displaying = False
            self.screen.fill(BLACK)
            self.high_score_manager.draw(self.screen)
            prompt_text = pygame.font.Font(FONT_NAME, FONT_SIZE).render('Press ENTER to Exit', True, WHITE)
            self.screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT - 100))
            pygame.display.flip()
            self.clock.tick(30)

    def main_menu(self):
        menu = True
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        while menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    menu = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        menu = False
                        self.level_selection_menu()
                        self.run()
                    elif event.key == pygame.K_q:
                        self.running = False
                        menu = False
            self.screen.fill(BLACK)
            title_text = font.render('Rapid Roll Clone', True, WHITE)
            start_text = font.render('Press ENTER to Start', True, WHITE)
            quit_text = font.render('Press Q to Quit', True, WHITE)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.display.flip()
            self.clock.tick(30)

    def start_game(self):
        self.main_menu()
        if self.running:
            self.run()

    def settings_menu(self):
        in_settings = True
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        volume = 0.5  # Example setting
        while in_settings:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    in_settings = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        in_settings = False
                    elif event.key == pygame.K_UP:
                        volume = min(1.0, volume + 0.1)
                    elif event.key == pygame.K_DOWN:
                        volume = max(0.0, volume - 0.1)
            self.screen.fill(GRAY)
            settings_text = font.render('Settings', True, WHITE)
            volume_text = font.render(f'Volume: {int(volume * 100)}%', True, WHITE)
            back_text = font.render('Press BACKSPACE to Return', True, WHITE)
            self.screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(volume_text, (SCREEN_WIDTH // 2 - volume_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.display.flip()
            self.clock.tick(30)

    def update_time(self):
        elapsed_time = time.time() - self.start_time
        self.time_left -= elapsed_time
        self.start_time = time.time()
        if self.time_left <= 0:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.time_left = 120
        self.generate_level()
        self.ui_manager.draw_level_up(self.screen, self.level)
        pygame.display.flip()
        pygame.time.delay(2000)

    def game_over(self):
        self.running = False
        name = self.get_player_name()
        self.high_score_manager.add_score(name, self.player.score)
        self.display_game_over()

    def get_player_name(self):
        name = ''
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 30)
        active = True
        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active = False
                    self.running = False
                    return 'Player'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode
            self.screen.fill(BLACK)
            prompt_text = font.render('Enter your name:', True, WHITE)
            self.screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            txt_surface = font.render(name, True, WHITE)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(self.screen, WHITE, input_box, 2)
            pygame.display.flip()
            self.clock.tick(30)
        return name if name else 'Player'

    def display_game_over(self):
        self.screen.fill(BLACK)
        self.ui_manager.draw_game_over(self.screen, self.player.score)
        pygame.display.flip()
        pygame.time.delay(3000)
        self.display_high_scores()

    def display_high_scores(self):
        displaying = True
        while displaying:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    displaying = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        displaying = False
            self.screen.fill(BLACK)
            self.high_score_manager.draw(self.screen)
            prompt_text = pygame.font.Font(FONT_NAME, FONT_SIZE).render('Press ENTER to Exit', True, WHITE)
            self.screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT - 100))
            pygame.display.flip()
            self.clock.tick(30)

    def pause_menu(self):
        paused = True
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    paused = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        paused = False
                    elif event.key == pygame.K_q:
                        paused = False
                        self.running = False
            self.screen.fill(GRAY)
            pause_text = font.render('Game Paused', True, WHITE)
            resume_text = font.render('Press R to Resume', True, WHITE)
            quit_text = font.render('Press Q to Quit', True, WHITE)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.display.flip()
            self.clock.tick(30)

    def reset_game(self):
        self.level = 1
        self.time_left = 120
        self.start_time = time.time()
        self.player.lives = 3
        self.player.score = 0
        self.generate_level()
        self.state = 'playing'

    def run(self):
        self.sound_manager.play_background_music()
        while self.running:
            self.clock.tick(FPS // 2 if self.slow_motion else FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.start_game()
