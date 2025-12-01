import pygame
import math
import sys
import os
from typing import List, Tuple, Optional

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 1000, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)


class BitmapResource:
    """Класс для работы с растровыми ресурсами"""

    def __init__(self, filename: str = None):
        self.image = None
        self.original_image = None
        self.filename = filename
        self.loaded = False

        if filename and os.path.exists(filename):
            self.load_from_file(filename)

    def load_from_file(self, filename: str):
        """Загрузка изображения из файла"""
        try:
            self.image = pygame.image.load(filename).convert_alpha()
            self.original_image = self.image.copy()
            self.filename = filename
            self.loaded = True
            print(f"Изображение загружено: {filename}")
        except pygame.error as e:
            print(f"Ошибка загрузки изображения: {e}")
            self.loaded = False

    def draw(self, surface, x: int, y: int, width: int = None, height: int = None):
        """Вывод изображения на экран с возможным масштабированием"""
        if not self.loaded:
            return

        if width is not None and height is not None:
            # Масштабирование изображения
            scaled_image = pygame.transform.scale(self.image, (width, height))
            surface.blit(scaled_image, (x, y))
        else:
            # Вывод в оригинальном размере
            surface.blit(self.image, (x, y))

    def scale(self, width: int, height: int):
        """Масштабирование изображения"""
        if self.loaded and self.original_image:
            self.image = pygame.transform.scale(self.original_image, (width, height))

    def get_width(self) -> int:
        """Получить ширину изображения"""
        return self.image.get_width() if self.loaded else 0

    def get_height(self) -> int:
        """Получить высоту изображения"""
        return self.image.get_height() if self.loaded else 0

    def create_pattern_surface(self, pattern_width: int, pattern_height: int) -> pygame.Surface:
        """Создание поверхности с повторяющимся узором"""
        if not self.loaded:
            return pygame.Surface((pattern_width, pattern_height))

        # Создаем поверхность для узора
        pattern_surface = pygame.Surface((pattern_width, pattern_height), pygame.SRCALPHA)

        # Заполняем поверхность повторяющимся изображением
        img_width = self.get_width()
        img_height = self.get_height()

        for x in range(0, pattern_width, img_width):
            for y in range(0, pattern_height, img_height):
                pattern_surface.blit(self.image, (x, y))

        return pattern_surface


class PatternBrush:
    """Класс кисти на основе растрового шаблона"""

    def __init__(self, pattern_bitmap: BitmapResource):
        self.pattern = pattern_bitmap
        self.brush_size = 32

    def fill_shape(self, surface, shape_points: List[Tuple[int, int]]):
        """Заполнение фигуры шаблонной кистью"""
        if not self.pattern.loaded or len(shape_points) < 3:
            return False

        # Создаем маску для фигуры
        mask_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 0))

        # Рисуем фигуру на маске
        pygame.draw.polygon(mask_surface, (255, 255, 255, 255), shape_points)

        # Создаем поверхность с узором
        pattern_surface = self.pattern.create_pattern_surface(WIDTH, HEIGHT)

        # Применяем маску к узору
        pattern_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Рисуем результат на основной поверхности
        surface.blit(pattern_surface, (0, 0))

        return True


