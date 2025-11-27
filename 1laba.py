import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


class DrawingWidget(QWidget):     # Виджет для рисования.
    def __init__(self):
        super().__init__()
        self.click_positions = []     # Список для хранения позиций кликов мыши.
        self.setMinimumSize(800, 600)    # Установка минимального размера виджета.

    def mousePressEvent(self, event):    # Обработчик события нажатия кнопки мыши.
        if event.button() == Qt.MouseButton.LeftButton:    # Проверка, что нажата левая кнопка мыши.
            self.click_positions.append(event.pos())      # # Добавление позиции клика в список
            self.update()

    def paintEvent(self, event):    # Обработчик события перерисовки виджета.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)   # Включение сглаживания

        for pos in self.click_positions:
            # Размеры фигур
            outer_size = 150  # Сторона внешнего квадрата
            circle_diameter = outer_size  # Диаметр окружности равен стороне квадрата
            
            # Диагональ внутреннего квадрата равна диаметру окружности
            # Для квадрата: диагональ = сторона * √2 ≈ сторона * 1.414
            inner_size = int(circle_diameter / 1.414)  # Сторона внутреннего квадрата
            
            # Рисуем внешний синий квадрат
            painter.setPen(QPen(QColor(0, 0, 255), 2))
            painter.setBrush(QBrush(QColor(0, 0, 255)))
            painter.drawRect(
                int(pos.x() - outer_size/2), 
                int(pos.y() - outer_size/2), 
                outer_size, 
                outer_size
            )
            
            # Рисуем белую окружность (диаметр = стороне внешнего квадрата)
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(
                int(pos.x() - circle_diameter/2), 
                int(pos.y() - circle_diameter/2), 
                circle_diameter, 
                circle_diameter
            )
            
            # Рисуем внутренний синий квадрат (диагональ = диаметру окружности)
            painter.setPen(QPen(QColor(0, 0, 255), 2))
            painter.setBrush(QBrush(QColor(0, 0, 255)))
            painter.drawRect(
                int(pos.x() - inner_size/2), 
                int(pos.y() - inner_size/2), 
                inner_size, 
                inner_size
            )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Рисование фигур")
        self.setGeometry(100, 100, 800, 600)
        self.drawing_widget = DrawingWidget()
        self.setCentralWidget(self.drawing_widget)


def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        print("Приложение запущено успешно! Кликайте левой кнопкой мыши для рисования.")
        return app.exec()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())