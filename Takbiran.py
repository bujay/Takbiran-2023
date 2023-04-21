import pygame
from pygame import mixer
import random
import time
import sys
import math
from datetime import datetime, timedelta, timezone

JAKARTA = timezone(timedelta(hours=7))

pygame.init()
mixer.init(channels=16)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Malam Takbiran Idul Fitri 2023")
# pygame Icon
pygame.display.set_icon(pygame.image.load("Takbiran.png"))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

font = pygame.font.Font(pygame.font.match_font('arial'), 64)
subheader_font = pygame.font.Font(pygame.font.match_font('arial'), 24)

explosion_sound = mixer.Sound("Audio/meledak.mp3")
explosion_sound.set_volume(0.5)
launch_sound = mixer.Sound("Audio/muncul.mp3")
launch_sound.set_volume(0.3)
countdown_sound = mixer.Sound("Audio/mundur.mp3")
countdown_sound.set_volume(0.5)
countdown_played = False
countdown_channel = None

takbiran_sound = mixer.Sound("Audio/takbiran.mp3")
takbiran_sound.set_volume(0.5)
takbiran_channel = None

fireworks_active = False

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.speed = random.uniform(1, 4)
        self.angle = random.uniform(0, 2 * math.pi)
        self.life = random.uniform(0.5, 3)

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.life -= 0.01

        return self.life <= 0 or self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)


class Rocket:
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = HEIGHT
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.speed = random.uniform(2, 6)
        self.exploded = False
        self.launch_sound_played = False

    def move(self):
        if not self.launch_sound_played:
            launch_channel = mixer.find_channel()
            if launch_channel:
                launch_channel.play(launch_sound)
                self.launch_sound_played = True

        self.y -= self.speed
        if self.y < random.randint(100, HEIGHT // 4):
            if not self.exploded:
                explosion_channel = mixer.find_channel()
                if explosion_channel:
                    explosion_channel.play(explosion_sound)
                self.exploded = True

    def draw(self, screen):
        if not self.exploded:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 6)


class Firework:
    def __init__(self, rocket):
        self.rocket = rocket
        self.particles = []

    def draw(self, screen):
        if not self.rocket.exploded:
            self.rocket.move()
            self.rocket.draw(screen)
            return False

        if not self.particles:
            self.particles = [Particle(self.rocket.x, self.rocket.y, self.rocket.color) for _ in range(50)]

        self.particles = [particle for particle in self.particles if not particle.move()]
        for particle in self.particles:
            particle.draw(screen)

        return len(self.particles) == 0


fireworks = []
counter = 10

def countdown():
    global counter
    if counter > 0:
        counter -= 1
        time.sleep(1)

text_timer = 0
takbiran_timer = 0
takbiran_playing = False

target_time = datetime.now(JAKARTA).replace(hour=19, minute=30, second=0, microsecond=0)
if datetime.now(JAKARTA) > target_time:
    target_time += timedelta(days=1)

clock = pygame.time.Clock()

while True:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    current_time = datetime.now(JAKARTA)
    remaining_time = target_time - current_time

    if fireworks_active and countdown_played:
        countdown_played = False
        countdown_channel.stop()

    if remaining_time > timedelta(seconds=0):
        countdown_color = GREEN
        if remaining_time <= timedelta(seconds=10):
            countdown_color = RED
            if not countdown_played:
                countdown_channel = mixer.find_channel()
                countdown_channel.play(countdown_sound)
                countdown_played = True

        countdown_text = font.render(str(remaining_time).split('.')[0], True, countdown_color)
        subheader_text = subheader_font.render("Sisa Waktu Mulai Malam Takbiran IED Fitri 2023", True, countdown_color)
        screen.blit(subheader_text,
                    (WIDTH // 2 - subheader_text.get_width() // 2, HEIGHT // 2 - countdown_text.get_height() // 2 - 40))

        countdown_text = font.render(str(remaining_time).split('.')[0], True, countdown_color)
        screen.blit(countdown_text,
                    (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 - countdown_text.get_height() // 2))

    if current_time >= target_time:
        text_timer += 1
        takbiran_timer += 1
        fireworks_active = True

        if takbiran_timer >= 15 * 60 and not takbiran_playing:
            takbiran_channel = mixer.find_channel()
            if takbiran_channel:
                takbiran_channel.play(takbiran_sound, loops=-1)  # Loop takbiran sound
                takbiran_playing = True

        if 15 * 60 <= text_timer <= 160 * 60:
            text_to_show = f"Malam Takbiran\nIdul Fitri\n 2023"
            text_lines = text_to_show.split('\n')
            for i, line in enumerate(text_lines):
                rendered_line = subheader_font.render(line, True, WHITE)
                screen.blit(rendered_line, (WIDTH // 2 - rendered_line.get_width() // 2, HEIGHT // 4 - 30 + i * 30))

        if random.random() < 0.02:
            rocket = Rocket()
            fireworks.append(Firework(rocket))

        fireworks = [firework for firework in fireworks if not firework.draw(screen)]

    pygame.display.flip()
    clock.tick(60)