class Shape:
    """Базовый класс фигуры"""

    def __init__(self, points: List[Tuple[int, int]]):
        self.points = points
        self.color = BLACK
        self.filled = False
        self.pattern_filled = False
        self.pattern_texture = None  # Для хранения текстуры заливки
        self.pattern_surface = None  # Для хранения поверхности с узором

    def draw(self, surface):
        """Рисование фигуры"""
        if len(self.points) < 2:
            return

        # Если фигура заполнена узором, рисуем текстуру
        if self.pattern_filled and self.pattern_surface:
            surface.blit(self.pattern_surface, (0, 0))

        # Иначе рисуем обычную заливку
        elif self.filled and len(self.points) > 2:
            pygame.draw.polygon(surface, self.color, self.points)

        # Рисуем контур
        pygame.draw.polygon(surface, BLACK, self.points, 2)

        # Рисуем точки вершин
        for point in self.points:
            pygame.draw.circle(surface, BLUE, point, 3)

    def fill_with_pattern(self, pattern_bitmap: BitmapResource):
        """Заполнение фигуры узором"""
        if not pattern_bitmap.loaded:
            return False

        self.pattern_filled = True
        self.pattern_texture = pattern_bitmap

        # Создаем поверхность для узора
        self.pattern_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.pattern_surface.fill((0, 0, 0, 0))

        # Создаем маску для фигуры
        mask_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 0))
        pygame.draw.polygon(mask_surface, (255, 255, 255, 255), self.points)

        # Создаем поверхность с узором
        pattern_texture_surface = pattern_bitmap.create_pattern_surface(WIDTH, HEIGHT)

        # Применяем маску к узору
        pattern_texture_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Сохраняем результат
        self.pattern_surface.blit(pattern_texture_surface, (0, 0))

        return True

    def clear_pattern(self):
        """Очистка узорной заливки"""
        self.pattern_filled = False
        self.pattern_texture = None
        self.pattern_surface = None

    def get_bounding_rect(self) -> pygame.Rect:
        """Получить ограничивающий прямоугольник"""
        if not self.points:
            return pygame.Rect(0, 0, 0, 0)

        min_x = min(point[0] for point in self.points)
        min_y = min(point[1] for point in self.points)
        max_x = max(point[0] for point in self.points)
        max_y = max(point[1] for point in self.points)

        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)


class Rectangle(Shape):
    """Класс прямоугольника"""

    def __init__(self, x: int, y: int, width: int, height: int):
        points = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height)
        ]
        super().__init__(points)


class Circle(Shape):
    """Класс круга (аппроксимированный полигоном)"""

    def __init__(self, center_x: int, center_y: int, radius: int, segments: int = 32):
        points = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((int(x), int(y)))
        super().__init__(points)


class Star(Shape):
    """Класс звезды"""

    def __init__(self, center_x: int, center_y: int, outer_radius: int, inner_radius: int, points_count: int = 5):
        star_points = []
        for i in range(points_count * 2):
            angle = math.pi * i / points_count
            if i % 2 == 0:
                radius = outer_radius
            else:
                radius = inner_radius

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            star_points.append((int(x), int(y)))
        super().__init__(star_points)


