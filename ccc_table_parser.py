from html.parser import HTMLParser


class CCCTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.recording = False
        self._table = []
        self.current_row = []

    @staticmethod
    def parse_name(raw_name):
        parts = [part.capitalize() for part in raw_name.split(" ")]
        parts.pop()
        return " ".join(parts)

    FIELD_MAP = {
        "rank": int,
        "name": str,
        "school": str,
        "problem1_score": int,
        "problem2_score": int,
        "problem3_score": int,
        "problem4_score": int,
        "problem5_score": int,
        "total_score": int,
    }

    def handle_starttag(self, tag, attrs):
        if not self.recording and ('class', 'grader-table') in attrs:
            # print("Found table of interest!:", tag, f"attrs: {attrs}")
            self._table = []
            self.recording = True

    def handle_endtag(self, tag):
        if self.recording and tag == 'table':
            # print("End of table of interest!")
            self.recording = False
        elif self.recording and tag == 'tr':
            self._table.append(self.current_row)
            self.current_row = []

    def handle_data(self, data):
        if self.recording:
            # print(f"\t{data}")
            if '\\n' not in data:
                self.current_row.append(data)

    @property
    def table_headers(self):
        try:
            return self._table[0]
        except IndexError:
            return None

    @property
    def table_data(self):
        # print(f"table_data: \n{self._table}\n\n")
        try:
            return [
                {field_name: func(data) for (field_name, func), data in zip(self.FIELD_MAP.items(), row)}
                for row in self._table[1:]
            ]
        except IndexError:
            return None

    @property
    def table(self):
        return self.table_headers + self.table_data

    @property
    def problem_names(self):
        try:
            return self.table_headers[3:-1]
        except IndexError:
            return None
