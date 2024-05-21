import pygame
import random

# 초기화
pygame.init()

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 화면 크기 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# 플레이어 크기 설정 (크기 줄임)
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30

# 적 크기 설정 (크기 줄임)
ENEMY_WIDTH = 30
ENEMY_HEIGHT = 30

# 화면 생성
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooting Game")

# 폰트 설정
font = pygame.font.SysFont("game.ttf", 25)

# 체력 바 그리기 함수
def draw_health_bar(screen, x, y, health, max_health):
    BAR_WIDTH = 30
    BAR_HEIGHT = 5
    fill = (health / max_health) * BAR_WIDTH
    border = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
    fill = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(screen, RED, border, 2)
    pygame.draw.rect(screen, GREEN, fill)

# 플레이어 클래스
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT // 2)
        self.health = 100
        self.shoot_delay = 250  # 총알 발사 간격 (밀리초)
        self.last_shot = pygame.time.get_ticks()  # 마지막 총알 발사 시간
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += 5
        # 총알 발사
        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top, -10)
            all_sprites.add(bullet)
            bullets.add(bullet)

# 적 클래스
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([ENEMY_WIDTH, ENEMY_HEIGHT])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
        self.rect.y = random.randint(-100, -40)
        self.speed_y = random.randint(1, 5)
        self.health = 30
        self.shoot_delay = 1000  # 적의 총알 발사 간격 (밀리초)
        self.last_shot = pygame.time.get_ticks()  # 마지막 총알 발사 시간
    
    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
            self.rect.y = random.randint(-100, -40)
            self.speed_y = random.randint(1, 5)
        # 적이 총알 발사
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()

    def shoot(self):
        enemy_bullet = Bullet(self.rect.centerx, self.rect.bottom, 5)
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)

# 총알 클래스
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y):
        super().__init__()
        self.image = pygame.Surface([5, 10])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_y = speed_y
    
    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

# 스프라이트 그룹 생성
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

# 플레이어 생성
player = Player()
all_sprites.add(player)

# 적 생성 함수
def spawn_enemy():
    if len(enemies) < 10:
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

# 초기 적 생성
for i in range(10):
    spawn_enemy()

# 점수 초기화
score = 0

# 게임 상태 초기화
game_over = False

# 게임 루프
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    # 게임 재시작
                    player = Player()
                    all_sprites.add(player)
                    for enemy in enemies:
                        enemy.kill()
                    enemies.empty()
                    bullets.empty()
                    enemy_bullets.empty()
                    for i in range(10):
                        spawn_enemy()
                    score = 0
                    game_over = False
            else:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.top, -10)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
    
    if not game_over:
        # 스프라이트 업데이트
        all_sprites.update()
        
        # 적과 총알 충돌 처리
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for hit in hits:
            hit.health -= 10
            if hit.health <= 0:
                hit.kill()
                score += 1
                spawn_enemy()
        
        # 플레이어와 적의 총알 충돌 처리
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for hit in hits:
            player.health -= 10
            if player.health <= 0:
                game_over = True
        
    # 화면에 그리기
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    if not game_over:
        # 체력 바 그리기
        draw_health_bar(screen, player.rect.x, player.rect.y - 10, player.health, 100)
        for enemy in enemies:
            draw_health_bar(screen, enemy.rect.x, enemy.rect.y - 10, enemy.health, 30)
    
        # 점수 표시
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, [10, 10])
    else:
        # 게임 오버 메시지
        game_over_text = font.render("Game Over! Press 'R' to Restart", True, WHITE)
        screen.blit(game_over_text, [SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2])
    
    # 화면 업데이트
    pygame.display.flip()
    
    # 프레임 설정
    clock.tick(60)

pygame.quit()
