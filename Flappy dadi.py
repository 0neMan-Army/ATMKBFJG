import pygame
import random
import sys
import os

# ============================================
# ============================================

GAME_CONFIG = {
    'bird_image': "",
    'pipe_image': "",
    'jump_sound': "",
    'gameover_sound': "",
    'background_music': None,

    
    'gravity': 0.3,          
    'jump_strength': -7.5,     # balanced upward motion
    'pipe_speed': 2.5,         # scrolling speed
    'pipe_gap': 190,           # narrower vertical gap 
    'pipe_distance': 280,      # horizontal spacing
    'bird_size': 50,
    'pipe_width': 80
}

# Pygame setup
pygame.init()
pygame.mixer.init()


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 450
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird - Landscape Balanced Edition')
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
SKY_BLUE, GREEN, YELLOW, RED = (135, 206, 235), (34, 139, 34), (255, 215, 0), (255, 0, 0)

# ============================================
#  HIGH SCORE SYSTEM
# ============================================
def load_highscore():
    if not os.path.exists("highscore.txt"):
        with open("highscore.txt", "w") as f:
            f.write("0")
    with open("highscore.txt", "r") as f:
        return int(f.read().strip())

def save_highscore(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

# ============================================
# BIRD CLASS
# ============================================
class Bird:
    def __init__(self):
        self.x, self.y = 150, SCREEN_HEIGHT // 2
        self.velocity = 0
        self.size = GAME_CONFIG['bird_size']
        try:
            img = pygame.image.load(GAME_CONFIG['bird_image'])
            self.image = pygame.transform.scale(img, (self.size, self.size))
            self.use_image = True
        except:
            print("⚠️ Bird image missing, using default circle.")
            self.use_image = False

    def jump(self):
        self.velocity = GAME_CONFIG['jump_strength']

    def update(self):
        self.velocity += GAME_CONFIG['gravity']
        self.y += self.velocity

    def draw(self, screen):
        if self.use_image:
            rotated = pygame.transform.rotate(self.image, -self.velocity * 3)
            rect = rotated.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(screen, YELLOW, (self.x + 25, int(self.y + 25)), 25)
            pygame.draw.circle(screen, BLACK, (self.x + 25, int(self.y + 25)), 25, 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

# ============================================
#  PIPE CLASS
# ============================================
class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = GAME_CONFIG['pipe_width']
        self.top_height = random.randint(50, SCREEN_HEIGHT - GAME_CONFIG['pipe_gap'] - 100)
        self.passed = False
        try:
            pipe_img = pygame.image.load(GAME_CONFIG['pipe_image'])
            self.top_pipe = pygame.transform.flip(
                pygame.transform.scale(pipe_img, (self.width, self.top_height)), False, True)
            self.bottom_pipe = pygame.transform.scale(
                pipe_img, (self.width, SCREEN_HEIGHT - self.top_height - GAME_CONFIG['pipe_gap']))
            self.use_image = True
        except:
            print("⚠️ Pipe image missing, using rectangles.")
            self.use_image = False

    def update(self, speed):
        self.x -= speed

    def draw(self, screen):
        if self.use_image:
            screen.blit(self.top_pipe, (self.x, 0))
            screen.blit(self.bottom_pipe, (self.x, self.top_height + GAME_CONFIG['pipe_gap']))
        else:
            pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.top_height))
            pygame.draw.rect(screen, GREEN, (self.x, self.top_height + GAME_CONFIG['pipe_gap'],
                                             self.width, SCREEN_HEIGHT - self.top_height - GAME_CONFIG['pipe_gap']))
            pygame.draw.rect(screen, BLACK, (self.x, 0, self.width, SCREEN_HEIGHT), 2)

    def get_top_rect(self):
        return pygame.Rect(self.x, 0, self.width, self.top_height)

    def get_bottom_rect(self):
        bottom_y = self.top_height + GAME_CONFIG['pipe_gap']
        return pygame.Rect(self.x, bottom_y, self.width, SCREEN_HEIGHT - bottom_y)

