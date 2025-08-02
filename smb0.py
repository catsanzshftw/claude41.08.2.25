import pygame
import sys
import math
import random

# --- Initialization ---
pygame.init()

# --- Settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_TITLE = "Super Mario Bros. 64DS Engine Edition"

# --- Enhanced Color Palette ---
BACKGROUND_COLOR = (92, 148, 252)
BACKGROUND_GRADIENT_TOP = (120, 180, 255)
PLAYER_RED = (216, 40, 0)
PLAYER_BLUE = (0, 88, 248)
PLAYER_SKIN = (252, 216, 168)
GROUND_COLOR = (222, 138, 54)
BRICK_COLOR = (200, 76, 12)
BRICK_MORTAR_COLOR = (148, 148, 148)
QUESTION_BLOCK_COLOR = (252, 188, 0)
ENEMY_BODY_COLOR = (152, 92, 40)
ENEMY_FEET_COLOR = (252, 216, 168)
PIPE_GREEN = (0, 168, 0)
PIPE_DARK_GREEN = (0, 120, 0)
TEXT_COLOR = (255, 255, 255)
BLACK = (0, 0, 0)
PARTICLE_COLORS = [(255, 255, 100), (255, 200, 50), (255, 150, 0)]

# --- SM64DS-Inspired Physics ---
GRAVITY = 0.6
PLAYER_WALK_ACC = 0.5
PLAYER_RUN_ACC = 0.9
PLAYER_FRICTION = 0.88  # Momentum-based
PLAYER_AIR_FRICTION = 0.95
PLAYER_JUMP_STRENGTH = -15
PLAYER_JUMP_BOOST = -2.5  # Hold jump for higher jump
MAX_WALK_SPEED = 4
MAX_RUN_SPEED = 7
ENEMY_SPEED = 1

# --- Screen & Font Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption(GAME_TITLE)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)
big_font = pygame.font.Font(None, 48)

# --- Pre-render gradient background ---
def create_gradient_background():
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        color = [
            int(BACKGROUND_GRADIENT_TOP[i] + (BACKGROUND_COLOR[i] - BACKGROUND_GRADIENT_TOP[i]) * ratio)
            for i in range(3)
        ]
        pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))
    return background

GRADIENT_BACKGROUND = create_gradient_background()

# --- Particle System ---
class Particle:
    def __init__(self, x, y, vx, vy, color, life=30):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.life = life
        self.max_life = float(life)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = self.life / self.max_life
            size = int(4 * alpha)
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

# --- Global particle list with limit ---
particles = []
MAX_PARTICLES = 100

def add_particle(x, y, vx, vy, color, life=30):
    if len(particles) < MAX_PARTICLES:
        particles.append(Particle(x, y, vx, vy, color, life))

