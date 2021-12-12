#! /usr/bin/env python3

import pygame
import pygame_tools as pgt

class PyPaintApp(pgt.GameScreen):
    '''
    A application similar to ms paint
    '''
    def __init__(self):
        pygame.init()
        size = pgt.Point(1400, 750)
        super().__init__(pygame.display.set_mode(size), size, size // 2)
        self.selected_color = 'black'
        self.selected_width = 5
        self.prev_pos = None
        self.screen.fill('white')

    def handle_left_click(self):
        pos = self.get_scaled_mouse_pos()
        if self.prev_pos is not None:
            pygame.draw.line(
                self.screen,
                self.selected_color,
                pos,
                self.prev_pos,
                self.selected_width
            )
        else:
            rect = pgt.Rect(0, 0, self.selected_width, self.selected_width)
            rect.center = pos
            pygame.draw.rect(
                self.screen,
                self.selected_color,
                rect
            )
        self.prev_pos = pos

    def update(self):
        if pygame.mouse.get_pressed()[0]: # left click pressed
            self.handle_left_click()
        else:
            self.prev_pos = None

def main():
    '''Driver code'''
    PyPaintApp().run()

if __name__ == "__main__":
    main()
