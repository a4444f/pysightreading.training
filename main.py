import random
import pygame
import pygame.freetype
import pygame.midi


class Controller(object):
    @staticmethod
    def get_midi():
        _midi_in = None
        _midi_out = None
        for i in range(0, pygame.midi.get_count()):
            (interface, name, _input, output, opened) = pygame.midi.get_device_info(i)
            print((interface, name, _input, output, opened))
            if name == b'UM-ONE MIDI 1' and _input == 1:
                _midi_in = pygame.midi.Input(i)
            elif name == b'in' and output == 1:
                _midi_out = pygame.midi.Output(i)
        return _midi_in, _midi_out

    def __init__(self):
        self.midi_in, self.midi_out = Controller.get_midi()


class Note(object):
    note_spacing = 0.2
    question_notes = list(
        {84: -2, 83: -1.5, 81: -1, 79: -.5, 77: 0, 76: .5, 74: 1, 72: 1.5, 71: 2, 69: 2.5, 67: 3, 65: 3.5, 64: 4,
         62: 4.5, 60: 5, 59: 5.5, 57: 6, 55: 6.5, 53: 7, 52: 7.5, 50: 8, 48: 8.5, 47: 9, 45: 9.5, 43: 10,
         41: 10.5, 40: 11, 38: 11.5, 36: 12}.keys())
    midi_to_line = {}
    last_random_note = None

    def __init__(self, _style):
        self.style = _style
        if Note.last_random_note:
            while True:
                self.midi = random.choice(Note.question_notes)
                if abs(self.midi - Note.last_random_note) < 10:
                    break
        else:
            self.midi = random.choice(Note.question_notes)
        Note.last_random_note = self.midi
        self.pos = 1

        self._length_index = 0  # random.choice([0, 1, 2, 3])
        self.length = [1, 0.5, 0.25, 0.125][self._length_index]
        self.pos_end = 1 + self.length * Note.note_spacing
        self.text = "𝅝𝅗𝅥𝅘𝅥𝅘𝅥𝅮"[self._length_index]

        self.ansi = pygame.midi.midi_to_ansi_note(self.midi)
        self.line = Note.midi_to_line[self.midi]

    @staticmethod
    def init_midi_to_line():
        _last_note = None
        line = 22.5
        for _i in range(0, 128):
            ansi_note = pygame.midi.midi_to_ansi_note(_i)
            note = ansi_note[0]
            Note.midi_to_line[_i] = line
            if _last_note != note:
                line -= 0.5
            _last_note = note


Note.init_midi_to_line()

green_field_start = 3 / 7.
green_field_width = 1 / 7.
green_field_end = 4 / 7