# --- Enhanced Level Data with Connectors ---
LEVEL_DATA = {
    1: {
        'platforms': [
            (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40, 'ground'),
            (200, SCREEN_HEIGHT - 120, 120, 40, 'brick'),
            (400, SCREEN_HEIGHT - 200, 40, 40, 'question'),
            (440, SCREEN_HEIGHT - 200, 80, 40, 'brick'),
            (550, SCREEN_HEIGHT - 320, 80, 40, 'brick'),
            (700, SCREEN_HEIGHT - 140, 60, 100, 'pipe'),  # Exit pipe
        ],
        'enemies': [(350, SCREEN_HEIGHT - 72)],
        'start_pos': (100, SCREEN_HEIGHT - 100),
        'exit_pos': (730, SCREEN_HEIGHT - 140)
    },
    2: {
        'platforms': [
            (0, SCREEN_HEIGHT - 40, 250, 40, 'ground'),
            (150, SCREEN_HEIGHT - 140, 80, 40, 'brick'),
            (300, SCREEN_HEIGHT - 240, 80, 40, 'brick'),
            (450, SCREEN_HEIGHT - 340, 80, 40, 'question'),
            (600, SCREEN_HEIGHT - 180, 120, 40, 'brick'),
            (550, SCREEN_HEIGHT - 40, 250, 40, 'ground'),
            (0, SCREEN_HEIGHT - 140, 60, 100, 'pipe'),  # Entry pipe
            (740, SCREEN_HEIGHT - 140, 60, 100, 'pipe'),  # Exit pipe
        ],
        'enemies': [(200, SCREEN_HEIGHT - 72), (650, SCREEN_HEIGHT - 72)],
        'start_pos': (60, SCREEN_HEIGHT - 140),
        'exit_pos': (770, SCREEN_HEIGHT - 140)
    },
    3: {
        'platforms': [
            (0, SCREEN_HEIGHT - 40, 300, 40, 'ground'),
            (450, SCREEN_HEIGHT - 40, 350, 40, 'ground'),
            (100, SCREEN_HEIGHT - 160, 40, 40, 'question'),
            (140, SCREEN_HEIGHT - 160, 40, 40, 'brick'),
            (180, SCREEN_HEIGHT - 160, 40, 40, 'question'),
            (500, SCREEN_HEIGHT - 180, 160, 40, 'brick'),
            (700, SCREEN_HEIGHT - 280, 40, 40, 'brick'),
            (0, SCREEN_HEIGHT - 140, 60, 100, 'pipe'),  # Entry pipe
            (740, SCREEN_HEIGHT - 140, 60, 100, 'pipe'),  # Exit pipe
        ],
        'enemies': [(250, SCREEN_HEIGHT - 72), (500, SCREEN_HEIGHT - 72), (600, SCREEN_HEIGHT - 72)],
        'start_pos': (60, SCREEN_HEIGHT - 140),
        'exit_pos': (770, SCREEN_HEIGHT - 140)
    },
    4: {
        'platforms': [
            (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40, 'ground'),
            (100, SCREEN_HEIGHT - 120, 80, 80, 'brick'),
            (250, SCREEN_HEIGHT - 200, 80, 160, 'brick'),
            (400, SCREEN_HEIGHT - 280, 80, 240, 'brick'),
            (600, SCREEN_HEIGHT - 200, 40, 40, 'question'),
            (680, SCREEN_HEIGHT - 280, 40, 40, 'question'),
            (0, SCREEN_HEIGHT - 140, 60, 100, 'pipe'),  # Entry pipe
            (740, SCREEN_HEIGHT - 140, 60, 100, 'pipe'),  # Exit pipe
        ],
        'enemies': [(500, SCREEN_HEIGHT - 72)],
        'start_pos': (60, SCREEN_HEIGHT - 140),
        'exit_pos': (770, SCREEN_HEIGHT - 140)
    },
    5: {
        'platforms': [
            (0, SCREEN_HEIGHT - 40, 150, 40, 'ground'),
            (250, SCREEN_HEIGHT - 100, 40, 40, 'brick'),
            (350, SCREEN_HEIGHT - 160, 40, 40, 'brick'),
            (450, SCREEN_HEIGHT - 220, 40, 40, 'question'),
            (300, SCREEN_HEIGHT - 40, 100, 40, 'ground'),
            (550, SCREEN_HEIGHT - 40, 250, 40, 'ground'),
            (600, SCREEN_HEIGHT - 140, 120, 40, 'brick'),
            (640, SCREEN_HEIGHT - 260, 40, 40, 'brick'),
            (0, SCREEN_HEIGHT - 140, 60, 100, 'pipe'),  # Entry pipe
        ],
        'enemies': [(100, SCREEN_HEIGHT - 72), (320, SCREEN_HEIGHT - 72), (650, SCREEN_HEIGHT - 172)],
        'start_pos': (60, SCREEN_HEIGHT - 140),
        'exit_pos': None  # Last level
    }
}

