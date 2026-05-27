import pygame

WIDTH = 800
HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)

WAYPOINTS = [(50, 50), (700, 50), (700, 500), (50, 500), (50, 300), (800, 300)]

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=WAYPOINTS[0])
        self.pos = pygame.Vector2(WAYPOINTS[0])
        self.target_waypoint = 1
        self.speed = 2
        self.health = 10

    def update(self):
        if self.target_waypoint < len(WAYPOINTS):
            target = pygame.Vector2(WAYPOINTS[self.target_waypoint])
            direction = (target - self.pos)
            if direction.length() > 0:
                direction = direction.normalize()
            
            self.pos += direction * self.speed
            self.rect.center = self.pos

            if self.pos.distance_to(target) < 5:
                self.target_waypoint += 1
        else:
            self.kill()

class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.range = 150
        self.cooldown = 0
        self.fire_rate = 30

    def update(self, enemies, projectiles):
        if self.cooldown > 0:
            self.cooldown -= 1
        
        for enemy in enemies:
            dist = pygame.Vector2(self.rect.center).distance_to(enemy.pos)
            if dist <= self.range and self.cooldown == 0:
                projectiles.add(Projectile(self.rect.center, enemy))
                self.cooldown = self.fire_rate
                break

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.Vector2(start_pos)
        self.target = target
        self.speed = 7

    def update(self):
        if not self.target.alive():
            self.kill()
            return

        direction = (self.target.pos - self.pos).normalize()
        self.pos += direction * self.speed
        self.rect.center = self.pos

        if self.rect.colliderect(self.target.rect):
            self.target.health -= 5
            if self.target.health <= 0:
                self.target.kill()
            self.kill()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    enemies = pygame.sprite.Group()
    towers = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()

    spawn_timer = 0
    running = True
    
    while running:
        screen.fill(GREEN)
        
        if len(WAYPOINTS) > 1:
            pygame.draw.lines(screen, WHITE, False, WAYPOINTS, 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                towers.add(Tower(mx, my))

        spawn_timer += 1
        if spawn_timer >= 60:
            enemies.add(Enemy())
            spawn_timer = 0

        enemies.update()
        towers.update(enemies, projectiles)
        projectiles.update()

        towers.draw(screen)
        enemies.draw(screen)
        projectiles.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

main()