def draw_board(notes, game_state):
    bgcolor = pygame.Color(255, 255, 255, 0)
    fgcolor = (0, 0, 0)
    GAME_FONT = pygame.freetype.SysFont("FreeSerif", 120)
    TEXT_FONT = pygame.freetype.SysFont("FreeSerif", 25)

    surface = pygame.display.get_surface()
    surface.fill(bgcolor)
    width, height = surface.get_width(), surface.get_height()
    # pygame.draw.circle(surface, (255, 255, 255), (x,y), 10)

    staff_y_off = height / 7
    line_y_spacing = height / 16
    staff_height = line_y_spacing * 4
    line_x_off = staff_y_off / 2 * 1.2
    line_width = width - line_x_off

    def note_to_y(midi_note):  # relative to line number (0 is uppermost visible treble line)
        return int(staff_y_off + Note.midi_to_line[midi_note] * line_y_spacing)

    def line_to_y(line):
        return int(staff_y_off + line * line_y_spacing)

    # render green field

    pygame.draw.rect(surface, pygame.Color(0x9f, 255, 0xb8),
                     pygame.Rect(line_x_off + line_width * green_field_start, 0, line_width * green_field_width,
                                 height))

    # render staffs
    STAFF_FONT = pygame.freetype.SysFont("FreeSerif", 165)
    # STAFF_FONT.render_to(surface, (line_x_off * 1.2, note_to_y(77)), "𝄞", fgcolor)
    STAFF_FONT.render_to(surface, (line_x_off * 1.2, line_to_y(-1)), "𝄞", fgcolor)
    STAFF_FONT.render_to(surface, (line_x_off * 1.2, note_to_y(56)), "𝄢", fgcolor)

    def draw_note(midi_note, x_norm, style="norm", note_color=fgcolor, note_text=random.choice("𝅝𝅗𝅥𝅘𝅥𝅘𝅥𝅮𝅘𝅥𝅯𝅘𝅥𝅰𝅘𝅥𝅱𝅘𝅥𝅲"),
                  _note=None):
        note_x = int(line_x_off + x_norm * line_width)
        note_x2 = int(note_x + line_width * Note.note_spacing * _note.length)
        note_y = note_to_y(midi_note)
        radius = int(line_y_spacing * .4)

        line = Note.midi_to_line[midi_note]

        # draw note as a circle
        # pygame.draw.circle(surface, fgcolor, (note_x, note_y), radius, 2)


        #draw note length line
        #pygame.draw.line(surface, (0x9f, 255, 0xb8), (note_x, note_y), (note_x2, note_y), 3)



        # text_surface, rect = GAME_FONT.render("𝅝", note_color)
        text_surface, rect = GAME_FONT.render(note_text, note_color)
        # text_surface = pygame.transform.smoothscale(text_surface, (int(text_surface.get_width() * 1.05), text_surface.get_height()))
        # rect.center = (note_x, note_y)
        rect.midbottom = (note_x, note_y + line_y_spacing / 2)

        if style == "text":
            TEXT_FONT.render_to(surface, (note_x, line_to_y(5)), pygame.midi.midi_to_ansi_note(midi_note), note_color)
            # TEXT_FONT.render_to(surface, rect, pygame.midi.midi_to_ansi_note(midi_note), note_color)
        else:
            surface.blit(text_surface, rect)
            # TEXT_FONT.render_to(surface, (note_x+30, rect.y), pygame.midi.midi_to_ansi_note(midi_note), note_color)
            TEXT_FONT.render_to(surface, (note_x, line_to_y(5)), pygame.midi.midi_to_ansi_note(midi_note), note_color)

            def draw_helper(line):
                helper_y = line_to_y(line)
                pygame.draw.line(surface, fgcolor, (note_x - radius * 2.5, helper_y), (note_x + radius * 2.5, helper_y),
                                 2)

            if line == 5:
                draw_helper(5)
            if line <= -1:
                draw_helper(-1)
            if line <= -2:
                draw_helper(-2)
            if line >= 11:
                draw_helper(11)
            if line >= 12:
                draw_helper(12)

        # GAME_FONT.render_to(surface, (note_x, note_y), "x", fgcolor)
        bpm = int(100 * 100 / (Note.note_spacing / game_state['speed']))
        max_bpm = int(100 * 100 / (Note.note_spacing / game_state['max_speed_so_far']))
        # TEXT_FONT.render_to(surface, (line_x_off, line_to_y(12)), "speed " + str(bpm) + " " + str(model['fps']), note_color)
        TEXT_FONT.render_to(surface, (line_x_off, line_to_y(12)),
                            " " * 50 + "max " + str(max_bpm) + " speed " + str(bpm) + " hits " + str(model['hits']) + \
                            " misses " + str(model['misses']), note_color)

    def sl_to_y(staff, line):
        return staff_y_off + staff * (line_y_spacing * 2 + staff_height) + line_y_spacing * line

    for staff in [0, 1]:  # "treble", "bass"):
        pygame.draw.line(surface, fgcolor, (line_x_off, sl_to_y(staff, 0)), (line_x_off, sl_to_y(staff, 4) + 1), 6)
        for line in [0, 1, 2, 3, 4]:
            y = staff_y_off + staff * (line_y_spacing * 2 + staff_height) + line_y_spacing * line
            pygame.draw.line(surface, fgcolor, (line_x_off, y), (width, y), 2)
    for note in notes:
        draw_note(note.midi, note.pos, note.style, note_text=note.text, _note=note)
    if grey_note and game_state['last_note_delay']:
        draw_note(grey_note, notes[0].pos, style="norm", note_color=(125, 125, 125), note_text="𝅝", _note=note)
        game_state['last_note_delay'] -= 1