# --- Enhanced Player Class with SM64DS Mechanics ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((32, 40), pygame.SRCALPHA)
        self.rect = self.surf.get_rect(center=(100, SCREEN_HEIGHT - 100))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.is_grounded = False
        self.is_running = False
        self.jump_held = False
        self.jump_timer = 0
        self.facing_right = True
        self.animation_timer = 0
        self.needs_redraw = True
        self.draw_player()
        
    def draw_player(self):
        if not self.needs_redraw:
            return
            
        self.surf.fill((0, 0, 0, 0))
        # Enhanced Mario sprite with better proportions
        # Overalls
        pygame.draw.rect(self.surf, PLAYER_BLUE, (0, 20, 32, 20))
        # Arms
        pygame.draw.rect(self.surf, PLAYER_BLUE, (4, 16, 8, 4))
        pygame.draw.rect(self.surf, PLAYER_BLUE, (20, 16, 8, 4))
        # Shirt
        pygame.draw.rect(self.surf, PLAYER_RED, (4, 12, 24, 12))
        # Hat
        pygame.draw.rect(self.surf, PLAYER_RED, (4, 0, 24, 8))
        # Face
        pygame.draw.rect(self.surf, PLAYER_SKIN, (8, 8, 16, 12))
        # Hands
        pygame.draw.rect(self.surf, PLAYER_SKIN, (0, 20, 6, 6))
        pygame.draw.rect(self.surf, PLAYER_SKIN, (26, 20, 6, 6))
        # Eyes (animated)
        if self.animation_timer % 120 < 110:  # Blink animation
            pygame.draw.rect(self.surf, BLACK, (10, 10, 3, 4))
            pygame.draw.rect(self.surf, BLACK, (19, 10, 3, 4))
        
        self.needs_redraw = False

    def move(self):
        self.acc = pygame.math.Vector2(0, GRAVITY)
        keys = pygame.key.get_pressed()
        
        # SM64DS-style running
        self.is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_z]
        
        # Movement with momentum
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.is_running:
                self.acc.x = -PLAYER_RUN_ACC
            else:
                self.acc.x = -PLAYER_WALK_ACC
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.is_running:
                self.acc.x = PLAYER_RUN_ACC
            else:
                self.acc.x = PLAYER_WALK_ACC
            self.facing_right = True
        
        # Apply friction
        if self.is_grounded:
            self.vel.x *= PLAYER_FRICTION
        else:
            self.vel.x *= PLAYER_AIR_FRICTION
            
        # Speed limits
        max_speed = MAX_RUN_SPEED if self.is_running else MAX_WALK_SPEED
        self.vel.x = max(-max_speed, min(max_speed, self.vel.x))
        
        # Update position
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        
        # Screen wrapping - fixed to not interfere with pipes
        if self.pos.x > SCREEN_WIDTH and self.vel.x > 0:
            self.pos.x = 0
        if self.pos.x < -32 and self.vel.x < 0:  # -32 to account for player width
            self.pos.x = SCREEN_WIDTH
        
        self.rect.topleft = self.pos
        self.animation_timer += 1
        
        # Check if we need to redraw (blink animation)
        if self.animation_timer % 10 == 0:
            self.needs_redraw = True

    def jump(self):
        if self.is_grounded and not self.jump_held:
            self.vel.y = PLAYER_JUMP_STRENGTH
            self.is_grounded = False
            self.jump_held = True
            self.jump_timer = 0
            # Jump particles
            for i in range(5):
                add_particle(
                    self.rect.centerx + random.randint(-10, 10),
                    self.rect.bottom,
                    random.uniform(-2, 2),
                    random.uniform(-3, -1),
                    random.choice(PARTICLE_COLORS)
                )
                
    def update_jump(self):
        # Variable jump height (hold to jump higher)
        if self.jump_held and self.jump_timer < 10 and self.vel.y < 0:
            self.vel.y += PLAYER_JUMP_BOOST
            self.jump_timer += 1

    def update(self, platforms):
        self.move()
        self.update_jump()
        # Check Y collision first
        self.rect.y = int(self.pos.y)
        self.check_collision_y(platforms)
        # Then X collision
        self.rect.x = int(self.pos.x)
        self.check_collision_x(platforms)
        self.draw_player()  # Redraw only if needed

    def check_collision_y(self, platforms):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            platform = hits[0]
            if self.vel.y > 0:  # Moving down
                self.rect.bottom = platform.rect.top
                self.pos.y = float(self.rect.y)
                self.vel.y = 0
                self.is_grounded = True
            elif self.vel.y < 0:  # Moving up
                if hasattr(platform, 'block_type') and platform.block_type != 'pipe':
                    self.rect.top = platform.rect.bottom
                    self.pos.y = float(self.rect.y)
                    self.vel.y = 0
                    # Block hit effect
                    if platform.block_type == 'question':
                        platform.hit()
                        # Coin particles
                        for i in range(8):
                            add_particle(
                                platform.rect.centerx,
                                platform.rect.centery,
                                random.uniform(-3, 3),
                                random.uniform(-5, -2),
                                random.choice(PARTICLE_COLORS)
                            )
                    
    def check_collision_x(self, platforms):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            platform = hits[0]
            if self.vel.x > 0:  # Moving right
                self.rect.right = platform.rect.left
                self.pos.x = float(self.rect.x)
                self.vel.x = 0
            elif self.vel.x < 0:  # Moving left
                self.rect.left = platform.rect.right
                self.pos.x = float(self.rect.x)
                self.vel.x = 0

