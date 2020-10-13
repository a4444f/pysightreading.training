import random

import pygame
import pygame.freetype
import pygame.midi


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


midi_to_line = {}

question_notes = list({84: -2, 83: -1.5, 81: -1, 79: -.5, 77: 0, 76: .5, 74: 1, 72: 1.5, 71: 2, 69: 2.5, 67: 3, 65: 3.5, 64: 4,
                     62: 4.5, 60: 5, 59: 5.5, 57: 6, 55: 6.5, 53: 7, 52: 7.5, 50: 8, 48: 8.5, 47: 9, 45: 9.5, 43: 10,
                     41: 10.5,
                     40: 11, 38: 11.5, 36: 12}.keys())

def init_midi_to_line():
    last_note = None
    line = 22.5
    for i in range(0, 128):

        ansi_note = pygame.midi.midi_to_ansi_note(i)
        note = ansi_note[0]
        midi_to_line[i] = line
        if last_note != note:
            line -= 0.5
        last_note = note

init_midi_to_line()

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
    #pygame.draw.circle(surface, (255, 255, 255), (x,y), 10)

    staff_y_off = height / 7
    line_y_spacing = height / 16
    staff_height = line_y_spacing * 4
    line_x_off = staff_y_off / 2 * 1.2
    line_width = width - line_x_off


    def note_to_y(midi_note):  # relative to line number (0 is uppermost visible treble line)
        return int(staff_y_off + midi_to_line[midi_note] * line_y_spacing)
    def line_to_y(line):
        return int(staff_y_off + line * line_y_spacing)

    # render green field

    pygame.draw.rect(surface, pygame.Color(0x9f, 255, 0xb8), pygame.Rect(line_x_off + line_width * green_field_start, 0, line_width*green_field_width, height))

    # render staffs
    STAFF_FONT = pygame.freetype.SysFont("FreeSerif", 165)
    #STAFF_FONT.render_to(surface, (line_x_off * 1.2, note_to_y(77)), "𝄞", fgcolor)
    STAFF_FONT.render_to(surface, (line_x_off * 1.2, line_to_y(-1)), "𝄞", fgcolor)
    STAFF_FONT.render_to(surface, (line_x_off * 1.2, note_to_y(56)), "𝄢", fgcolor)

    def draw_note(midi_note, x_norm, style="norm", note_color=fgcolor):
        note_x = int(line_x_off + x_norm * line_width)
        note_y = note_to_y(midi_note)
        radius = int(line_y_spacing * .4)

        line = midi_to_line[midi_note]

        # pygame.draw.circle(surface, fgcolor, (note_x, note_y), radius, 2)
        text_surface, rect = GAME_FONT.render("𝅝", note_color)
        #text_surface = pygame.transform.smoothscale(text_surface, (int(text_surface.get_width() * 1.05), text_surface.get_height()))
        rect.center = (note_x, note_y)

        if style == "text" or model['notes_text']:
            TEXT_FONT.render_to(surface, (note_x, line_to_y(5)), pygame.midi.midi_to_ansi_note(midi_note), note_color)
            #TEXT_FONT.render_to(surface, rect, pygame.midi.midi_to_ansi_note(midi_note), note_color)
        else:
            surface.blit(text_surface, rect)


        #GAME_FONT.render_to(surface, (note_x, note_y), "x", fgcolor)
        bpm = int(100 * 100 / (0.2 / game_state['speed']))
        #TEXT_FONT.render_to(surface, (line_x_off, line_to_y(12)), "speed " + str(bpm) + " " + str(model['fps']), note_color)
        TEXT_FONT.render_to(surface, (line_x_off, line_to_y(12)), " " * 50 + "speed " + str(bpm)  +" hits " + str(model['hits'])+ \
                            " misses " + str(model['misses']), note_color)

        def draw_helper(line):
            helper_y = line_to_y(line)
            pygame.draw.line(surface, fgcolor, (note_x - radius * 2.5, helper_y), (note_x + radius * 2.5, helper_y), 2)
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


    def sl_to_y(staff, line):
        return staff_y_off + staff * (line_y_spacing * 2 + staff_height) + line_y_spacing * line
    for staff in [0, 1]:  #  "treble", "bass"):
        pygame.draw.line(surface, fgcolor, (line_x_off, sl_to_y(staff, 0)), (line_x_off, sl_to_y(staff, 4) + 1), 6)
        for line in [0,1,2,3,4]:
            y = staff_y_off + staff * (line_y_spacing * 2 + staff_height) + line_y_spacing * line
            pygame.draw.line(surface, fgcolor, (line_x_off, y), (width, y), 2)
    for (note, normalized) in notes:  #[84, 83, 81, 38, 36]:
        draw_note(note, normalized)
    if grey_note and game_state['last_note_delay']:
        draw_note(grey_note, notes[0][1], style="norm", note_color=(125, 125, 125))
        game_state['last_note_delay'] -= 1


