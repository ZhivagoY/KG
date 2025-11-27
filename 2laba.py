import pygame
import math
import sys
from typing import List, Tuple

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 1000, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class CBasePoint:
    """Базовый класс точки с методом преобразования"""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def transform(self, dx: float, dy: float, angle_degrees: float = 0, pivot_x: float = None, pivot_y: float = None):
        """Преобразование точки - перенос и поворот"""
        # Перенос
        self.x += dx
        self.y += dy

        # Поворот если задан угол
        if angle_degrees != 0:
            if pivot_x is None:
                pivot_x = self.x
            if pivot_y is None:
                pivot_y = self.y

            self.rotate(angle_degrees, pivot_x, pivot_y)

    def rotate(self, angle_degrees: float, pivot_x: float, pivot_y: float):
        """Поворот точки вокруг опорной точки"""
        angle_rad = math.radians(angle_degrees)

        # Смещаем точку относительно опорной
        x_rel = self.x - pivot_x
        y_rel = self.y - pivot_y

        # Поворачиваем
        x_rotated = x_rel * math.cos(angle_rad) - y_rel * math.sin(angle_rad)
        y_rotated = x_rel * math.sin(angle_rad) + y_rel * math.cos(angle_rad)

        # Возвращаем обратно
        self.x = x_rotated + pivot_x
        self.y = y_rotated + pivot_y


class Polygon:
    """Класс полигона"""

    def __init__(self, points: List[Tuple[float, float]]):
        self.points = [CBasePoint(x, y) for x, y in points]
        self.color = BLACK
        self.selected = False
        self.fill_color = None  # None означает пустоту внутри

    def draw(self, surface):
        """Рисование полигона"""
        if len(self.points) < 2:
            return

        point_list = [(point.x, point.y) for point in self.points]

        # Рисуем заливку только если указан цвет
        if self.fill_color and len(self.points) > 2:
            pygame.draw.polygon(surface, self.fill_color, point_list, 0)

        # Рисуем контур
        line_color = RED if self.selected else BLACK
        pygame.draw.polygon(surface, line_color, point_list, 2)

        # Рисуем точки вершин
        for point in self.points:
            pygame.draw.circle(surface, BLUE, (int(point.x), int(point.y)), 3)

    def transform_position(self, angle_degrees: float = 0, dx: float = 0, dy: float = 0):
        """Преобразование положения полигона"""
        if not self.points:
            return

        # Используем первую точку как опорную для поворота
        pivot = self.points[0]

        # Применяем преобразование ко всем точкам
        for point in self.points:
            point.transform(dx, dy, angle_degrees, pivot.x, pivot.y)

    def translate(self, dx: float, dy: float):
        """Перенос полигона"""
        self.transform_position(0, dx, dy)

    def rotate(self, angle_degrees: float):
        """Поворот полигона"""
        self.transform_position(angle_degrees, 0, 0)

    def get_bounding_rect(self):
        """Получить ограничивающий прямоугольник для выделения"""
        if not self.points:
            return pygame.Rect(0, 0, 0, 0)

        min_x = min(point.x for point in self.points)
        min_y = min(point.y for point in self.points)
        max_x = max(point.x for point in self.points)
        max_y = max(point.y for point in self.points)

        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)


class GermanCross(Polygon):
    """Немецкий крест (пустой внутри)"""

    def __init__(self, center_x: float, center_y: float, size: float = 100):
        points = self.calculate_points(center_x, center_y, size)
        super().__init__(points)
        self.center_x = center_x
        self.center_y = center_y
        self.size = size
        self.color = BLACK
        self.fill_color = None  # Пустота внутри

    def calculate_points(self, center_x: float, center_y: float, size: float):
        """Вычисление точек для немецкого креста (форма из SVG)"""
        points = []
        
        # Параметры креста (адаптировано из SVG path)
        outer_size = size * 0.5
        inner_size = size * 0.2
        notch_depth = size * 0.15
        
        # Внешний контур креста (двигаемся по часовой стрелке)
        
        # Правый луч
        points.append((center_x + outer_size, center_y - inner_size))
        points.append((center_x + outer_size, center_y + inner_size))
        
        # Нижний правый угол
        points.append((center_x + inner_size, center_y + inner_size))
        points.append((center_x + inner_size, center_y + outer_size))
        
        # Нижний луч
        points.append((center_x - inner_size, center_y + outer_size))
        points.append((center_x - inner_size, center_y + inner_size))
        
        # Нижний левый угол
        points.append((center_x - outer_size, center_y + inner_size))
        points.append((center_x - outer_size, center_y - inner_size))
        
        # Верхний левый угол
        points.append((center_x - inner_size, center_y - inner_size))
        points.append((center_x - inner_size, center_y - outer_size))
        
        # Верхний луч
        points.append((center_x + inner_size, center_y - outer_size))
        points.append((center_x + inner_size, center_y - inner_size))
        
        return points