# --- Enhanced Platform Class ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, block_type='ground'):
        super().__init__()
        self.block_type = block_type
        self.surf = pygame.Surface((w, h))
        self.rect = self.surf.get_rect(topleft=(x, y))
        self.hit_animation = 0
        self.original_y = y
        self.was_hit = False
        self.draw_block()

    def draw_block(self):
        if self.block_type == 'ground':
            self.surf.fill(GROUND_COLOR)
            # Add texture
            for i in range(0, self.rect.width, 8):
                if i + 4 < self.rect.width:
                    pygame.draw.line(self.surf, (200, 120, 40), (i, 0), (i+4, 8), 2)
        elif self.block_type == 'brick':
            self.surf.fill(BRICK_COLOR)
            w, h = self.rect.size
            for i in range(0, int(w), 16):
                pygame.draw.line(self.surf, BRICK_MORTAR_COLOR, (i, 0), (i, h), 2)
            for i in range(0, int(h), 16):
                pygame.draw.line(self.surf, BRICK_MORTAR_COLOR, (0, i), (w, i), 2)
        elif self.block_type == 'question':
            if self.was_hit:
                self.surf.fill((180, 140, 100))  # Used block color
            else:
                self.surf.fill(QUESTION_BLOCK_COLOR)
                # Animated question mark
                q_font = pygame.font.Font(None, int(self.rect.h * 0.8))
                q_text = q_font.render("?", True, BLACK)
                q_rect = q_text.get_rect(center=self.surf.get_rect().center)
                self.surf.blit(q_text, q_rect)
        elif self.block_type == 'pipe':
            # Draw a classic Mario pipe
            pygame.draw.rect(self.surf, PIPE_GREEN, (0, 0, self.rect.width, self.rect.height))
            pygame.draw.rect(self.surf, PIPE_DARK_GREEN, (0, 0, 5, self.rect.height))
            pygame.draw.rect(self.surf, PIPE_DARK_GREEN, (self.rect.width-5, 0, 5, self.rect.height))
            pygame.draw.rect(self.surf, PIPE_DARK_GREEN, (0, 0, self.rect.width, 5))
            
    def hit(self):
        if self.block_type == 'question' and not self.was_hit:
            self.hit_animation = 20
            self.was_hit = True
            
    def update(self):
        if self.hit_animation > 0:
            # Bounce animation
            offset = math.sin(self.hit_animation * 0.3) * 5
            self.rect.y = int(self.original_y - offset)
            self.hit_animation -= 1
            if self.hit_animation == 0:
                self.rect.y = self.original_y
                self.draw_block()

