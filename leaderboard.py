import hashlib
import math
import threading
import time
from dataclasses import dataclass
from typing import List

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT

from ccc_scraper import CCCScraper
from ccc_table_parser import CCCTableParser

DEV_MODE = True
try:
    with open(".credentials", "r") as f:
        USERNAME, PASSWORD = f.read().split("\n")
except FileNotFoundError:
    raise FileNotFoundError("You must have a .credentials file with the teacher login and password inside.")

JR_NUMBER = 180  # 2022
SR_NUMBER = 181  # 2022

CCC_TOTAL_POINTS = 75
WIDTH = int(2880//2.0)
HEIGHT = int(1920//2.0)

PADDING = 5
FONT_SIZE = 25


try:
    with open(".opt-out", "r") as f:
        OPT_OUTS = [n.strip() for n in f.readlines()]
except FileNotFoundError:
    OPT_OUTS: List[str] = []

pygame.font.init()


class Color:
    WHITE = pygame.Color(255, 255, 255)
    BLACK = pygame.Color(0, 0, 0)
    GREEN = pygame.Color(0, 255, 0)
    MIDNIGHT_BLUE = pygame.Color(25, 25, 112)
    DARK_MIDNIGHT_BLUE = pygame.Color(0, 51, 102)
    DARK_BLUE_GRAY = pygame.Color(102, 102, 153)
    LIGHT_BLUE = pygame.Color(173, 216, 230)
    SILVER_CHALICE = pygame.Color(172, 172, 172)
    ORANGE_PEEL = pygame.Color(255, 159, 0)


@dataclass
class Row:
    rank: int
    name: str
    scores: List[int]
    hovering: bool = False
    font = pygame.font.SysFont('Arial', FONT_SIZE)
    star_font = pygame.font.SysFont("Arial", int(FONT_SIZE * 1.7))

    def draw(self, surface: pygame.Surface, table: "Table", row_num: int):
        parts = self.name.split(" ")
        username = parts.pop()[1:-1]
        display_name = " ".join(parts)
        if username in OPT_OUTS:
            hash = hashlib.md5(display_name.encode()).hexdigest()[:4]
            display_name = "Anonymous " + hash

        data = display_name, str(sum(self.scores))
        if sum(self.scores) == CCC_TOTAL_POINTS:
            text_color = Color.BLACK
            star_color = text_color
            bg_color = Color.GREEN
            bg_opacity = 150
        elif sum(self.scores) >= 4 * CCC_TOTAL_POINTS // 5:
            text_color = Color.GREEN
            star_color = text_color
            bg_opacity = 255
            bg_color = Color.MIDNIGHT_BLUE
        elif sum(self.scores) > 2 * CCC_TOTAL_POINTS // 5:
            text_color = Color.WHITE
            c = Color.SILVER_CHALICE
            star_color = pygame.Color(int(c.r*1.3), int(c.g*1.3), int(c.b*1.3))
            bg_color = Color.BLACK
            bg_opacity = 100
        else:
            text_color = Color.WHITE
            c = Color.ORANGE_PEEL
            star_color = pygame.Color(int(c.r*0.9), int(c.g*0.9), int(c.b*0.9))

            bg_color = Color.MIDNIGHT_BLUE
            bg_opacity = 120
        
        bg_color.a = bg_opacity

        # Completion bar
        bar_width = sum(self.scores) / CCC_TOTAL_POINTS * table.width
        pygame.draw.rect(surface,
                         bg_color,
                         (
                             0,
                             (table.height * table.header_size) + table.height * table.row_size * (row_num),
                             bar_width,
                             math.ceil(table.height * table.row_size))
                          )

        for j, datum in enumerate(data):
            data_text = Row.font.render(str(datum), True, text_color)
            surface.blit(
                data_text,
                (
                    j * table.width / len(table.header_labels) + PADDING * 2,
                    ((table.height * table.header_size) +
                        table.height * table.row_size * row_num) + PADDING * 2
                )
            )

            # horizontal line
            pygame.draw.rect(
                surface,
                table.color_dark,
                (
                    0,
                    (
                        (table.height * table.header_size) +
                        table.height * table.row_size * row_num + (table.height * table.row_size)
                    ),
                    table.width,
                    2
                )
            )

        # stars
        stars = []
        for score in self.scores:
            if score == 15:
                stars.append("★")
            elif score > 0:
                stars.append("☆")
            else:
                stars.append(" ")

        for i, sym in enumerate(reversed(stars)):
            star_text = Row.star_font.render(
                sym,
                True,
                star_color
            )
            star_text_width = star_text.get_width()
            
            x = table.width - (i + 1) * star_text_width - PADDING
            y = ((table.height * table.header_size)
                    + (table.height * table.row_size * row_num))

            surface.blit(star_text, (x, y))


class Table:
    shapelist: pygame.Surface
    header_size: int = 0.05
    header_labels: List[str] = ["name", "score"]
    color: Color = Color.DARK_BLUE_GRAY
    font = pygame.font.SysFont('Arial', FONT_SIZE)
    header_font = pygame.font.SysFont('Arial', FONT_SIZE, bold=True)

    def __init__(self, x: int=0, y: int=0, width: int=300, height: int=200):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rows: List[Row] = []
        self.table_img = pygame.Surface((self.width, self.height))
        self.student_rows_img = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32).convert_alpha()

        brightness = 0.5
        top_col = self.color
        r = top_col.r
        g = top_col.g
        b = top_col.b
        bot_col = pygame.Color(int(r * brightness), int(g * brightness), int(b * brightness))
        self.color_dark = bot_col

        # Table background gradient
        for y in range(0, self.height):
            percent = y / self.height
            color = top_col.lerp(bot_col, percent)
            pygame.draw.line(self.table_img, color, (0, y), (self.width, y))
        
        self.draw_table_header(self.table_img)
    
    def draw_table_header(self, surface):
        # table header
        # bg
        pygame.draw.rect(
            surface,
            self.color_dark,
            (0, 0, self.width, self.header_size * self.height)
        )

        # labels
        for i, label in enumerate(self.header_labels):
            header_text = Table.header_font.render(label.capitalize(), True, Color.WHITE)
            header_text_height = header_text.get_height()
            surface.blit(
                header_text,
                (
                    i*self.width/len(self.header_labels) + PADDING * 2,
                    header_text_height // 2 - PADDING
                )
            )

    @property
    def row_size(self):
        return (1 - self.header_size) / min(max(20, len(self.rows)), 35)


    def _add_row(self, rank: int, name: str, scores: List[int]):
        row = Row(rank=rank, name=name, scores=scores)
        self.rows.append(row)

    def add_rows(self, table_data: List):
        self.rows = []
        for student in table_data:
            rank = student["rank"]
            name = student["name"]
            scores = [
                student["problem1_score"],
                student["problem2_score"],
                student["problem3_score"],
                student["problem4_score"],
                student["problem5_score"],
            ]

            self._add_row(rank, name, scores)
        
        self._draw_students()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.table_img, (self.x, self.y))
        surface.blit(self.student_rows_img, (self.x, self.y))

    def _draw_students(self):
        # students
        for i, row in enumerate(self.rows):
            row.draw(self.student_rows_img, self, i)


