import pygame
import math
import random

# --- Constants ---
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

# --- Pygame Initialization ---
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

# --- GameObject Class ---
class GameObject:
    def __init__(self, x, y, radius, color, mass=1.0, is_static=False):
        self.pos = pygame.math.Vector2(x, y)
        self.radius = radius
        self.color = color
        self.mass = mass if not is_static else float('inf')
        self.is_static = is_static
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0  # Degrees
        self.angular_velocity = 0  # Degrees per second
        self.external_force = pygame.math.Vector2(0, 0)
        self.selected = False

    def apply_force(self, force_vector):
        if not self.is_static:
            acceleration = force_vector / self.mass
            self.velocity += acceleration

    def check_collision(self, other):
        """Check collision with another object"""
        if self == other or (self.is_static and other.is_static):
            return False
        
        distance = self.pos.distance_to(other.pos)
        return distance < (self.radius + other.radius)

    def resolve_collision(self, other):
        """Resolve collision with another object"""
        if self.is_static and other.is_static:
            return
        
        # Calculate collision vector
        collision_vector = other.pos - self.pos
        distance = collision_vector.length()
        
        if distance == 0:
            return
        
        # Normalize collision vector
        collision_normal = collision_vector / distance
        
        # Separate objects
        overlap = (self.radius + other.radius) - distance
        separation = collision_normal * (overlap / 2)
        
        if not self.is_static:
            self.pos -= separation
        if not other.is_static:
            other.pos += separation
        
        # Calculate relative velocity
        relative_velocity = other.velocity - self.velocity
        velocity_along_normal = relative_velocity.dot(collision_normal)
        
        # Don't resolve if velocities are separating
        if velocity_along_normal > 0:
            return
        
        # Calculate restitution (bounciness)
        restitution = 0.8
        
        # Calculate impulse scalar
        impulse_scalar = -(1 + restitution) * velocity_along_normal
        impulse_scalar /= (1/self.mass + 1/other.mass) if not self.is_static and not other.is_static else 1
        
        # Apply impulse
        impulse = impulse_scalar * collision_normal
        
        if not self.is_static:
            self.velocity -= impulse / self.mass
        if not other.is_static:
            other.velocity += impulse / other.mass

    def update(self, dt):
        if not self.is_static:
            # Apply external force (if any) continuously
            if self.external_force.length_squared() > 0:
                self.apply_force(self.external_force * dt)

            # Apply simple damping to prevent infinite acceleration
            self.velocity *= 0.999

            self.pos += self.velocity * dt
            self.angle = (self.angle + self.angular_velocity * dt) % 360
            
            # Keep objects within screen bounds
            if self.pos.x - self.radius < 0 or self.pos.x + self.radius > SCREEN_WIDTH:
                self.velocity.x *= -0.8  # Bounce with energy loss
                self.pos.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.pos.x))
            
            if self.pos.y - self.radius < 0:
                self.velocity.y *= -0.8
                self.pos.y = self.radius
            
            if self.pos.y + self.radius > SCREEN_HEIGHT - 160:  # Account for UI area
                self.velocity.y *= -0.8
                self.pos.y = SCREEN_HEIGHT - 160 - self.radius

    def draw(self, surface):
        # Draw circle
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), int(self.radius))
        
        # Draw a line to indicate angle
        end_x = self.pos.x + self.radius * math.cos(math.radians(self.angle))
        end_y = self.pos.y + self.radius * math.sin(math.radians(self.angle))
        pygame.draw.line(surface, BLACK, self.pos, (end_x, end_y), 2)
        
        if self.selected:
            pygame.draw.circle(surface, LIGHT_BLUE, (int(self.pos.x), int(self.pos.y)), 
                             int(self.radius + 3), 3)

    def is_clicked(self, mouse_pos):
        return self.pos.distance_to(mouse_pos) < self.radius

# --- Game Variables ---
objects = []
selected_object = None
dragging = False
show_debug_info = True
gravity_enabled = False  # Global gravity toggle

# --- Helper Functions ---
def draw_text(text, position, surface, color=BLACK, font_size="normal"):
    chosen_font = font if font_size == "normal" else small_font
    text_surface = chosen_font.render(text, True, color)
    surface.blit(text_surface, position)

def create_random_object():
    x = random.randint(100, SCREEN_WIDTH - 100)
    y = random.randint(100, SCREEN_HEIGHT - 250)
    radius = random.randint(15, 40)
    color = random.choice([RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE])
    mass = random.uniform(0.5, 5.0)
    is_static = random.choice([True, False])
    return GameObject(x, y, radius, color, mass, is_static)