if __name__ == '__main__':
    pygame.midi.init()
    pygame.init()
    screen = pygame.display.set_mode((900, 480))
    clock = pygame.time.Clock()
    midi_in, midi_out = get_midi()
    print(midi_in, midi_out)
    state = "new_note"
    last_note = None
    grey_note = None
    question_note = None
    notes = []
    delay = 0

    model = {
        'notes_text': False,
        'last_note_delay': 0,
        'speed': 0.002,
        'lowest_speed': 0.002,
        'fps': 0,
        'hits': 0,
        'misses': 0,
        'hit_history': []
    }
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                elif event.type == pygame.KEYDOWN and \
                        event.key == pygame.K_m:
                    model['notes_text'] = not model['notes_text']
            if not notes or notes[-1][1] < 0.8:
                notes.append([random.choice(question_notes), 1])
            if notes and notes[0][1] <= 0.2:
                # if model['speed'] >= 0.0015:
                #     model['speed'] -= 0.000001
                    pass
            #     model['speed'] = 0.0015
            #     notes = notes[1:]
            if notes and notes[0][1] > 0.2:
                for i in range(len(notes)):
                    notes[i][1] -= model['speed']


            if delay != 0:
                delay -= 1
            else:
                if state == "new_note":
                    question_note = notes[0][0] # random.randrange(48, 85)
                    state = "ask_note"
                if state == "ask_note":
                    # midi_out.set_instrument(0, 1)
                    # midi_out.note_on(question_note, 120, 1)
                    print("\n?", pygame.midi.midi_to_ansi_note(question_note), end=' : ')
                    state = "get_answer"
                elif state == "get_answer":
                    if last_note == question_note:  # correct
                        last_note = None
                        grey_note = None
                        delay = 10
                        state = "new_note"
                        model['hits'] += 1
                        if green_field_start <= notes[0][1] <= green_field_end:
                            model['hit_history'].append('green')
                            if (len(model['hit_history'])) > 0:
                                model['speed'] += 0.00005
                                model['hit_history'] = []
                        else:
                            if model['hit_history']:
                                model['hit_history'] = []
                            if model['speed'] >= model['lowest_speed']:
                                if not notes[0][1] > 0.2:
                                    model['speed'] -= 0.00005

                            pass
                        notes = notes[1:]
                    elif last_note is None:
                        pass
                    else:  # incorrect
                        model['misses'] += 1
                        if model['hit_history']:
                            model['hit_history'] = []
                        if model['speed'] >= model['lowest_speed']:
                            model['speed'] /= 1.05

                        #if model['speed'] > 0.01:
                        #    model['speed'] /= 1.1
                        # state = "ask_note"
                        grey_note = last_note

                        last_note = None
                        pass
                        # delay = 10
            x = midi_in.read(1000)
            if x:
                for p in x:
                    (a, b, c, d) = p[0]
                    if a == 144 and c != 0:  # note on
                        print(midi_to_line[b], b, pygame.midi.midi_to_ansi_note(b), end='\n ')
                        last_note = b
                        grey_note = b
                        model['last_note_delay'] = 15
                        #notes.append([b,1])
                midi_out.write(x)
            draw_board(notes, model)
            pygame.display.flip()
            clock.tick(100)
            model['fps'] = clock.get_fps()

    except KeyboardInterrupt:
        del midi_in
        del midi_out


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
