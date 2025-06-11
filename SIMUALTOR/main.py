import pygame
import math
import random

# --- 상수 ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# --- Pygame 초기화 ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Physics Simulator")
clock = pygame.time.Clock()

try:
    font = pygame.font.Font("Pretendard-Regular.otf", 20)
    small_font = pygame.font.Font("Pretendard-Regular.otf", 16)
except:
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)

# --- 게임 객체 클래스 ---
class GameObject:
    def __init__(self, x, y, radius, color, mass=1.0, is_static=False):
        self.pos = pygame.math.Vector2(x, y)
        self.radius = radius
        self.color = color
        self.mass = mass if not is_static else float('inf')
        self.is_static = is_static
        self.velocity = pygame.math.Vector2(0, 0)
        self.external_force = pygame.math.Vector2(0, 0)
        self.selected = False

    def apply_force(self, force_vector):
        if not self.is_static:
            acceleration = force_vector / self.mass
            self.velocity += acceleration

    def check_collision(self, other):
        """다른 객체와의 충돌 검사"""
        if self == other or (self.is_static and other.is_static):
            return False
        
        distance = self.pos.distance_to(other.pos)
        return distance < (self.radius + other.radius)

    def resolve_collision(self, other):
        if self.is_static and other.is_static:
            return
        
        # 두 공의 중심 사이의 거리와 방향 계산 (피타고라스 정리 사용)
        dx = other.pos.x - self.pos.x  # x축 거리차
        dy = other.pos.y - self.pos.y  # y축 거리차
        distance = math.sqrt(dx*dx + dy*dy)  # 직선거리 = √(dx² + dy²)
        
        if distance == 0:
            return
        
        # 겹친 부분을 분리 (단순히 반반씩 밀어냄)
        overlap = (self.radius + other.radius) - distance
        
        # 방향을 단위벡터로 만들기 (전체 거리로 나누면 방향만 남음)
        direction_x = dx / distance  # x방향 (-1 ~ 1 사이 값)
        direction_y = dy / distance  # y방향 (-1 ~ 1 사이 값)
        
        # 겹친 만큼 객체들을 분리
        move_distance = overlap / 2
        if not self.is_static:
            self.pos.x -= direction_x * move_distance
            self.pos.y -= direction_y * move_distance
        if not other.is_static:
            other.pos.x += direction_x * move_distance
            other.pos.y += direction_y * move_distance
        
        # 충돌 방향으로의 속도만 계산 (내적 대신 단순 곱셈과 덧셈)
        # 각 공의 속도를 충돌 방향으로 투영
        v1_collision = self.velocity.x * direction_x + self.velocity.y * direction_y
        v2_collision = other.velocity.x * direction_x + other.velocity.y * direction_y
        
        # 이미 분리되고 있으면 더이상 처리하지 않음
        if v1_collision - v2_collision <= 0:
            return
        
        # 질량 처리 (정적 객체는 매우 무거운 것으로 처리)
        if self.is_static:
            m1 = 999999
        else:
            m1 = self.mass
            
        if other.is_static:
            m2 = 999999
        else:
            m2 = other.mass
        
        # 완전 탄성 충돌 공식 (고등학교 물리 공식 그대로)
        # 새로운 속도 = ((자신질량-상대질량) × 자신속도 + 2×상대질량×상대속도) ÷ (질량합)
        new_v1_collision = ((m1 - m2) * v1_collision + 2 * m2 * v2_collision) / (m1 + m2)
        new_v2_collision = ((m2 - m1) * v2_collision + 2 * m1 * v1_collision) / (m1 + m2)
        
        # 속도 변화량 계산
        v1_change = (new_v1_collision - v1_collision) 
        v2_change = (new_v2_collision - v2_collision) 
        
        # 충돌 방향으로만 속도 변경 (충돌과 수직인 방향은 그대로 유지)
        if not self.is_static:
            self.velocity.x += direction_x * v1_change
            self.velocity.y += direction_y * v1_change
        if not other.is_static:
            other.velocity.x += direction_x * v2_change
            other.velocity.y += direction_y * v2_change

    def update(self, dt):
        if not self.is_static:
            # 외부 힘이 있으면 지속적으로 적용
            if self.external_force.length_squared() > 0:
                self.apply_force(self.external_force * dt)

            self.pos += self.velocity * dt
            
            # 객체를 화면 경계 내에 유지
            if self.pos.x - self.radius < 0 or self.pos.x + self.radius > SCREEN_WIDTH:
                self.velocity.x *= -1  # 에너지 손실과 함께 반사
                self.pos.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.pos.x))
            
            if self.pos.y - self.radius < 0:
                self.velocity.y *= -1
                self.pos.y = self.radius
            
            if self.pos.y + self.radius > SCREEN_HEIGHT - 160:  # UI 영역 고려
                self.velocity.y *= -1
                self.pos.y = SCREEN_HEIGHT - 160 - self.radius

    def draw(self, surface):
        # 원 그리기
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), int(self.radius))
        
        if self.selected:
            pygame.draw.circle(surface, LIGHT_BLUE, (int(self.pos.x), int(self.pos.y)), 
                             int(self.radius + 3), 3)

    def is_clicked(self, mouse_pos):
        return self.pos.distance_to(mouse_pos) < self.radius