# --- Enhanced Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.normal_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.squished_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.surf.get_rect(topleft=(x, y))
        self.pos = pygame.math.Vector2(float(x), float(y))
        self.vel = pygame.math.Vector2(ENEMY_SPEED, 0)
        self.patrol_range = (x - 100, x + 100)
        self.squish_timer = 0
        self.alive = True
        self.walk_frame = 0
        self.pre_draw_enemy()
        self.update_sprite()

    def pre_draw_enemy(self):
        # Pre-draw normal enemy
        self.normal_surf.fill((0, 0, 0, 0))
        # Body
        pygame.draw.ellipse(self.normal_surf, ENEMY_BODY_COLOR, (0, 4, 32, 28))
        # Eyes
        pygame.draw.rect(self.normal_surf, BLACK, (8, 12, 5, 8))
        pygame.draw.rect(self.normal_surf, BLACK, (19, 12, 5, 8))
        # Angry eyebrows
        pygame.draw.line(self.normal_surf, BLACK, (8, 10), (13, 8), 2)
        pygame.draw.line(self.normal_surf, BLACK, (19, 8), (24, 10), 2)
        
        # Pre-draw squished enemy
        self.squished_surf.fill((0, 0, 0, 0))
        pygame.draw.ellipse(self.squished_surf, ENEMY_BODY_COLOR, (0, 20, 32, 12))

    def update_sprite(self):
        self.surf.fill((0, 0, 0, 0))
        if self.alive:
            self.surf.blit(self.normal_surf, (0, 0))
            # Draw animated feet
            offset = self.walk_frame * 4
            pygame.draw.rect(self.surf, ENEMY_FEET_COLOR, (2 + offset, 28, 12, 4))
            pygame.draw.rect(self.surf, ENEMY_FEET_COLOR, (18 - offset, 28, 12, 4))
        else:
            self.surf.blit(self.squished_surf, (0, 0))

    def update(self, platforms):
        if self.alive:
            self.pos.x += self.vel.x
            if self.pos.x < self.patrol_range[0] or self.pos.x > self.patrol_range[1]:
                self.vel.x *= -1
            self.rect.x = int(self.pos.x)
            self.rect.y = int(self.pos.y)
            # Update walk animation every 10 frames
            if pygame.time.get_ticks() % 200 < 100:
                self.walk_frame = 0
            else:
                self.walk_frame = 1
            self.update_sprite()
        else:
            self.squish_timer += 1
            if self.squish_timer > 30:
                self.kill()