if __name__ == '__main__':
    pygame.midi.init()
    pygame.init()
    screen = pygame.display.set_mode((900, 480))
    clock = pygame.time.Clock()
    controller = Controller()

    state = "new_note"
    last_note = None
    grey_note = None
    question_note = None
    notes = []
    delay = 0

    model = {
        'notes_text': False,
        'last_note_delay': 0,
        'speed': 0.0025,
        'lowest_speed': 0.0025,
        'max_speed_so_far': 0.0025,
        'fps': 0,
        'hits': 0,
        'misses': 0,
        'hit_history': [],
        'play_question_note_delay': 0
    }
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                elif event.type == pygame.KEYDOWN and \
                        event.key == pygame.K_m:
                    model['notes_text'] = not model['notes_text']
            if not notes or notes[-1].pos_end < 1:
                if model['notes_text']:
                    style = "text"
                else:
                    style = "norm"
                notes.append(Note(style))
                # model['notes_text'] = not model['notes_text']
            if notes and notes[0].pos <= 0.2:
                # if model['speed'] >= 0.0015:
                #     model['speed'] -= 0.000001
                pass
            #     model['speed'] = 0.0015
            #     notes = notes[1:]
            if notes and notes[0].pos > 0.2:
                for i in range(len(notes)):
                    notes[i].pos -= model['speed']
                    notes[i].pos_end -= model['speed']
            if delay != 0:
                delay -= 1
            else:
                if state == "new_note":
                    question_note = notes[0].midi
                    state = "ask_note"
                if state == "ask_note":




                    print("\n?", pygame.midi.midi_to_ansi_note(question_note), end=' : ')
                    state = "get_answer"
                elif state == "get_answer":

                    if model['play_question_note_delay'] == 0:
                        controller.midi_out.set_instrument(0, 1)
                        controller.midi_out.note_on(question_note, 120, 1)
                    model['play_question_note_delay'] -= 1

                    if last_note == question_note:  # correct
                        last_note = None
                        grey_note = last_note
                        delay = 30
                        state = "new_note"
                        model['play_question_note_delay'] = 50
                        model['hits'] += 1
                        if green_field_start <= notes[0].pos <= green_field_end:
                            model['hit_history'].append('green')
                            if (len(model['hit_history'])) > 0:
                                model['speed'] += 0.00005
                                model['max_speed_so_far'] = max(model['max_speed_so_far'], model['speed'])
                                model['hit_history'] = []
                        else:
                            if model['hit_history']:
                                model['hit_history'] = []
                            if model['speed'] >= model['lowest_speed']:
                                if not notes[0].pos > 0.2:
                                    model['speed'] -= 0.00005
                            pass
                        notes = notes[1:]
                    elif last_note is None:
                        pass
                    else:  # incorrect
                        model['play_question_note_delay'] = 50
                        model['misses'] += 1
                        if model['hit_history']:
                            model['hit_history'] = []
                        if model['speed'] >= model['lowest_speed']:
                            model['speed'] /= 1.05
                        # if model['speed'] > 0.01:
                        #    model['speed'] /= 1.1
                        # state = "ask_note"
                        grey_note = last_note
                        last_note = None
                        # delay = 10
            midi_events = controller.midi_in.read(1000)
            if midi_events:
                for p in midi_events:
                    (a, b, c, d) = p[0]
                    if a == 144 and c != 0:  # note on
                        print(Note.midi_to_line[b], b, pygame.midi.midi_to_ansi_note(b), end='\n ')
                        last_note = b
                        grey_note = b
                        model['last_note_delay'] = 15
                        # notes.append([b,1])
                controller.midi_out.write(midi_events)
            draw_board(notes, model)
            pygame.display.flip()
            clock.tick(100)
            model['fps'] = clock.get_fps()

    except (KeyboardInterrupt, SystemExit):
        del controller.midi_in
        del controller.midi_out

# note input:
# - flute
# - text
# - mouse
# - sound?
#
# note presentation:
# - postion
# - name
# - sound


# different note lengths
# exercise engine [ dobieranie cwiczenia na podstawie algorytmu uczacego sie, jak juz dobrze, to kolejne nowe
# dzwieki nut
# glosno / cicho
# rozne czasy trwania nut
# slurrs
# trills
# pomysly z dziury


# wszystkie możliwe nuty z ewi 4000s
