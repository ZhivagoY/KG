import pygame
import math
import sys

pygame.init()

WIDTH, HEIGHT = 1000, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)


class CBasePoint:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.label = ""

    def transform(self, dx: float, dy: float, angle_degrees: float = 0, pivot_x: float = None, pivot_y: float = None):
        self.x += dx
        self.y += dy

        if angle_degrees != 0:
            if pivot_x is None:
                pivot_x = self.x
            if pivot_y is None:
                pivot_y = self.y

            self.rotate(angle_degrees, pivot_x, pivot_y)

    def rotate(self, angle_degrees: float, pivot_x: float, pivot_y: float):
        angle_rad = math.radians(angle_degrees)
        x_rel = self.x - pivot_x
        y_rel = self.y - pivot_y

        x_rotated = x_rel * math.cos(angle_rad) - y_rel * math.sin(angle_rad)
        y_rotated = x_rel * math.sin(angle_rad) + y_rel * math.cos(angle_rad)

        self.x = x_rotated + pivot_x
        self.y = y_rotated + pivot_y


class Polygon:
    def __init__(self, points):
        self.points = [CBasePoint(x, y) for x, y, _ in points]
        for i, (_, _, label) in enumerate(points):
            if label:
                self.points[i].label = label
        self.color = BLUE
        self.selected = False
        self.rotation_angle = 0

    def draw(self, surface):
        if len(self.points) >= 7:
            point_list = [
                (self.points[0].x, self.points[0].y),
                (self.points[5].x, self.points[5].y),
                (self.points[4].x, self.points[4].y),
                (self.points[3].x, self.points[3].y),
                (self.points[2].x, self.points[2].y),
                (self.points[6].x, self.points[6].y),
                (self.points[1].x, self.points[1].y)
            ]
            
            pygame.draw.polygon(surface, self.color, point_list, 0)
            
            line_color = (255, 0, 0) if self.selected else BLACK
            pygame.draw.polygon(surface, line_color, point_list, 2)
            
            pygame.draw.line(surface, BLACK, 
                           (self.points[0].x, self.points[0].y),
                           (self.points[5].x, self.points[5].y), 2)
            pygame.draw.line(surface, BLACK, 
                           (self.points[5].x, self.points[5].y),
                           (self.points[4].x, self.points[4].y), 2)
            
            pygame.draw.line(surface, BLACK, 
                           (self.points[1].x, self.points[1].y),
                           (self.points[6].x, self.points[6].y), 2)
            pygame.draw.line(surface, BLACK, 
                           (self.points[6].x, self.points[6].y),
                           (self.points[2].x, self.points[2].y), 2)

    def transform_position(self, angle_degrees: float = 0, dx: float = 0, dy: float = 0):
        if not self.points:
            return

        pivot = self.points[0]

        for point in self.points:
            point.transform(dx, dy, angle_degrees, pivot.x, pivot.y)
        
        self.rotation_angle += angle_degrees
        self.rotation_angle %= 360

    def translate(self, dx: float, dy: float):
        self.transform_position(0, dx, dy)

    def rotate(self, angle_degrees: float):
        self.transform_position(angle_degrees, 0, 0)

    def get_bounding_rect(self):
        if not self.points:
            return pygame.Rect(0, 0, 0, 0)

        min_x = min(point.x for point in self.points)
        min_y = min(point.y for point in self.points)
        max_x = max(point.x for point in self.points)
        max_y = max(point.y for point in self.points)

        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)


class Arrow(Polygon):
    def __init__(self, center_x: float, center_y: float, size: float = 100):
        self.direction = 270
        
        points = self.calculate_points(center_x, center_y, size)
        
        super().__init__(points)
        self.center_x = center_x
        self.center_y = center_y
        self.size = size
        self.rotation_angle = 270

    def calculate_points(self, center_x: float, center_y: float, size: float):
        arrow_length = size * 2.0
        base_width = size * 0.5
        tip_length = size * 1.0
        tip_width = size * 1.2
        
        a_x = center_x - base_width / 2
        a_y = center_y - arrow_length / 2
        
        b_x = center_x + base_width / 2
        b_y = a_y
        
        c_x = center_x + tip_width / 2
        c_y = a_y + tip_length
        
        d_x = center_x
        d_y = center_y + arrow_length / 2
        
        e_x = center_x - tip_width / 2
        e_y = c_y
        
        f_x = a_x
        f_y = e_y
        
        g_x = b_x
        g_y = c_y
        
        unrotated_points = [
            (a_x, a_y, ""),
            (b_x, b_y, ""),
            (c_x, c_y, ""),
            (d_x, d_y, ""),
            (e_x, e_y, ""),
            (f_x, f_y, ""),
            (g_x, g_y, "")
        ]
        
        rotated_points = []
        for x, y, label in unrotated_points:
            x_rel = x - center_x
            y_rel = y - center_y
            
            angle_rad = math.radians(self.direction)
            x_rotated = x_rel * math.cos(angle_rad) - y_rel * math.sin(angle_rad)
            y_rotated = x_rel * math.sin(angle_rad) + y_rel * math.cos(angle_rad)
            
            rotated_points.append((x_rotated + center_x, y_rotated + center_y, label))
        
        return rotated_points