# --- Optimized Screen Transition Effect ---
def transition_effect(screen, direction='out'):
    steps = 15  # Reduced from 20 for smoother animation
    for i in range(steps):
        if direction == 'out':
            radius = i * (SCREEN_WIDTH // steps)
        else:
            radius = SCREEN_WIDTH - (i * (SCREEN_WIDTH // steps))
        
        screen.fill(BLACK)
        if radius > 0:
            pygame.draw.circle(screen, BACKGROUND_COLOR, 
                             (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), radius)
        
        pygame.display.flip()
        clock.tick(60)

# --- Game Loop Function ---
def game_loop():
    current_level = 1
    game_complete = False
    
    while not game_complete:
        # Initialize level
        all_sprites = pygame.sprite.Group()
        platforms = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        
        level_data = LEVEL_DATA[current_level]
        
        # Create player
        player = Player()
        start_x, start_y = level_data['start_pos']
        player.rect.topleft = (start_x, start_y)
        player.pos = pygame.math.Vector2(float(start_x), float(start_y))
        all_sprites.add(player)
        
        # Create platforms
        for p_data in level_data['platforms']:
            p = Platform(*p_data)
            platforms.add(p)
            all_sprites.add(p)
            
        # Create enemies
        for e_data in level_data['enemies']:
            e = Enemy(*e_data)
            enemies.add(e)
            all_sprites.add(e)
        
        # Transition in
        transition_effect(screen, 'in')
        
        level_complete = False
        particles.clear()
        
        while not level_complete:
            dt = clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_SPACE, pygame.K_w]:
                        player.jump()
                if event.type == pygame.KEYUP:
                    if event.key in [pygame.K_UP, pygame.K_SPACE, pygame.K_w]:
                        player.jump_held = False

            # Update
            player.update(platforms)
            enemies.update(platforms)
            
            # Update platforms with animations
            for platform in platforms:
                if hasattr(platform, 'update'):
                    platform.update()
            
            # Update particles
            for particle in particles[:]:
                particle.update()
                if particle.life <= 0:
                    particles.remove(particle)

            # Player-Enemy Collision
            enemy_hit = pygame.sprite.spritecollideany(player, enemies)
            if enemy_hit and enemy_hit.alive:
                # More precise collision detection
                if (player.vel.y > 1 and 
                    player.rect.bottom > enemy_hit.rect.top and
                    player.rect.bottom < enemy_hit.rect.centery + 10 and
                    player.rect.centerx > enemy_hit.rect.left and
                    player.rect.centerx < enemy_hit.rect.right):
                    # Successful stomp
                    enemy_hit.alive = False
                    enemy_hit.update_sprite()
                    player.vel.y = PLAYER_JUMP_STRENGTH / 2
                    # Stomp particles
                    for i in range(6):
                        add_particle(
                            enemy_hit.rect.centerx,
                            enemy_hit.rect.centery,
                            random.uniform(-3, 3),
                            random.uniform(-4, -1),
                            ENEMY_BODY_COLOR
                        )
                else:
                    # Player dies - restart level
                    transition_effect(screen, 'out')
                    break

            # Check for level completion (reach exit pipe)
            if level_data['exit_pos']:
                exit_x, exit_y = level_data['exit_pos']
                if (abs(player.rect.centerx - exit_x) < 30 and 
                    abs(player.rect.centery - exit_y) < 50):
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                        # Enter pipe animation
                        for i in range(30):
                            player.rect.y += 2
                            draw_game(screen, all_sprites, particles, current_level)
                            pygame.display.flip()
                            clock.tick(FPS)
                        
                        level_complete = True
                        current_level += 1
                        if current_level > 5:
                            game_complete = True
                        else:
                            transition_effect(screen, 'out')
            elif current_level == 5:
                # Last level - check if reached the right edge
                if player.rect.right >= SCREEN_WIDTH - 10:
                    game_complete = True
                    level_complete = True

            # Draw everything
            draw_game(screen, all_sprites, particles, current_level)
            
            # Draw pipe entry hint
            if level_data['exit_pos']:
                exit_x, exit_y = level_data['exit_pos']
                if (abs(player.rect.centerx - exit_x) < 40 and 
                    abs(player.rect.centery - exit_y) < 60):
                    hint_text = font.render("Press DOWN to enter", True, TEXT_COLOR)
                    hint_rect = hint_text.get_rect(center=(exit_x, exit_y - 80))
                    screen.blit(hint_text, hint_rect)
            
            pygame.display.flip()
    
    # Game complete screen
    screen.fill(BACKGROUND_COLOR)
    complete_text = big_font.render("GAME COMPLETE!", True, TEXT_COLOR)
    complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(complete_text, complete_rect)
    
    thanks_text = font.render("Thanks for playing!", True, TEXT_COLOR)
    thanks_rect = thanks_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
    screen.blit(thanks_text, thanks_rect)
    
    pygame.display.flip()
    pygame.time.wait(3000)

def draw_game(screen, all_sprites, particles, level):
    # Use pre-rendered gradient background
    screen.blit(GRADIENT_BACKGROUND, (0, 0))
    
    # Draw sprites
    for sprite in all_sprites:
        screen.blit(sprite.surf, sprite.rect)
    
    # Draw particles
    for particle in particles:
        particle.draw(screen)
    
    # UI
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, TEXT_COLOR)
    screen.blit(fps_text, (10, 10))
    
    level_text = font.render(f"World 1-{level}", True, TEXT_COLOR)
    screen.blit(level_text, (SCREEN_WIDTH - 100, 10))
    
    # Controls hint
    controls_text = font.render("WASD/Arrows to move, SPACE/UP to jump, SHIFT/Z to run", True, TEXT_COLOR)
    controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 20))
    screen.blit(controls_text, controls_rect)

# --- Main Program ---
def main():
    # Start screen
    screen.fill(BACKGROUND_COLOR)
    title_text = big_font.render(GAME_TITLE, True, PLAYER_RED)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
    screen.blit(title_text, title_rect)
    
    start_text = font.render("Press any key to start", True, TEXT_COLOR)
    start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
    screen.blit(start_text, start_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
    
    game_loop()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
