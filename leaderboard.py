from typing import List, Dict
from dataclasses import dataclass, field
import arcade
import threading
import time
from ccc_table_parser import CCCTableParser
from ccc_scraper import CCCScraper

DEV_MODE = True
with open(".credentials", "r") as f:
    USERNAME, PASSWORD = f.read().split("\n")

JR_NUMBER = 155  # 2020
SR_NUMBER = 157  # 2020

CCC_TOTAL_POINTS = 75
WIDTH = 1440
HEIGHT = 960
PADDING = 5
FONT_SIZE = 25


@dataclass
class Row:
    rank: int
    name: str
    scores: List[int]
    hovering: bool = False

    def update(self):
        pass

    def draw(self, table: "Table", row_num: int):
        data = self.name, str(sum(self.scores))
        if sum(self.scores) == CCC_TOTAL_POINTS:
            text_color = arcade.color.BLACK
            star_color = text_color
            bg_color = arcade.color.GREEN
            bg_opacity = 150
        elif sum(self.scores) >= 4 * CCC_TOTAL_POINTS // 5:
            text_color = arcade.color.GREEN
            star_color = text_color
            bg_opacity = 255
            bg_color = arcade.color.MIDNIGHT_BLUE
        elif sum(self.scores) > 2 * CCC_TOTAL_POINTS // 5:
            text_color = arcade.color.WHITE
            star_color = tuple(int(v*1.3) for v in arcade.color.SILVER_CHALICE)
            bg_color = arcade.color.BLACK
            bg_opacity = 100
        else:
            text_color = arcade.color.WHITE
            star_color = tuple(int(c*0.9) for c in arcade.color.ORANGE_PEEL)

            bg_color = arcade.color.MIDNIGHT_BLUE
            bg_opacity = 120
        # Completion bar
        bar_width = sum(self.scores) / CCC_TOTAL_POINTS * table.width
        arcade.draw_xywh_rectangle_filled(table.x,
                                          ((table.y + table.height - table.height * table.header_size)
                                           - table.height * table.row_size * (row_num + 1)),
                                          bar_width,
                                          table.height * table.row_size,
                                          (*bg_color, bg_opacity))

        for j, datum in enumerate(data):
            arcade.draw_text(
                str(datum),
                j * table.width / len(table.header_labels) + table.x + PADDING * 2,
                ((table.y + table.height - table.height * table.header_size) -
                    table.height * table.row_size * row_num - (table.height * table.row_size / 2)),
                text_color,
                font_size=FONT_SIZE,
                # width=table.width // len(data),
                bold=False,
                anchor_y="center")

            # horizontal line
            arcade.draw_lrtb_rectangle_filled(
                table.x,
                table.x + table.width,
                ((table.y + table.height - table.height * table.header_size) -
                    table.height * table.row_size * row_num - (table.height * table.row_size)),
                ((table.y + table.height - table.height * table.header_size) -
                    table.height * table.row_size * row_num - (table.height * table.row_size) - 2),
                table.color_dark)
        # stars
        stars = []
        for score in self.scores:
            if score == 15:
                stars.append("█")  # ★
            elif score > 0:
                stars.append("▒")  # ☆
            else:
                stars.append(" ")

        for i, sym in enumerate(reversed(stars)):
            arcade.draw_text(sym,
                             table.x + table.width - PADDING * 4 - i * FONT_SIZE * 1.4,
                             ((table.y + table.height - table.height * table.header_size)
                              - table.height * table.row_size * row_num - (table.height * table.row_size / 2)),
                             star_color,
                             font_size=FONT_SIZE,
                             font_name="Arial",
                            #  width=FONT_SIZE,
                            #  bold=False,
                             anchor_x="right",
                             anchor_y="center")