# --- Main Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_a:  # Add a new random object
                objects.append(create_random_object())
            if event.key == pygame.K_c:  # Add circle
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT - 250)
                radius = random.randint(15, 40)
                color = random.choice([RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE])
                objects.append(GameObject(x, y, radius, color, mass=2.0))
            if event.key == pygame.K_d:  # Toggle debug info
                show_debug_info = not show_debug_info
            if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:  # Delete selected object
                if selected_object and selected_object in objects:
                    objects.remove(selected_object)
                    selected_object = None
            if event.key == pygame.K_z:  # Toggle global gravity
                gravity_enabled = not gravity_enabled
            
            # Controls for selected object (if any)
            if selected_object:
                if event.key == pygame.K_s:  # Toggle static state
                    selected_object.is_static = not selected_object.is_static
                    selected_object.mass = float('inf') if selected_object.is_static else random.uniform(1.0, 5.0)
                    selected_object.velocity = pygame.math.Vector2(0, 0)
                if event.key == pygame.K_UP:  # Increase mass
                    if not selected_object.is_static:
                        selected_object.mass = round(selected_object.mass + 0.5, 1)
                if event.key == pygame.K_DOWN:  # Decrease mass
                    if not selected_object.is_static and selected_object.mass > 0.5:
                        selected_object.mass = round(selected_object.mass - 0.5, 1)
                if event.key == pygame.K_LEFT:  # Rotate counter-clockwise
                    selected_object.angular_velocity -= 20
                if event.key == pygame.K_RIGHT:  # Rotate clockwise
                    selected_object.angular_velocity += 20
                if event.key == pygame.K_SPACE:  # Stop rotation
                    selected_object.angular_velocity = 0
                
                # External forces
                if event.key == pygame.K_f:  # Force right
                    if selected_object.external_force.x > 0:
                        selected_object.external_force = pygame.math.Vector2(0, 0)
                    else:
                        selected_object.external_force = pygame.math.Vector2(100, 0)
                if event.key == pygame.K_v:  # Gravity down (individual object)
                    if selected_object.external_force.y > 0:
                        selected_object.external_force = pygame.math.Vector2(0, 0)
                    else:
                        selected_object.external_force = pygame.math.Vector2(0, 200)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                clicked_on_object = False
                for obj in reversed(objects):  # Check topmost object first
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
            if event.button == 1:  # Left click
                dragging = False

        if event.type == pygame.MOUSEMOTION:
            if dragging and selected_object:
                selected_object.pos = pygame.math.Vector2(event.pos)
                # Keep dragged object within bounds
                selected_object.pos.x = max(selected_object.radius, min(SCREEN_WIDTH - selected_object.radius, selected_object.pos.x))
                selected_object.pos.y = max(selected_object.radius, min(SCREEN_HEIGHT - 200, selected_object.pos.y))
                if not selected_object.is_static:
                    selected_object.velocity = pygame.math.Vector2(0, 0)

    # --- Game Logic ---
    # Apply global gravity if enabled
    if gravity_enabled:
        for obj in objects:
            if not obj.is_static:
                obj.apply_force(pygame.math.Vector2(0, obj.mass * 200 * dt))  # Gravity force
    
    # Update all objects
    for obj in objects:
        obj.update(dt)
    
    # Check collisions between all objects
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            obj1 = objects[i]
            obj2 = objects[j]
            if obj1.check_collision(obj2):
                obj1.resolve_collision(obj2)

    # --- Drawing ---
    screen.fill(WHITE)
    for obj in objects:
        obj.draw(screen)

    # --- UI & Info ---
    ui_start_y = SCREEN_HEIGHT - 150
    pygame.draw.rect(screen, GRAY, (0, ui_start_y, SCREEN_WIDTH, 150))
    
    # Control instructions
    draw_text("조작법: (A)무작위 객체 | (C)원 추가", 
              (10, ui_start_y + 5), screen, BLACK, "small")
    draw_text("(DEL)선택된 객체 삭제 | (D)정보 표시 토글 | (S)정지/움직임 토글 | (Z)전체 중력 토글", 
              (10, ui_start_y + 25), screen, BLACK, "small")
    draw_text("선택된 객체: (↑/↓)질량 | (←/→)회전 | (SPACE)회전 정지", 
              (10, ui_start_y + 45), screen, BLACK, "small")
    draw_text("(F)오른쪽 힘 토글 | (V)개별 중력 토글", 
              (10, ui_start_y + 65), screen, BLACK, "small")
    draw_text("마우스로 클릭해서 선택하고 드래그로 이동", 
              (10, ui_start_y + 85), screen, BLACK, "small")

    # Gravity status
    gravity_status = "켜짐" if gravity_enabled else "꺼짐"
    draw_text(f"전체 중력: {gravity_status}", (SCREEN_WIDTH - 150, ui_start_y + 5), screen, BLACK, "small")

    # Object info
    if selected_object and show_debug_info:
        info_text = [
            f"선택된 객체: 원",
            f"  위치: ({selected_object.pos.x:.1f}, {selected_object.pos.y:.1f})",
            f"  질량: {'정지' if selected_object.is_static else f'{selected_object.mass:.1f}'}",
            f"  속도: ({selected_object.velocity.x:.1f}, {selected_object.velocity.y:.1f})",
            f"  각도: {selected_object.angle:.1f}°",
            f"  각속도: {selected_object.angular_velocity:.1f}°/s",
            f"  외부 힘: ({selected_object.external_force.x:.1f}, {selected_object.external_force.y:.1f})"
        ]
        for i, line in enumerate(info_text):
            draw_text(line, (10, 10 + i * 22), screen, BLACK, "small")
    elif show_debug_info:
        draw_text("객체를 클릭해서 선택하세요.", (10, 10), screen, BLACK, "small")

    # Show object count
    draw_text(f"총 객체 수: {len(objects)}", (SCREEN_WIDTH - 150, 10), screen, BLACK, "small")

    pygame.display.flip()

pygame.quit()
