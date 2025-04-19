import pygame
import sys
import math
import random

pygame.init()

# Setup
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 Solar System Simulation")
clock = pygame.time.Clock()

# Constants
G = 6.67430e-1  # Tweaked gravitational constant
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
paused = False

# Camera
zoom = 1.0
offset_x = 0
offset_y = 0
dragging = False
drag_start = None

bodies = []

class Body:
    def __init__(self, x, y, radius, color, mass, vx=0, vy=0, is_static=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.vx = vx
        self.vy = vy
        self.is_static = is_static
        self.trail = []

    def screen_pos(self):
        return (
            int((self.x + offset_x) * zoom + WIDTH / 2),
            int((self.y + offset_y) * zoom + HEIGHT / 2)
        )

    def draw(self):
        # Trail
        if len(self.trail) > 2:
            points = [
                ((px + offset_x) * zoom + WIDTH / 2, (py + offset_y) * zoom + HEIGHT / 2)
                for px, py in self.trail
            ]
            pygame.draw.lines(screen, self.color, False, points, 1)

        # Body
        pygame.draw.circle(screen, self.color, self.screen_pos(), max(int(self.radius * zoom), 2))

    def update(self):
        if self.is_static or paused:
            return

        fx = fy = 0
        for other in bodies:
            if other is self:
                continue
            dx = other.x - self.x
            dy = other.y - self.y
            distance = math.hypot(dx, dy)
            if distance == 0:
                continue

            # Collision check
            if distance < self.radius + other.radius:
                self.merge(other)
                continue

            # Gravity
            force = G * self.mass * other.mass / distance**2
            angle = math.atan2(dy, dx)
            fx += math.cos(angle) * force
            fy += math.sin(angle) * force

        # Apply force
        self.vx += fx / self.mass
        self.vy += fy / self.mass
        self.x += self.vx
        self.y += self.vy

        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 150:
            self.trail.pop(0)

    def merge(self, other):
        if other.is_static:
            return
        if self.mass < other.mass:
            other.mass += self.mass
            other.vx = (other.vx * other.mass + self.vx * self.mass) / (self.mass + other.mass)
            other.vy = (other.vy * other.mass + self.vy * self.mass) / (self.mass + other.mass)
            other.radius = math.sqrt(other.radius**2 + self.radius**2)
            if self in bodies:
                bodies.remove(self)
        else:
            self.mass += other.mass
            self.vx = (self.vx * self.mass + other.vx * other.mass) / (self.mass + other.mass)
            self.vy = (self.vy * self.mass + other.vy * other.mass) / (self.mass + other.mass)
            self.radius = math.sqrt(self.radius**2 + other.radius**2)
            if other in bodies:
                bodies.remove(other)

# 🌞 Add Sun
sun = Body(0, 0, 20, (255, 204, 0), mass=10000, is_static=True)
bodies.append(sun)

def add_planet(pos=None):
    # Orbiting from center or mouse
    angle = random.uniform(0, 2 * math.pi)
    dist = random.randint(100, 400)
    x = math.cos(angle) * dist
    y = math.sin(angle) * dist

    if pos:
        mx, my = pos
        x = (mx - WIDTH / 2) / zoom - offset_x
        y = (my - HEIGHT / 2) / zoom - offset_y

    distance = math.hypot(x, y)
    speed = math.sqrt(G * sun.mass / distance)
    vx = -math.sin(angle) * speed
    vy = math.cos(angle) * speed

    planet = Body(x, y, radius=6, color=(0, 150, 255), mass=5, vx=vx, vy=vy)
    bodies.append(planet)

def add_asteroid():
    x = random.randint(-WIDTH, WIDTH)
    y = random.randint(-HEIGHT, HEIGHT)
    vx = random.uniform(-2, 2)
    vy = random.uniform(-2, 2)
    asteroid = Body(x, y, radius=3, color=(150, 150, 150), mass=1, vx=vx, vy=vy)
    bodies.append(asteroid)

# 🌌 Main loop
while True:
    screen.fill(BLACK)

    # 🖱️ Handle input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # KEYBOARD
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_a:
                add_planet()
            elif event.key == pygame.K_s:
                add_asteroid()
            elif event.key == pygame.K_d and len(bodies) > 1:
                bodies.pop()
            elif event.key == pygame.K_EQUALS:
                zoom *= 1.1
            elif event.key == pygame.K_MINUS:
                zoom /= 1.1

        # MOUSE
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click = add planet
                add_planet(event.pos)
            elif event.button == 2:  # Middle click = reset camera
                offset_x = offset_y = 0
                zoom = 1.0
            elif event.button == 3:  # Right click = start dragging
                dragging = True
                drag_start = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            dx = event.pos[0] - drag_start[0]
            dy = event.pos[1] - drag_start[1]
            offset_x += dx / zoom
            offset_y += dy / zoom
            drag_start = event.pos

    # Update + draw bodies
    for body in bodies[:]:
        body.update()
        body.draw()

    # UI Info
    font = pygame.font.SysFont("consolas", 18)
    info = f"[A]dd Planet  [S] Asteroid  [D] Delete  [P] Pause  [+/-] Zoom"
    screen.blit(font.render(info, True, WHITE), (10, 10))

    pygame.display.flip()
    clock.tick(60)
