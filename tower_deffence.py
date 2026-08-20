import pygame
import random

WIDTH = 800
HEIGHT = 600
FPS = 60
MAX_TOWERS = 20
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GREY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)

WAYPOINTS = [(50, 50), (700, 50), (700, 500), (50, 500), (50, 300), (800, 300)]

ENEMY_TYPES = {
    "basic": {
        "health": 15,
        "speed": 2,
        "color": RED,
        "size": (30, 30),
        "value": 10
    },
    "fast": {
        "health": 8,
        "speed": 4,
        "color": (255, 140, 0),
        "size": (20, 20),
        "value": 15
    },
    "tank": {
        "health": 45,
        "speed": 1,
        "color": (128, 0, 128),
        "size": (40, 40),
        "value": 30
    }
}

TOWER_TYPES = {
    "basic": {
        "range": 130,
        "fire_rate": 60,
        "damage": 5,
        "color": BLUE,
        "size": (40, 40),
        "cost": 250
    },
    "sniper": {
        "range": 280,
        "fire_rate": 120,
        "damage": 20,
        "color": BLACK,
        "size": (30, 30),
        "cost": 650
    }
}

class Base:
    def __init__(self):
        self.health = 100
        self.max_health = 100
        self.pos = WAYPOINTS[-1]
        self.rect = pygame.Rect(self.pos[0] - 60, self.pos[1] - 30, 60, 60)

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        bar_width = 200
        bar_height = 20
        fill = (max(0, self.health) / self.max_health) * bar_width
        outline_rect = pygame.Rect(WIDTH // 2 - bar_width // 2, 10, bar_width, bar_height)
        fill_rect = pygame.Rect(WIDTH // 2 - bar_width // 2, 10, fill, bar_height)

        pygame.draw.rect(screen, RED, outline_rect)
        pygame.draw.rect(screen, GREEN, fill_rect)
        pygame.draw.rect(screen, WHITE, outline_rect, 2)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, base, enemy_type="basic"):
        super().__init__()
        data = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["basic"])

        self.image = pygame.Surface(data["size"])
        self.image.fill(data["color"])
        self.rect = self.image.get_rect(center=WAYPOINTS[0])
        self.pos = pygame.Vector2(WAYPOINTS[0])
        self.target_waypoint = 1
        self.speed = data["speed"]
        self.health = data["health"]
        self.value = data["value"]
        self.base = base

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
            self.base.health -= 10
            self.kill()

class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y, tower_type="basic"):
        super().__init__()
        data = TOWER_TYPES.get(tower_type, TOWER_TYPES["basic"])

        self.image = pygame.Surface(data["size"])
        self.image.fill(data["color"])
        self.rect = self.image.get_rect(center=(x, y))
        self.range = data["range"]
        self.damage = data["damage"]
        self.fire_rate = data["fire_rate"]
        self.cooldown = 0

    def update(self, enemies, projectiles):
        if self.cooldown > 0:
            self.cooldown -= 1

        for enemy in enemies:
            dist = pygame.Vector2(self.rect.center).distance_to(enemy.pos)
            if dist <= self.range and self.cooldown == 0:
                projectiles.add(Projectile(self.rect.center, enemy, self.damage))
                self.cooldown = self.fire_rate
                break

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target, damage=5):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.Vector2(start_pos)
        self.target = target
        self.speed = 7
        self.damage = damage

    def update(self):
        if not self.target.alive():
            self.kill()
            return 0

        direction = self.target.pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()

        self.pos += direction * self.speed
        self.rect.center = self.pos

        if self.rect.colliderect(self.target.rect):
            self.target.health -= self.damage
            reward = 0
            if self.target.health <= 0:
                reward = self.target.value
                self.target.kill()
            self.kill()
            return reward
        return 0