pygame.init()


SIZE = (WIDTH, HEIGHT)

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("CCC Leaderboard")
clock = pygame.time.Clock()


junior_table = Table(x=PADDING * 4, y=PADDING * 4, width=WIDTH // 2 - PADDING * 6, height=int(HEIGHT * 1.0) - PADDING*8)
senior_table = Table(x=WIDTH//2 + PADDING * 2, y=PADDING * 4, width=WIDTH // 2 - PADDING * 6, height=int(HEIGHT * 1.0) - PADDING*8)

scraper = CCCScraper(username=USERNAME, password=PASSWORD, dev_mode=DEV_MODE)


def get_html_data(contest_id: int, table: Table):
    global scraper, stop_threads
    parser = CCCTableParser()
    while not stop_threads:
        html = scraper.scrape_leaderboard_html(contest_id=contest_id)
        parser.feed(html)
        table.add_rows([student for student in parser.table_data if student["total_score"] > 0])

        # Gives the ability to sleep the thread for a given time
        # and still be able to stop the thread mid-sleep
        for _ in range(5 if DEV_MODE else 20):
            if stop_threads:
                break
            time.sleep(1)


jr_number = 173 if DEV_MODE else JR_NUMBER
sr_number = 174 if DEV_MODE else SR_NUMBER
stop_threads = False

jr_fetch_thread = threading.Thread(target=get_html_data, args=(jr_number, junior_table))
jr_fetch_thread.start()

sr_fetch_thread = threading.Thread(target=get_html_data, args=(sr_number, senior_table))
sr_fetch_thread.start()

bg = pygame.Surface((WIDTH, HEIGHT), masks=pygame.SRCALPHA)
bg.fill((0, 0, 0, 0))
for y in range(HEIGHT):
    percent = y / HEIGHT
    color = Color.DARK_MIDNIGHT_BLUE.lerp(Color.LIGHT_BLUE, percent)
    pygame.draw.line(bg, color, (0, y), (WIDTH, y))

running = True
pygame.event.clear()
while running:
    # EVENT HANDLING
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
        elif event.type == QUIT:
            running = False

    screen.fill(Color.WHITE)

    screen.blit(bg, (0, 0))
    junior_table.draw(screen)
    senior_table.draw(screen)

    pygame.display.flip()
    clock.tick(30)


pygame.quit()
stop_threads = True
jr_fetch_thread.join()
sr_fetch_thread.join()
