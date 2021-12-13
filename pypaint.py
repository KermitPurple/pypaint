#! /usr/bin/env python3

import pygame
import pygame_tools as pgt
import re
from enum import Enum

HEX_DICT = {
    '0': 0,
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

class InputDestination(Enum):
    Color = 0

class PyPaintApp(pgt.GameScreen):
    '''
    A application similar to ms paint
    '''
    def __init__(self):
        pygame.init()
        size = pgt.Point(1400, 750)
        super().__init__(pygame.display.set_mode(size), size, size // 2)
        self.center = self.window_size // 2
        self.selected_color = 'black'
        self.selected_width = 5
        self.prev_pos = None
        self.input_destination = None
        input_height = 60
        self.input_box = pgt.InputBox(
            pygame.Rect(
                self.window_size.x // 10,
                self.center.y - input_height // 2,
                self.window_size.x * 8 // 10,
                input_height,
            ),
            self.parse_color('#333'),
            'white',
            0,
            None,
            pygame.font.Font(pygame.font.get_default_font(), 40),
            True
        )
        self.input_box.done = True
        self.drawing_screen = pygame.Surface(self.window_size)
        self.drawing_screen.fill('white')

    def handle_left_click(self):
        '''
        handle left click input
        '''
        pos = self.get_scaled_mouse_pos()
        if self.prev_pos is not None:
            pygame.draw.line(
                self.drawing_screen,
                self.selected_color,
                pos,
                self.prev_pos,
                self.selected_width
            )
        else:
            rect = pgt.Rect(0, 0, self.selected_width, self.selected_width)
            rect.center = pos
            pygame.draw.rect(
                self.drawing_screen,
                self.selected_color,
                rect
            )
        self.prev_pos = pos

    def key_down(self, event: pygame.event.Event):
        '''
        called when key is pressed
        :event: event of when the key is pressed
        '''
        if not self.input_box.done:
            self.input_box.update(event)
            if self.input_box.done:
                match self.input_destination:
                    case InputDestination.Color:
                        self.set_color(self.input_box.get_value())
                self.input_destination = None
            return
        match event.unicode.lower():
            case 'c':
                self.input_destination = InputDestination.Color
                self.input_box.reset()

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
        self.screen.blit(self.drawing_screen, (0, 0))
        self.input_box.draw(self.screen) # box above drawing screen

def main():
    '''Driver code'''
    PyPaintApp().run()

if __name__ == "__main__":
    main()
