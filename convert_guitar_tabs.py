import enum
import re
import sys


class Note:
    CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    KALIMBA_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

    def __init__(self, name, octave):
        self.name = name
        self.octave = octave

    def __str__(self):
        return f"{self.name}{self.octave}"

    def __repr__(self):
        return f"{self.name}{self.octave}"

    def transpose(self, semitones):
        current_index = self.CHROMATIC_SCALE.index(self.name)
        new_index = current_index + semitones
        new_octave = self.octave + (new_index // 12)
        new_index = new_index % 12
        new_name = self.CHROMATIC_SCALE[new_index]
        return Note(new_name, new_octave)

    def to_kalimba(self, base_octave=3):
        number = self.KALIMBA_NOTES.index(self.name[0]) + 1
        octave_diff = self.octave - base_octave

        dots = ""
        if octave_diff < 0:
            number = "1"
        elif octave_diff == 1:
            dots = "."
        elif octave_diff == 2:
            dots = ":"
        elif octave_diff > 3:
            dots = ":"
            number = min(3, number)

        return f"{number}{dots}"


class GString(enum.Enum):
    E_LOW = ('E', 2)
    A = ('A', 2)
    D = ('D', 3)
    G = ('G', 3)
    B = ('B', 3)
    E_HIGH = ('e', 4)

    @staticmethod
    def get_note(note, octave=None):
        for string in GString:
            if string.value[0] == note and (octave is None or string.value[1] == octave):
                return Note(string.value[0].upper(), string.value[1])
        raise ValueError(f"No guitar string matches the note {note} with octave {octave}")


def parse_line(line):
    frets = []
    line_splits = line.split('|')
    string = line_splits[0]
    line = line_splits[1]
    for i in range(1, len(line), 4):
        if line[i].isdigit():
            frets.append(int(line[i]))
        elif line[i] == '-':
            frets.append(-1)
        else:
            raise ValueError('parsing error')
    return string, frets


def process_phrase(phrase):
    notes = []
    for line in phrase:
        string, frets = parse_line(line)
        note = GString.get_note(string)
        row = []
        for fret in frets:
            row.append(note.transpose(fret).to_kalimba() if fret != -1 else None)
        notes.append(row)

    # print Kalimba sheet style
    output = []
    for k_nums in zip(*notes):
        k_nums = [k_num for k_num in k_nums if k_num]
        if len(k_nums) > 1:
            group = "(" + "".join(k_nums) + ")"
            output.append(group)
        else:
            output.append(k_nums[0])
    print(" ".join(output)) 


def extract_tabs(lines):
    tab_line_pattern = re.compile(r'^[eBGDAEe]\|[-0-9|]+')
    tabs = []
    for line in lines:
        if tab_line_pattern.match(line.strip()):
            tabs.append(line.strip())
    
    assert len(tabs) % 6 == 0, ValueError('file parsing error')
    phrases = []
    for i in range(0, len(tabs), 6):
        phrases.append(tabs[i:(i+6)])
    return phrases


def read_file(filename):
    """Read and display guitar tabs from a given file."""
    try:
        with open(filename, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        print("The file was not found. Please check the filename and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    tabs = extract_tabs(read_file(filename))
    [process_phrase(p) for p in tabs]

if __name__ == "__main__":
    main()