# --- 게임 변수 ---
objects = []
selected_object: GameObject = None
dragging = False
show_debug_info = True
input_mode = None  # 커스텀 힘 입력용: "force_x", "force_y", None
input_text = ""  # 현재 입력 텍스트
current_input_force = [0, 0]  # 커스텀 힘을 위한 [x, y]

# --- 헬퍼 함수 ---
def draw_text(text, position, surface, color=BLACK, font_size="normal"):
    chosen_font = font if font_size == "normal" else small_font
    text_surface = chosen_font.render(text, True, color)
    surface.blit(text_surface, position)

# --- 메인 게임 루프 ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # 델타 타임 (초 단위)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # 커스텀 힘 입력 처리
            if input_mode is not None:
                if event.key == pygame.K_RETURN:  # 엔터로 입력 확인
                    try:
                        force_value = float(input_text)
                        if input_mode == "force_x":
                            current_input_force[0] = force_value
                            input_mode = "force_y"
                            input_text = ""
                        elif input_mode == "force_y":
                            current_input_force[1] = force_value
                            if selected_object:
                                selected_object.external_force = pygame.math.Vector2(current_input_force[0], current_input_force[1])
                            input_mode = None
                            input_text = ""
                            current_input_force = [0, 0]
                    except ValueError:
                        input_mode = None
                        input_text = ""
                        current_input_force = [0, 0]
                elif event.key == pygame.K_ESCAPE:  # ESC로 입력 취소
                    input_mode = None
                    input_text = ""
                    current_input_force = [0, 0]
                elif event.key == pygame.K_BACKSPACE:  # 백스페이스로 문자 삭제
                    input_text = input_text[:-1]
                elif event.key == pygame.K_MINUS:  # 마이너스 기호
                    if len(input_text) == 0:
                        input_text += "-"
                elif event.unicode.isdigit() or event.unicode == ".":  # 숫자와 소수점
                    input_text += event.unicode
                continue  # 입력 중에는 다른 키 처리하지 않음
            
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_c:  # 원 추가
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT - 250)
                radius = random.randint(15, 40)
                color = random.choice([RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE])
                objects.append(GameObject(x, y, radius, color, mass=2.0))
            if event.key == pygame.K_d:  # 디버그 정보 토글
                show_debug_info = not show_debug_info
            if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:  # 선택된 객체 삭제
                if selected_object and selected_object in objects:
                    objects.remove(selected_object)
                    selected_object = None
            
            # 선택된 객체가 있을 때의 조작
            if selected_object:
                if event.key == pygame.K_s:  # 정적 상태 토글
                    selected_object.is_static = not selected_object.is_static
                    selected_object.mass = float('inf') if selected_object.is_static else random.uniform(1.0, 5.0)
                    selected_object.velocity = pygame.math.Vector2(0, 0)
                if event.key == pygame.K_UP:  # 질량 증가
                    if not selected_object.is_static:
                        selected_object.mass = round(selected_object.mass + 0.5, 1)
                if event.key == pygame.K_DOWN:  # 질량 감소
                    if not selected_object.is_static and selected_object.mass > 0.5:
                        selected_object.mass = round(selected_object.mass - 0.5, 1)
                if event.key == pygame.K_v:  # 개별 객체 중력 (아래 방향)
                    if selected_object.external_force.y > 0:
                        selected_object.external_force = pygame.math.Vector2(0, 0)
                    else:
                        selected_object.external_force = pygame.math.Vector2(0, 100*selected_object.mass)
                if event.key == pygame.K_x:  # 커스텀 힘 입력
                    input_mode = "force_x"
                    input_text = ""
                    current_input_force = [0, 0]

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 왼쪽 클릭
                clicked_on_object = False
                for obj in reversed(objects):  # 최상단 객체부터 확인
                    if obj.is_clicked(event.pos):
                        if selected_object:
                            selected_object.selected = False
                        selected_object = obj
                        selected_object.selected = True
                        dragging = True
                        clicked_on_object = True
                        break
                if not clicked_on_object:
                    if selected_object:
                        selected_object.selected = False
                    selected_object = None
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 왼쪽 클릭
                dragging = False

        if event.type == pygame.MOUSEMOTION:
            if dragging and selected_object:
                selected_object.pos = pygame.math.Vector2(event.pos)
                # 드래그된 객체를 경계 내에 유지
                selected_object.pos.x = max(selected_object.radius, min(SCREEN_WIDTH - selected_object.radius, selected_object.pos.x))
                selected_object.pos.y = max(selected_object.radius, min(SCREEN_HEIGHT - 200, selected_object.pos.y))
                if not selected_object.is_static:
                    selected_object.velocity = pygame.math.Vector2(0, 0)

    # --- 게임 로직 ---
    
    # 모든 객체 업데이트
    for obj in objects:
        obj.update(dt)
    
    # 모든 객체 간 충돌 검사
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            obj1 = objects[i]
            obj2 = objects[j]
            if obj1.check_collision(obj2):
                obj1.resolve_collision(obj2)

    # --- 그리기 ---
    screen.fill(WHITE)
    for obj in objects:
        obj.draw(screen)

    # --- UI 및 정보 ---
    ui_start_y = SCREEN_HEIGHT - 150
    pygame.draw.rect(screen, GRAY, (0, ui_start_y, SCREEN_WIDTH, 150))
    
    # 조작법 안내
    draw_text("조작법: (C)원 추가", 
              (10, ui_start_y + 5), screen, BLACK, "small")
    draw_text("(DEL)선택된 객체 삭제 | (D)정보 표시 토글 | (S)정지/움직임 토글", 
              (10, ui_start_y + 25), screen, BLACK, "small")
    draw_text("선택된 객체: (↑/↓)질량 | (V)개별 중력 토글 | (X)커스텀 외력 설정", 
              (10, ui_start_y + 45), screen, BLACK, "small")
    draw_text("마우스로 클릭해서 선택하고 드래그로 이동", 
              (10, ui_start_y + 65), screen, BLACK, "small")

    # 커스텀 힘 입력 표시
    if input_mode is not None:
        if input_mode == "force_x":
            draw_text(f"X축 힘 입력: {input_text}_", (SCREEN_WIDTH - 300, ui_start_y + 45), screen, RED, "small")
        elif input_mode == "force_y":
            draw_text(f"Y축 힘 입력: {input_text}_ (X: {current_input_force[0]})", (SCREEN_WIDTH - 300, ui_start_y + 45), screen, RED, "small")

    # 객체 정보
    if selected_object and show_debug_info:
        info_text = [
            f"선택된 객체: 원",
            f"  위치: ({selected_object.pos.x:.1f}, {selected_object.pos.y:.1f})",
            f"  질량: {'정지' if selected_object.is_static else f'{selected_object.mass:.1f}'}",
            f"  속도: ({selected_object.velocity.x:.1f}, {selected_object.velocity.y:.1f})",
            f"  외부 힘: ({selected_object.external_force.x:.1f}, {selected_object.external_force.y:.1f})"
        ]
        for i, line in enumerate(info_text):
            draw_text(line, (10, 10 + i * 22), screen, BLACK, "small")
    elif show_debug_info:
        draw_text("객체를 클릭해서 선택하세요.", (10, 10), screen, BLACK, "small")

    # 객체 개수 표시
    draw_text(f"총 객체 수: {len(objects)}", (SCREEN_WIDTH - 150, 10), screen, BLACK, "small")

    pygame.display.flip()

pygame.quit()