class Table:
    shapelist: arcade.ShapeElementList
    header_size: int = 0.05
    header_labels: List[str] = ["name", "score"]
    color: arcade.Color = arcade.color.DARK_BLUE_GRAY

    def __init__(self, x: int=0, y: int=0, width: int=300, height: int=200):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rows = []
        self.shapelist = arcade.ShapeElementList()

        brightness = 0.5
        top_col = self.color
        r, g, b = top_col
        bot_col = (int(r * brightness), int(g * brightness), int(b * brightness))
        self.color_dark = bot_col
        self.shapelist.append(
            arcade.create_rectangles_filled_with_colors(
                [(x, y), (x+self.width, y), (x+self.width, y+self.height), (x, y+self.height)],
                [bot_col, bot_col, top_col, top_col]
            ),
        )

    @property
    def row_size(self):
        return (1 - self.header_size) / min(max(20, len(self.rows)), 35)


    def add_row(self, rank: int, name: str, scores: List[int]):
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

            self.add_row(rank, name, scores)

    def update(self):
        for row in self.rows:
            row.update()

    def draw(self):
        # table bg
        self.shapelist.draw()

        # table header
        # bg
        arcade.draw_lrtb_rectangle_filled(self.x,
                                          self.x+self.width,
                                          self.y+self.height,
                                          self.y+self.height - self.header_size*self.height,
                                          self.color_dark)

        # labels
        for i, label in enumerate(self.header_labels):
            arcade.draw_text(label.capitalize(),
                             i*self.width/len(self.header_labels) + self.x + PADDING * 2,
                             self.y+self.height-self.height*self.header_size/2,
                             arcade.color.WHITE,
                             font_size=20,
                            #  width=self.width,
                             bold=True,
                             anchor_y="center")

        # students
        # print(self.rows)
        for i, row in enumerate(self.rows):
            row.draw(self, i)

window = arcade.open_window(WIDTH, HEIGHT, "CCC Leaderboard")


junior_table = Table(x=PADDING * 4, y=PADDING * 4, width=WIDTH // 2 - PADDING * 6, height=int(HEIGHT * 1.0) - PADDING*8)
senior_table = Table(x=WIDTH//2 + PADDING * 2, y=PADDING * 4, width=WIDTH // 2 - PADDING * 6, height=int(HEIGHT * 1.0) - PADDING*8)

scraper = CCCScraper(username=USERNAME, password=PASSWORD, dev_mode=DEV_MODE)


def get_html_data(contest_id: int, table: Table):
    global scraper
    parser = CCCTableParser()
    while True:
        html = scraper.scrape_leaderboard_html(contest_id=contest_id)
        parser.feed(html)
        table.add_rows([student for student in parser.table_data if student["total_score"] > 0])
        time.sleep(5 if DEV_MODE else 20)


jr_number = 123 if DEV_MODE else JR_NUMBER
sr_number = 124 if DEV_MODE else SR_NUMBER

jr_fetch_thread = threading.Thread(target=get_html_data, args=(jr_number, junior_table))
jr_fetch_thread.start()

sr_fetch_thread = threading.Thread(target=get_html_data, args=(sr_number, senior_table))
sr_fetch_thread.start()

bg_shapelist = arcade.ShapeElementList()
bg_shapelist.append(
    arcade.create_rectangles_filled_with_colors(
        [(0, 0), (0, HEIGHT), (WIDTH, HEIGHT), (WIDTH, 0)],
        [arcade.color.DARK_MIDNIGHT_BLUE, arcade.color.LIGHT_BLUE, arcade.color.LIGHT_BLUE, arcade.color.DARK_MIDNIGHT_BLUE]))


def update(delta_time):
    pass


@window.event
def on_draw():
    arcade.start_render()
    bg_shapelist.draw()
    junior_table.draw()
    senior_table.draw()


@window.event
def on_key_press(key, modifiers):
    if key == arcade.key.F:
        window.set_fullscreen(not window.fullscreen)
        # width, height = window.get_size()
        # print(width, height)


arcade.set_background_color(arcade.color.WHITE)
arcade.schedule(update, 1/60)
arcade.run()