class Painter:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Painter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 16)

        self.polygons = []
        self.create_arrow()
        self.selected_polygon = None

        self.rotation_step = 5
        self.translation_step = 5
        self.show_menu = True

    def create_arrow(self):
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        arrow_size = 80
        arrow = Arrow(center_x, center_y, arrow_size)
        self.polygons.append(arrow)
        self.selected_polygon = arrow

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                self.handle_keyboard_events(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_events(event)

        return True

    def handle_keyboard_events(self, event):
        if event.key == pygame.K_m:
            self.show_menu = not self.show_menu

        elif event.key == pygame.K_n:
            self.create_arrow()

        elif event.key == pygame.K_TAB:
            if self.polygons:
                if self.selected_polygon in self.polygons:
                    current_index = self.polygons.index(self.selected_polygon)
                    next_index = (current_index + 1) % len(self.polygons)
                else:
                    next_index = 0
                self.selected_polygon = self.polygons[next_index]

        elif event.key == pygame.K_DELETE:
            if self.selected_polygon in self.polygons:
                self.polygons.remove(self.selected_polygon)
                self.selected_polygon = self.polygons[0] if self.polygons else None

        if self.selected_polygon:
            if event.key == pygame.K_r:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_polygon.rotate(-self.rotation_step)
                else:
                    self.selected_polygon.rotate(self.rotation_step)

            elif event.key == pygame.K_UP:
                self.selected_polygon.translate(0, -self.translation_step)
            elif event.key == pygame.K_DOWN:
                self.selected_polygon.translate(0, self.translation_step)
            elif event.key == pygame.K_LEFT:
                self.selected_polygon.translate(-self.translation_step, 0)
            elif event.key == pygame.K_RIGHT:
                self.selected_polygon.translate(self.translation_step, 0)

    def handle_mouse_events(self, event):
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            for polygon in reversed(self.polygons):
                if polygon.get_bounding_rect().collidepoint(mouse_pos):
                    if self.selected_polygon:
                        self.selected_polygon.selected = False

                    polygon.selected = True
                    self.selected_polygon = polygon
                    break

    def draw_menu(self):
        if not self.show_menu:
            return

        menu_items = [
            "M - Показать/скрыть меню",
            "N - Создать новую фигуру",
            "TAB - Выбрать следующую фигуру",
            "DELETE - Удалить выбранную фигуру",
            "",
            "R - Поворот по часовой (+5°)",
            "Shift+R - Поворот против часовой (-5°)",
            "Стрелки - Перенос фигуры",
            "",
            "ЛКМ - Выбрать фигуру",
        ]

        y_offset = 10
        for item in menu_items:
            text = self.font.render(item, True, BLACK)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25

    def draw_status(self):
        status = f"Фигур на холсте: {len(self.polygons)}"
        if self.selected_polygon:
            status += " | Выбрана фигура"
            
            angle = self.selected_polygon.rotation_angle
            status += f" | Угол: {angle:.1f}°"
            
            if angle == 0 or angle == 360:
                status += " (вправо)"
            elif angle == 90:
                status += " (вверх)"
            elif angle == 180:
                status += " (влево)"
            elif angle == 270:
                status += " (вниз)"
            elif 0 < angle < 90:
                status += " (вправо-вверх)"
            elif 90 < angle < 180:
                status += " (влево-вверх)"
            elif 180 < angle < 270:
                status += " (влево-вниз)"
            elif 270 < angle < 360:
                status += " (вправо-вниз)"

        text = self.font.render(status, True, BLACK)
        self.screen.blit(text, (10, HEIGHT - 30))

    def run(self):
        running = True
        while running:
            running = self.handle_events()

            self.screen.fill(WHITE)

            for polygon in self.polygons:
                polygon.draw(self.screen)

            self.draw_menu()
            self.draw_status()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = Painter()
    app.run()