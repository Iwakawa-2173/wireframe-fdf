import pygame
from pygame.locals import (
    DOUBLEBUF, OPENGL,
    MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT
)
from OpenGL.GL import (
    glBegin, glClear, glColor3f, glEnd, glLoadIdentity, glRotatef,
    glTranslatef, glVertex3f, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_LINE_STRIP, glScalef
)
from OpenGL.GLU import gluPerspective
from PIL import Image
import numpy as np


def image_to_height_map_with_scale(
    image_path, scale_width, scale_height, max_height=2
):
    img = Image.open(image_path).convert("L").resize(
        (scale_width, scale_height), Image.LANCZOS
    )
    img_array = np.array(img)
    height_map = (255 - img_array) / 255 * max_height
    height_map_int = np.rint(height_map).astype(int)
    return height_map_int


def save_height_map_to_txt(height_map, filename):
    np.savetxt(filename, height_map, fmt="%d", delimiter=" ")


def load_height_map(filename):
    height_map = []
    try:
        with open(filename, "r") as file:
            line = file.readline()
            while line:
                row = [float(value) for value in line.strip().split()]
                height_map.append(row)
                line = file.readline()
    except Exception as exc:
        print(f"Ошибка при чтении файла {filename}: {exc}")
    return height_map


def interpolate_maps(map1, map2, alpha):
    rows = len(map1)
    cols = len(map1[0])
    result = []
    y = 0
    while y < rows:
        row = []
        x = 0
        while x < cols:
            val = map1[y][x] + (map2[y][x] - map1[y][x]) * alpha
            row.append(val)
            x += 1
        result.append(row)
        y += 1
    return result


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

    height_map_result = image_to_height_map_with_scale(
        "buddha.jpg", 100, 100, max_height=2
    )
    save_height_map_to_txt(height_map_result, "height_map.txt")

    height_map_result = image_to_height_map_with_scale(
        "lotos.jpg", 100, 100, max_height=2
    )
    save_height_map_to_txt(height_map_result, "height_map2.txt")

    height_map1 = load_height_map("height_map.txt")
    height_map2 = load_height_map("height_map2.txt")

    if not height_map1 or not height_map2:
        print("Ошибка: один из файлов height_map отсутствует или пуст.")
        return

    if (len(height_map1) != len(height_map2) or
            len(height_map1[0]) != len(height_map2[0])):
        print("Ошибка: размеры height_map не совпадают.")
        return

    rot_x, rot_y = 25, 0
    mouse_sensitivity = 0.3
    dragging = False
    zoom = -15
    alpha = 0.0
    alpha_step = 0.01
    alpha_direction = 1  # 1 - увеличиваем alpha, -1 - уменьшаем

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
                if event.button == 1:
                    pygame.event.set_grab(True)
                    pygame.mouse.set_visible(False)
                    dragging = True
                    pygame.mouse.get_rel()
                elif event.button == 4:
                    zoom += 1.0
                elif event.button == 5:
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

        # Интерполируем height_map для текущего alpha
        current_map = interpolate_maps(height_map1, height_map2, alpha)
        alpha += alpha_step * alpha_direction
        if alpha >= 1.0:
            alpha = 1.0
            alpha_direction = -1  # Начинаем уменьшать alpha
        elif alpha <= 0.0:
            alpha = 0.0
            alpha_direction = 1  # Начинаем увеличивать alpha

        glLoadIdentity()
        glScalef(1, -1, 1)
        gluPerspective(45, display[0] / display[1], 0.1, 2050.0)
        glTranslatef(-2, -2, zoom)
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_wireframe(current_map)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