# ============================================
#  GAME CLASS
# ============================================
class Game:
    def __init__(self):
        self.bird = Bird()
        self.pipes = [Pipe(SCREEN_WIDTH + 200)]
        self.score = 0
        self.highscore = load_highscore()
        self.game_started = False
        self.game_over = False
        self.paused = False
        self.pipe_speed = GAME_CONFIG['pipe_speed']
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)

        
        try:
            self.jump_sound = pygame.mixer.Sound(GAME_CONFIG['jump_sound'])
        except:
            self.jump_sound = None
        try:
            self.gameover_sound = pygame.mixer.Sound(GAME_CONFIG['gameover_sound'])
        except:
            self.gameover_sound = None
        if GAME_CONFIG['background_music']:
            pygame.mixer.music.load(GAME_CONFIG['background_music'])
            pygame.mixer.music.play(-1)

    def reset(self):
        if self.gameover_sound:
            self.gameover_sound.stop()
        self.__init__()
        self.game_started = True

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    if not self.game_started:
                        self.reset()
                    elif not self.game_over:
                        if self.gameover_sound:
                            self.gameover_sound.stop()
                        self.bird.jump()
                        if self.jump_sound:
                            self.jump_sound.play()
                    else:
                        self.reset()
                if e.key == pygame.K_p and self.game_started:
                    self.paused = not self.paused
        return True

    def update(self):
        if not self.game_started or self.game_over or self.paused:
            return
        self.bird.update()
        for pipe in self.pipes:
            pipe.update(self.pipe_speed)

       
        if self.pipes[-1].x < SCREEN_WIDTH - GAME_CONFIG['pipe_distance']:
            self.pipes.append(Pipe(SCREEN_WIDTH))
        self.pipes = [p for p in self.pipes if p.x > -p.width]

        bird_rect = self.bird.get_rect()
        for p in self.pipes:
            if bird_rect.colliderect(p.get_top_rect()) or bird_rect.colliderect(p.get_bottom_rect()):
                self.game_over = True
                if self.gameover_sound:
                    self.gameover_sound.play()
            if not p.passed and p.x + p.width < self.bird.x:
                p.passed = True
                self.score += 1
                self.pipe_speed += 0.02
                if self.score > self.highscore:
                    self.highscore = self.score
                    save_highscore(self.highscore)

        if self.bird.y < 0 or self.bird.y + self.bird.size > SCREEN_HEIGHT:
            self.game_over = True
            if self.gameover_sound:
                self.gameover_sound.play()

    def draw(self, screen):
        screen.fill(SKY_BLUE)
        for pipe in self.pipes:
            pipe.draw(screen)
        self.bird.draw(screen)
        score_text = self.font.render(str(self.score), True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 50))
        if not self.game_started:
            self._draw_overlay("Flappy Bird", "Press SPACEBAR to Start", "Keep pressing SPACEBAR to fly!")
        if self.paused:
            self._draw_overlay("Paused", "Press P to Resume", "")
        if self.game_over:
            self._draw_overlay("ATMKBFJG!", f"Score: {self.score}", "Press SPACEBAR to Restart")

    def _draw_overlay(self, title, line1, line2):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        t = self.font.render(title, True, RED)
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 150))
        if line1:
            l1 = self.small_font.render(line1, True, WHITE)
            screen.blit(l1, (SCREEN_WIDTH // 2 - l1.get_width() // 2, 240))
        if line2:
            l2 = self.small_font.render(line2, True, WHITE)
            screen.blit(l2, (SCREEN_WIDTH // 2 - l2.get_width() // 2, 280))
        h = self.small_font.render(f"High Score: {self.highscore}", True, YELLOW)
        screen.blit(h, (SCREEN_WIDTH // 2 - h.get_width() // 2, 330))

# ============================================
#  MAIN LOOP
# ============================================
def main():
    print("Starting Flappy Bird - Landscape Balanced Edition...")
    game = Game()
    running = True
    while running:
        running = game.handle_events()
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