class TowerSelector:
    def __init__(self, font):
        self.font = font
        self.tower_types = list(TOWER_TYPES.keys())
        self.selected_type = "basic"
        self.hovered_type = None

        self.panel_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT - 60, 320, 50)
        self.button_rects = {}

        btn_width = 140
        btn_height = 36
        spacing = 10
        start_x = self.panel_rect.x + spacing
        y = self.panel_rect.y + 7

        for i, tower_key in enumerate(self.tower_types):
            rect = pygame.Rect(start_x + i * (btn_width + spacing), y, btn_width, btn_height)
            self.button_rects[tower_key] = rect

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.panel_rect.collidepoint(event.pos):
                for tower_key, rect in self.button_rects.items():
                    if rect.collidepoint(event.pos):
                        self.selected_type = tower_key
                return True
        return False

    def update_hover(self, mouse_pos):
        self.hovered_type = None
        for tower_key, rect in self.button_rects.items():
            if rect.collidepoint(mouse_pos):
                self.hovered_type = tower_key
                break

    def draw(self, screen):
        pygame.draw.rect(screen, GREY, self.panel_rect)
        for tower_key, rect in self.button_rects.items():
            is_selected = (tower_key == self.selected_type)

            color = WHITE if is_selected else BLACK
            text_color = BLACK if is_selected else WHITE

            pygame.draw.rect(screen, color, rect)
            text_surf = self.font.render(tower_key.capitalize(), True, text_color)
            screen.blit(text_surf, text_surf.get_rect(center=rect.center))

        if self.hovered_type:
            self.draw_tooltip(screen, self.hovered_type)

    def draw(self, screen):
        pygame.draw.rect(screen, GREY, self.panel_rect)
        for tower_key, rect in self.button_rects.items():
            is_selected = (tower_key == self.selected_type)

            color = WHITE if is_selected else BLACK
            text_color = BLACK if is_selected else WHITE

            pygame.draw.rect(screen, color, rect)
            text_surf = self.font.render(tower_key.capitalize(), True, text_color)
            screen.blit(text_surf, text_surf.get_rect(center=rect.center))

        if self.hovered_type:
            self.draw_tooltip(screen, self.hovered_type)

    def draw_tooltip(self, screen, tower_type):
        data = TOWER_TYPES[tower_type]
        lines = [
            f"Type: {tower_type.capitalize()}",
            f"Damage: {data['damage']}",
            f"Range: {data['range']}",
            f"Fire Rate: {60 / data['fire_rate']:.1f}/sec"
        ]
        padding = 8
        line_height = self.font.get_linesize()
        box_width = 150
        box_height = (len(lines) * line_height) + (padding * 2)

        mx, my = pygame.mouse.get_pos()
        box_x = min(max(10, mx - box_width // 2), WIDTH - box_width - 10)
        box_y = self.panel_rect.y - box_height - 10

        tooltip_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, BLACK, tooltip_rect)

        for i, line in enumerate(lines):
            text_surf = self.font.render(line, True, WHITE)
            screen.blit(text_surf, (box_x + padding, box_y + padding + (i * line_height)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tower Defense - Base Health")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 48)
    small_font = pygame.font.SysFont("Arial", 24)
    selector = TowerSelector(small_font)

    background_file = "background.png"
    try:
        background_image = pygame.image.load(background_file).convert()
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    except (pygame.error, FileNotFoundError):
        background_image = None

    scrap = 400
    base = Base()
    enemies = pygame.sprite.Group()
    towers = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()

    spawn_timer = 0
    running = True
    game_over = False
    waiting_to_start = True

    while running:
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(GREEN)

        if len(WAYPOINTS) > 1:
            pygame.draw.lines(screen, WHITE, False, WAYPOINTS, 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            menu_clicked = selector.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if waiting_to_start:
                    waiting_to_start = False
                elif not game_over and not menu_clicked:
                    if len(towers) < MAX_TOWERS:
                        mx, my = pygame.mouse.get_pos()
                        towers.add(Tower(mx, my, tower_type=selector.selected_type))

        if not game_over and not waiting_to_start:
            spawn_timer += 1
            if spawn_timer >= 60:
                chosen_type = random.choice(list(ENEMY_TYPES.keys()))
                enemies.add(Enemy(base, enemy_type=chosen_type))
                spawn_timer = 0

            enemies.update()
            towers.update(enemies, projectiles)

            for proj in list(projectiles.sprites()):
                earned_scrap = proj.update()
                if earned_scrap:
                    scrap += earned_scrap

            if base.health <= 0:
                game_over = True

        selector.update_hover(pygame.mouse.get_pos())

        towers.draw(screen)
        enemies.draw(screen)
        projectiles.draw(screen)
        base.draw(screen)
        selector.draw(screen)

        scrap_text = small_font.render(f"Scrap: {scrap} | Towers: {len(towers)}/{MAX_TOWERS}", True, BLACK)
        screen.blit(scrap_text, (20, 10))

        if waiting_to_start:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160)) 
            screen.blit(overlay, (0, 0))

            title_text = font.render("OVERCLOCKED TOWER DEFENSE", True, WHITE)
            prompt_text = small_font.render("Click Anywhere to Start", True, WHITE)

            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 20))

        if game_over:
            text = font.render("GAME OVER", True, BLACK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
main()