class Painter:
    """Основной класс программы Painter"""

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Painter - Немецкий крест (пустой)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 16)

        # Список фигур
        self.polygons = []

        # Создаем немецкий крест по умолчанию
        self.create_german_cross()

        # Текущая выбранная фигура
        self.selected_polygon = None

        # Параметры управления
        self.rotation_step = 5  # градусов за нажатие
        self.translation_step = 5  # пикселей за нажатие

        # Флаги меню
        self.show_menu = True

    def create_german_cross(self):
        """Создание немецкого креста"""
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        
        # Создаем немецкий крест
        cross = GermanCross(center_x, center_y, 150)
        self.polygons.append(cross)
        self.selected_polygon = cross

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
        """Обработка клавиатурных событий"""
        # Переключение меню
        if event.key == pygame.K_m:
            self.show_menu = not self.show_menu

        # Создание нового креста
        elif event.key == pygame.K_n:
            import random
            x = random.randint(150, WIDTH - 150)
            y = random.randint(150, HEIGHT - 150)
            size = random.randint(80, 120)
            
            new_cross = GermanCross(x, y, size)
            self.polygons.append(new_cross)
            self.selected_polygon = new_cross

        # Выделение следующей фигуры
        elif event.key == pygame.K_TAB:
            if self.polygons:
                if self.selected_polygon in self.polygons:
                    current_index = self.polygons.index(self.selected_polygon)
                    next_index = (current_index + 1) % len(self.polygons)
                else:
                    next_index = 0
                self.selected_polygon = self.polygons[next_index]

        # Удаление выбранной фигуры
        elif event.key == pygame.K_DELETE:
            if self.selected_polygon in self.polygons:
                self.polygons.remove(self.selected_polygon)
                self.selected_polygon = self.polygons[0] if self.polygons else None

        # Преобразования выбранной фигуры
        if self.selected_polygon:
            # Поворот
            if event.key == pygame.K_r:
                # Проверяем, нажат ли Shift для обратного поворота
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_polygon.rotate(-self.rotation_step)
                else:
                    self.selected_polygon.rotate(self.rotation_step)

            # Перенос
            elif event.key == pygame.K_UP:
                self.selected_polygon.translate(0, -self.translation_step)
            elif event.key == pygame.K_DOWN:
                self.selected_polygon.translate(0, self.translation_step)
            elif event.key == pygame.K_LEFT:
                self.selected_polygon.translate(-self.translation_step, 0)
            elif event.key == pygame.K_RIGHT:
                self.selected_polygon.translate(self.translation_step, 0)

    def handle_mouse_events(self, event):
        """Обработка событий мыши"""
        if event.button == 1:  # Левая кнопка мыши
            mouse_pos = pygame.mouse.get_pos()

            # Снимаем выделение со всех фигур
            for polygon in self.polygons:
                polygon.selected = False

            # Проверяем клик по фигурам (с конца для приоритета верхних)
            for polygon in reversed(self.polygons):
                if polygon.get_bounding_rect().collidepoint(mouse_pos):
                    # Выделяем новую
                    polygon.selected = True
                    self.selected_polygon = polygon
                    break

    def draw_menu(self):
        """Отрисовка меню управления"""
        if not self.show_menu:
            return

        menu_items = [
            "=== PAINTER - НЕМЕЦКИЙ КРЕСТ ===",
            "M - Показать/скрыть меню",
            "N - Создать новый крест",
            "TAB - Выбрать следующую фигуру", 
            "DELETE - Удалить выбранную фигуру",
            "",
            "=== ПРЕОБРАЗОВАНИЯ ===",
            "R - Поворот по часовой (+5°)",
            "Shift+R - Поворот против часовой (-5°)",
            "Стрелки - Перенос фигуры",
            "",
            "=== МЫШЬ ===",
            "ЛКМ - Выбрать фигуру"
        ]

        y_offset = 10
        for item in menu_items:
            text = self.font.render(item, True, BLACK)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25

    def draw_status(self):
        """Отрисовка статусной строки"""
        status = f"Крестов на холсте: {len(self.polygons)}"
        if self.selected_polygon:
            status += " | Выбран немецкий крест (пустой)"

        text = self.font.render(status, True, BLACK)
        self.screen.blit(text, (10, HEIGHT - 30))

    def run(self):
        """Основной цикл программы"""
        running = True
        while running:
            running = self.handle_events()

            # Очистка экрана
            self.screen.fill(WHITE)

            # Отрисовка всех полигонов
            for polygon in self.polygons:
                polygon.draw(self.screen)

            # Отрисовка меню и статуса
            self.draw_menu()
            self.draw_status()

            # Обновление экрана
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = Painter()
    app.run()