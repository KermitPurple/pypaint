#! /usr/bin/env python3

import pygame_tools as pgt
import pygame
import math
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
        16 * HEX_DICT[r1] + HEX_DICT[r2],
        16 * HEX_DICT[g1] + HEX_DICT[g2],
        16 * HEX_DICT[b1] + HEX_DICT[b2]
    )

def smooth_line(
    screen: pygame.Surface,
    color: pygame.Color,
    start_pos: pgt.Point,
    end_pos: pgt.Point,
    density: int,
    width: int = 1,
    ):
    distance = pgt.Point.distance(start_pos, end_pos)
    scale = distance / density
    theta = math.atan2(end_pos.y - start_pos.y, end_pos.x - start_pos.x)
    i = 0
    while i < distance:
        rect = pygame.Rect(0, 0, width, width)
        rect.center = start_pos + i * pgt.Point(math.cos(theta), math.sin(theta))
        pygame.draw.rect(
            screen,
            color,
            rect
        )
        i += scale

def parse_color(color: str) -> pygame.Color:
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

class InputDestination(Enum):
    Color = 0
    BrushWidth = 1
    SaveFile = 2
    LoadFile = 3

INPUT_TITLE_DICT = {
    InputDestination.Color: 'Enter a brush color',
    InputDestination.BrushWidth: 'Enter a brush width',
    InputDestination.SaveFile: 'Enter filename to save to',
    InputDestination.LoadFile: 'Enter filename to load from',
}

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
            parse_color('#333'),
            'white',
            0,
            None,
            pygame.font.Font(pygame.font.get_default_font(), 40),
            True
        )
        title_height = 15
        self.title_box = pgt.TextBox(
            [''],
            pygame.Rect(
                self.window_size.x // 10,
                self.input_box.rect.y - title_height,
                self.window_size.x * 8 // 10,
                title_height,
            ),
            parse_color('#222'),
            'white',
            0,
            pgt.Point(0, 0),
            pygame.font.Font(pygame.font.get_default_font(), title_height),
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
            smooth_line(
                self.drawing_screen,
                self.selected_color,
                pos,
                self.prev_pos,
                100,
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
                    case InputDestination.BrushWidth:
                        try:
                            self.selected_width = int(self.input_box.get_value())
                        except: pass
                    case InputDestination.SaveFile:
                        try:
                            pygame.image.save(self.drawing_screen, self.input_box.get_value())
                        except: pass
                    case InputDestination.LoadFile:
                        self.drawing_screen = pygame.image.load(self.input_box.get_value())
                self.input_destination = None
            return
        match event.unicode.lower():
            case ('c' | 'w' | 's' | 'l' ) as val:
                match val:
                    case 'c': # set color
                        self.input_destination = InputDestination.Color
                    case 'w': # set brush width
                        self.input_destination = InputDestination.BrushWidth
                    case 's': # save to file
                        self.input_destination = InputDestination.SaveFile
                    case 'l': # load from file
                        self.input_destination = InputDestination.LoadFile
                self.input_box.reset()
                self.title_box.text[0] = INPUT_TITLE_DICT[self.input_destination]
            case 'f': # fill screen
                self.drawing_screen.fill(self.selected_color)

    def set_color(self, color: str) -> bool:
        '''
        set the current color
        :color: a string representing a color
        '''
        try:
            self.selected_color = parse_color(color)
        except ValueError as e:
            return False
        return True

    def draw_input(self):
        '''
        draw title_box and input_box to screen if input_box is active
        '''
        if self.input_box.done:
            return
        self.input_box.draw(self.screen)
        self.title_box.draw(self.screen)

    def update(self):
        if pygame.mouse.get_pressed()[0]: # left click pressed
            self.handle_left_click()
        else:
            self.prev_pos = None
        self.screen.blit(self.drawing_screen, (0, 0))
        self.draw_input() # draw box above drawing_screen

def main():
    '''Driver code'''
    PyPaintApp().run()

if __name__ == "__main__":
    main()
