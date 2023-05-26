from random import randint
import pygame


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.Make_Field()
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.move = False

    def Make_Field(self):
        self.field = [[' '] * (self.height + 2) for i in range(self.width + 2)]
        self.field[0] = ['+'] * (self.height + 2)
        for i in range(self.width):
            self.field[i + 1][0] = '+'
            self.field[i + 1][self.height + 1] = '+'
        self.field[self.width + 1] = ['+'] * (self.height + 2)

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        color = pygame.Color('white')
        filcolor = pygame.Color('green')
        minecolor = pygame.Color('red')
        for col in range(self.width):
            for row in range(self.height):
                if self.field[col + 1][row + 1] == 'checked':
                    font = pygame.font.Font(None, 30)
                    text = font.render('0', True, filcolor)
                    screen.blit(text, (self.left + col * self.cell_size,
                                       self.top + row * self.cell_size,
                                       self.cell_size, self.cell_size))
                elif self.field[col + 1][row + 1] == 'mine':
                    pygame.draw.rect(screen, minecolor, (self.left + col * self.cell_size,
                                                     self.top + row * self.cell_size,
                                                     self.cell_size, self.cell_size))
                else:
                    font = pygame.font.Font(None, 30)
                    text = font.render(self.field[col + 1][row + 1], True, filcolor)
                    screen.blit(text, (self.left + col * self.cell_size,
                                        self.top + row * self.cell_size,
                                        self.cell_size, self.cell_size))
                pygame.draw.rect(screen, color, (self.left + col * self.cell_size,
                                                 self.top + row * self.cell_size,
                                                 self.cell_size, self.cell_size), 1)



class Saper(Board):
    def setmines(self, cell):
        self.mines = [(randint(1, self.width), randint(1, self.height)) for i in range(15)]
        while cell in self.mines:
            self.mines = [(randint(1, self.width), randint(1, self.height)) for i in range(15)]
        print(self.mines)

    def flag(self, x, y):
        if self.field[x][y] == 'F':
            self.field[x][y] = '?'
        elif self.field[x][y] == ' ':
            self.field[x][y] = 'F'
        elif self.field[x][y] == '?':
            self.field[x][y] = ' '

    def open(self, x, y):
        if self.field[x][y] in ('F', '?'):
            pass
        elif (x, y) in self.mines:
            for i in self.mines:
                self.field[i[0]][i[1]] = 'mine'
        else:
            neibours = self.check(x, y)[:]
            if len(neibours) == 9:
                self.field[x][y] = 'checked'
                for neibour in neibours:
                    if 0 < neibour[0] <= self.width and 0 < neibour[1] <= self.height\
                            and self.field[neibour[0]][neibour[1]] != 'checked':
                        self.open(neibour[0], neibour[1])
            else:
                self.field[x][y] = f'{9 - len(neibours)}'

    def check(self, x, y):
        neibours = []
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if (i, j) not in self.mines:
                    neibours.append((i, j))
        return neibours

    def get_click(self, mouse):
        cell = self.get_cell(mouse.pos)
        if mouse.button == 1:
            if self.first:
                self.setmines(cell)
                self.first = False
            self.open(*cell)
        if mouse.button == 3:
            self.flag(*cell)

    def get_cell(self, mouse_pos):
        if self.left <= mouse_pos[0] <= self.left + self.width * self.cell_size and self.top <= mouse_pos[1] <= self.top + self.height * self.cell_size:
            return (mouse_pos[0] - self.left) // self.cell_size + 1, (mouse_pos[1] - self.top) // self.cell_size + 1

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Saper')
    size = (550, 460)
    screen = pygame.display.set_mode(size)
    board = Saper(18, 15)
    board.set_view(5, 5, 30)
    board.first = True
    running = True
    MYEVENTTYPE = pygame.USEREVENT + 1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event)
        screen.fill((0, 0, 0))
        board.render(screen)
        pygame.display.flip()