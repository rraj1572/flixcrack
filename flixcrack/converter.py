import re

timing_regex = re.compile(
    r"([\d\.:]+ \-\-\> [\d\.:]+) " + \
    r"position:[\d.\.]+%,\w+ align:(\w+) size:[\d.\.]+% line:([\d.\.]+)"
)

def fix(text: str):
    fixes = [
        ["\r", ""],
        ["\n", ""],
        ["&lt;", "<"],
        ["&gt;", ">"],
        ["&lrm;", "\u200e"],
        ["&rlm;", "\u200f"],
        ["&nbsp;", "\u00a0"],
        ["&amp;", "&"]
    ]
    for sf, r in fixes:
        text = text.replace(sf, r)
    text = re.sub("<\/?(([^/ibu>]{1})|([^/>]{2,}?))>", "", text)
    return text

class Converter:
    def __init__(self, file: str):
        self.name = file
        self.raw_name = ".".join(file.split(".")[:-1])

    def to_srt(self):
        new_lines = []
        timing_regex = re.compile(
            " ".join([
                r"([\d\.:]+ \-\-\> [\d\.:]+)",
                r"position:[\d.\.]+%,\w+ align:(\w+) size:[\d.\.]+% line:([\d.\.]+)"
            ])
        )
        lines = open(self.name, "r", encoding="utf8").readlines()
        
        verical_pos = -1     
        line_pos_matrix = [
            ["7", "8", "9"],
            ["4", "5", "6"],
            ["1", "2", "3"]
        ]
        
        for i, line in enumerate(lines):
            line = line.replace("\r", "")
            if line == "\n" or line.startswith("NOTE"):
                continue
            match = timing_regex.search(line)
            if not match:
                continue
            time = match.group(1).replace(".", ",")
            align_type = match.group(2)
            line_value = float(match.group(3))
            if line_value <= 25.00:
                verical_pos = 0
            elif line_value >= 75.00:
                verical_pos = 2
            else:
                verical_pos = 1
            horizontal_pos = {
                "middle": 1,
                "center": 1,
            }.get(align_type, -1)
            position = line_pos_matrix[verical_pos][horizontal_pos]
            new_lines.append(
                f"{time}\n" + ("{\\an%s}" % position) \
                .replace("{\\an2}", "") + fix(lines[i+1]) + "\n\n"
            )
        with open(self.raw_name + ".srt", "w+", encoding="utf-8") as f:
            f.writelines(new_lines)