class Painter:
    """Основной класс программы Painter"""

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Painter - Растровые ресурсы и кисти")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 16)

        # Растровые ресурсы
        self.bitmaps = []
        self.load_default_bitmaps()

        # Кисти
        self.pattern_brush = PatternBrush(self.bitmaps[0] if self.bitmaps else BitmapResource())

        # Фигуры
        self.shapes = []
        self.create_default_shapes()

        # Текущая выбранная фигура
        self.selected_shape = None

        # Режимы работы
        self.mode = "view"  # "view", "create_shape", "fill_pattern"
        self.creating_shape = False
        self.current_points = []

        # Флаги меню
        self.show_menu = True

    def load_default_bitmaps(self):
        """Загрузка растровых ресурсов по умолчанию"""
        # Пытаемся загрузить изображения из файлов
        test_files = ["texture.png", "pattern.png", "brush.png"]

        for filename in test_files:
            if os.path.exists(filename):
                bitmap = BitmapResource(filename)
                if bitmap.loaded:
                    self.bitmaps.append(bitmap)

        # Если файлы не найдены, создаем программные текстуры
        if not self.bitmaps:
            print("Создание программных текстур...")
            self.create_programmatic_bitmaps()

    def create_programmatic_bitmaps(self):
        """Создание растровых ресурсов программно"""
        # Текстура 1: Круг
        circle_size = 16
        circle_surface = pygame.Surface((circle_size, circle_size), pygame.SRCALPHA)
        circle_surface.fill((0, 0, 0, 0))
        pygame.draw.circle(circle_surface, (200, 0, 0), (circle_size // 2, circle_size // 2), circle_size // 2, 2)

        pygame.image.save(circle_surface, "circle_pattern.png")
        self.bitmaps.append(BitmapResource("circle_pattern.png"))

        # Текстура 2: Треугольник
        triangle_size = 16
        triangle_surface = pygame.Surface((triangle_size, triangle_size), pygame.SRCALPHA)
        triangle_surface.fill((0, 0, 0, 0))
        pygame.draw.polygon(triangle_surface, (200, 0, 0), [(0, 0), (triangle_size, 0), (triangle_size // 2, triangle_size)], 2)

        pygame.image.save(triangle_surface, "triangle_pattern.png")
        self.bitmaps.append(BitmapResource("triangle_pattern.png"))

        # Текстура 3: Квадрат
        square_size = 16
        square_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        square_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(square_surface, (200, 0, 0), (0, 0, square_size, square_size), 2)

        pygame.image.save(square_surface, "square_pattern.png")
        self.bitmaps.append(BitmapResource("square_pattern.png"))
    def create_default_shapes(self):
        """Создание фигур по умолчанию"""
        # Прямоугольник
        rect = Rectangle(100, 100, 200, 150)
        rect.color = (200, 200, 255)
        self.shapes.append(rect)

        # Круг
        circle = Circle(400, 300, 80)
        circle.color = (255, 200, 200)
        self.shapes.append(circle)

        # Звезда
        star = Star(600, 200, 70, 30, 7)
        star.color = (200, 255, 200)
        self.shapes.append(star)

        self.selected_shape = self.shapes[0]

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

        # Создание фигур
        elif event.key == pygame.K_c:
            self.mode = "create_shape"
            self.creating_shape = True
            self.current_points = []

        # Завершение создания фигуры
        elif event.key == pygame.K_RETURN and self.creating_shape:
            if len(self.current_points) >= 3:
                new_shape = Shape(self.current_points.copy())
                new_shape.color = (150, 150, 255)
                self.shapes.append(new_shape)
                self.selected_shape = new_shape
            self.creating_shape = False
            self.mode = "view"

        # Отмена создания фигуры
        elif event.key == pygame.K_ESCAPE and self.creating_shape:
            self.creating_shape = False
            self.mode = "view"
            self.current_points = []

        # Заполнение фигуры узором
        elif event.key == pygame.K_f and self.selected_shape and self.bitmaps:
            # Используем текущую текстуру из pattern_brush
            if self.pattern_brush.pattern and self.pattern_brush.pattern.loaded:
                self.selected_shape.fill_with_pattern(self.pattern_brush.pattern)

        # Очистка узора фигуры
        elif event.key == pygame.K_x and self.selected_shape:
            self.selected_shape.clear_pattern()

        # Обычная заливка фигуры
        elif event.key == pygame.K_b and self.selected_shape:
            self.selected_shape.filled = not self.selected_shape.filled
            self.selected_shape.clear_pattern()  # Убираем узор при обычной заливке

        # Выбор следующей фигуры
        elif event.key == pygame.K_TAB:
            if self.shapes:
                if self.selected_shape in self.shapes:
                    current_index = self.shapes.index(self.selected_shape)
                    next_index = (current_index + 1) % len(self.shapes)
                else:
                    next_index = 0
                self.selected_shape = self.shapes[next_index]

        # Выбор следующей текстуры для кисти
        elif event.key == pygame.K_t and self.bitmaps:
            if self.pattern_brush.pattern in self.bitmaps:
                current_index = self.bitmaps.index(self.pattern_brush.pattern)
                next_index = (current_index + 1) % len(self.bitmaps)
            else:
                next_index = 0
            self.pattern_brush.pattern = self.bitmaps[next_index]

    def handle_mouse_events(self, event):
        """Обработка событий мыши"""
        mouse_pos = pygame.mouse.get_pos()

        if event.button == 1:  # Левая кнопка мыши
            if self.mode == "create_shape" and self.creating_shape:
                # Добавляем точку к создаваемой фигуре
                self.current_points.append(mouse_pos)
            else:
                # Выбор фигуры
                for shape in reversed(self.shapes):
                    if shape.get_bounding_rect().collidepoint(mouse_pos):
                        self.selected_shape = shape
                        break

        elif event.button == 3:  # Правая кнопка мыши
            # Удаление последней точки при создании фигуры
            if self.creating_shape and self.current_points:
                self.current_points.pop()

    def draw_menu(self):
        """Отрисовка меню управления"""
        if not self.show_menu:
            return

        menu_items = [
            "=== PAINTER - РАСТРОВЫЕ РЕСУРСЫ И КИСТИ ===",
            "M - Показать/скрыть меню",
            "",
            "=== РЕЖИМЫ ===",
            "C - Начать создание фигуры (клик - добавить точку, ПКМ - удалить)",
            "ENTER - Завершить создание фигуры",
            "ESC - Отмена создания фигуры",
            "",
            "=== ОПЕРАЦИИ С ФИГУРАМИ ===",
            "F - Заполнить выбранную фигуру узором",
            "B - Включить/выключить обычную заливку",
            "X - Очистить узор фигуры",
            "TAB - Выбрать следующую фигуру",
            "",
            "=== УПРАВЛЕНИЕ ТЕКСТУРАМИ ===",
            "T - Сменить текстуру кисти",
            "",
            "=== ИНФОРМАЦИЯ ===",
            f"Текстур загружено: {len(self.bitmaps)}",
            f"Фигур на сцене: {len(self.shapes)}",
            f"Режим: {'Создание фигуры' if self.creating_shape else 'Просмотр'}"
        ]

        y_offset = 10
        for item in menu_items:
            text = self.font.render(item, True, BLACK)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25

    def draw_status(self):
        """Отрисовка статусной строки"""
        status = f"Фигур: {len(self.shapes)}"
        if self.selected_shape:
            status += f" | Выбрана фигура с {len(self.selected_shape.points)} точками"
            if self.selected_shape.filled:
                status += " | Обычная заливка"
            if self.selected_shape.pattern_filled:
                status += " | Узорная заливка"
        if self.creating_shape:
            status += f" | Создание: {len(self.current_points)} точек"

        text = self.font.render(status, True, BLACK)
        self.screen.blit(text, (10, HEIGHT - 30))

    def draw_bitmap_previews(self):
        """Отрисовка превью растровых ресурсов"""
        if not self.bitmaps:
            return

        x_offset = WIDTH - 150
        y_offset = 10

        title = self.font.render("Текстуры кистей:", True, BLACK)
        self.screen.blit(title, (x_offset, y_offset))
        y_offset += 25

        for i, bitmap in enumerate(self.bitmaps):
            # Рамка для активной текстуры
            if bitmap == self.pattern_brush.pattern:
                pygame.draw.rect(self.screen, RED, (x_offset - 2, y_offset - 2, 54, 54), 2)

            # Превью текстуры
            bitmap.draw(self.screen, x_offset, y_offset, 50, 50)

            # Номер текстуры
            text = self.font.render(str(i + 1), True, BLACK)
            self.screen.blit(text, (x_offset + 55, y_offset + 20))

            y_offset += 60

    def run(self):
        """Основной цикл программы"""
        running = True
        while running:
            running = self.handle_events()

            # Очистка экрана
            self.screen.fill(WHITE)

            # Отрисовка всех фигур
            for shape in self.shapes:
                shape.draw(self.screen)

                # Подсветка выбранной фигуры
                if shape == self.selected_shape:
                    bounding_rect = shape.get_bounding_rect()
                    pygame.draw.rect(self.screen, RED, bounding_rect, 2)

            # Отрисовка создаваемой фигуры
            if self.creating_shape and len(self.current_points) >= 2:
                if len(self.current_points) == 2:
                    pygame.draw.line(self.screen, GREEN, self.current_points[0], self.current_points[1], 2)
                else:
                    pygame.draw.polygon(self.screen, (200, 200, 200), self.current_points, 0)
                    pygame.draw.polygon(self.screen, GREEN, self.current_points, 2)

                # Рисуем точки
                for point in self.current_points:
                    pygame.draw.circle(self.screen, BLUE, point, 4)

            # Отрисовка превью текстур
            self.draw_bitmap_previews()

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