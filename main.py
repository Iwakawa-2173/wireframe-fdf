import pygame
from pygame.locals import (
    DOUBLEBUF, OPENGL,
    MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT
)
from OpenGL.GL import (
    glBegin, glClear, glColor3f, glEnd, glLoadIdentity, glRotatef,
    glTranslatef, glVertex3f, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_LINE_STRIP
)
from OpenGL.GLU import gluPerspective


def load_height_map(filename):
    height_map = []
    try:
        with open(filename, "r") as file:
            line = file.readline()
            while line:
                row = [int(value) for value in line.strip().split()]
                height_map.append(row)
                line = file.readline()
    except Exception as exc:
        print(f"Ошибка при чтении файла {filename}: {exc}")
    return height_map


def draw_wireframe(grid):
    rows = len(grid)
    if rows == 0:
        return
    cols = len(grid[0])
    glColor3f(1, 1, 1)  # Белый цвет для линий

    y = 0
    while y < rows:
        glBegin(GL_LINE_STRIP)
        x = 0
        while x < cols:
            glVertex3f(x, y, grid[y][x])
            x += 1
        glEnd()
        y += 1

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
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    height_map = load_height_map("height_map.txt")
    if not height_map:
        height_map = [
            [0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 2, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0],
        ]

    rot_x, rot_y = 25, 0
    mouse_sensitivity = 0.3
    dragging = False
    zoom = -15  # Начальное значение z камеры

    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)

    clock = pygame.time.Clock()

    running = True
    while running:
        events = pygame.event.get()
        i = 0
        while i < len(events):
            event = events[i]
            i += 1

            if event.type == QUIT:
                running = False

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    pygame.event.set_grab(True)
                    pygame.mouse.set_visible(False)
                    dragging = True
                    pygame.mouse.get_rel()
                elif event.button == 4:  # Колёсико вперед (приближение)
                    zoom += 1.0
                elif event.button == 5:  # Колёсико назад (отдаление)
                    zoom -= 1.0

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
                dragging = False

        if dragging:
            dx, dy = pygame.mouse.get_rel()
            rot_x += dy * mouse_sensitivity
            rot_y += dx * mouse_sensitivity
        else:
            pygame.mouse.get_rel()

        glLoadIdentity()
        gluPerspective(45, display[0] / display[1], 0.1, 50.0)
        glTranslatef(-2, -2, zoom)
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_wireframe(height_map)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
