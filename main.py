import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Данные высот для wireframe модели (эмуляция содержимого fdf)
height_map = [
    [0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 2, 0, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0],
]

def draw_wireframe(grid):
    rows = len(grid)
    cols = len(grid[0])
    glColor3f(1, 1, 1)  # Белый цвет для линий

    # Рисуем линии в направлении оси X, используя while вместо for
    y = 0
    while y < rows:
        glBegin(GL_LINE_STRIP)
        x = 0
        while x < cols:
            glVertex3f(x, y, grid[y][x])  # Добавляем точку с высотой z=grid[y][x]
            x += 1
        glEnd()
        y += 1

    # Рисуем линии в направлении оси Y, используя while вместо for
    x = 0
    while x < cols:
        glBegin(GL_LINE_STRIP)
        y = 0
        while y < rows:
            glVertex3f(x, y, grid[y][x])
            y += 1
        glEnd()
        x += 1

def main():
    pygame.init()
    display = (800, 600)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Настройка перспективы и начального положения камеры
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(-2, -2, -15)

    rot_x, rot_y = 25, 0              # Начальные углы вращения по осям X и Y
    mouse_sensitivity = 0.3           # Чувствительность мыши
    dragging = False                  # Флаг, удерживается ли левая кнопка мыши

    pygame.mouse.set_visible(True)    # Мышь видима по умолчанию
    pygame.event.set_grab(False)      # Мышь не захвачена по умолчанию

    clock = pygame.time.Clock()

    running = True
    while running:
        # Получаем все события в списке
        events = pygame.event.get()
        i = 0
        # Обрабатываем события циклом while
        while i < len(events):
            event = events[i]
            i += 1

            if event.type == pygame.QUIT:  # Закрытие окна
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Нажата левая кнопка - захватываем мышь
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
                dragging = True
                pygame.mouse.get_rel()  # Сброс смещения мыши

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Отпущена левая кнопка - освобождаем мышь
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
                dragging = False

        if dragging:
            # Получаем смещение мыши с последнего кадра
            dx, dy = pygame.mouse.get_rel()
            # Изменяем углы вращения пропорционально смещению мыши
            rot_x += dy * mouse_sensitivity
            rot_y += dx * mouse_sensitivity
        else:
            pygame.mouse.get_rel()  # Сброс смещения при отсутствии захвата мыши

        # Сброс трансформаций модели
        glLoadIdentity()
        # Настройка камеры и трансформаций вращения
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(-2, -2, -15)
        glRotatef(rot_x, 1, 0, 0)  # Вращение по X
        glRotatef(rot_y, 0, 1, 0)  # Вращение по Y

        # Очистка экрана и отрисовка каркасной модели
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_wireframe(height_map)

        pygame.display.flip()  # Обновление дисплея
        clock.tick(60)         # Ограничение до 60 кадров в секунду

    pygame.quit()

if __name__ == "__main__":
    main()
