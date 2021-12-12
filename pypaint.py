#! /usr/bin/env python3

import pygame
import pygame_tools as pgt
import re

HEX_DICT = {
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'a': 10,
    'b': 11,
    'c': 12,
    'd': 13,
    'e': 14,
    'f': 15
}

def convert_hex(r1: str, r2: str, g1: str, g2: str, b1: str, b2: str) -> pygame.Color:
    return pygame.Color(
        15 * HEX_DICT[r1] + HEX_DICT[r2],
        15 * HEX_DICT[g1] + HEX_DICT[g2],
        15 * HEX_DICT[b1] + HEX_DICT[b2]
    )

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
        '''
        handle left click input
        '''
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

    def set_color(self, color: str) -> bool:
        '''
        set the current color
        :color: a string representing a color
        '''
        try:
            self.selected_color = self.parse_color(color)
        except ValueError as e:
            return False
        return True

    def parse_color(self, color: str) -> pygame.Color:
        '''
        parse a color string
        :color: a string representing a color
        '''
        if color in pygame.colordict.THECOLORS:
            return pygame.Color(color)
        match list(color.lower()):
            case ['#', r1, r2, g1, g2, b1, b2] | [r1, r2, g1, g2 ,b1, b2]:
                return convert_hex(r1, r2, g1, g2, b1, b2)
            case ['#', r, g, b] | [r, g, b]:
                return convert_hex(r, r, g, g, b, b)
        match list(filter(lambda x: x, re.split(' |\(|\)|,', color.lower()))):
            case ['rgb', r, g, b] | [r, g, b]:
                return pygame.Color(
                    int(r),
                    int(g),
                    int(b),
                    )
        raise ValueError('Invalid Color')

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
