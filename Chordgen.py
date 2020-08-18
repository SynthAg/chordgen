# chordgen.py 
# 1.0 09-06-20
# 1.1 27-07-20 add --pads and --seq
# if you modify/republish code please give a shout-out for the site:
# https://synthagora.blogspot.com/

import pygame.midi
import time, sys, os, argparse, json
from miditime.miditime import MIDITime # just for note to pitch

def genMidiNote(noteoctave):
    mymidi = MIDITime()
    note_number = mymidi.note_to_midi_pitch(noteoctave)    # 'noteoctave' pair - octave is actual octave + 1
    # middle C is C4 so is C5 using miditime
    return note_number
    
def findMidiDevice(name, input):
    # return ID of midi device matching name for input (input=true) or output (input=false)
    
    for n in range(pygame.midi.get_count()):
        info = pygame.midi.get_device_info(n)
        if name in info:
            # info ('MMSystem', 'KeyLab 49', 1, 0, 0)
            # check if open
            if info[4] == 0:
                if input:
                    if info[2] == 1:
                        print ('Found Midi input device ' + name + ' ID: ' + str(n))
                        return n
                else:
                    if info[3] == 1:
                        print ('Found Midi output device ' + name + ' ID: ' + str(n))
                        return n
            else:
                print ('Error: Midi device ' + name + ' already open')
                return -1
    print ('Error: Midi device ' + name + ' not found')
    return -1
    
def getMidiDevices():
    # display info for all devices eg ('MMSystem', 'KeyLab 49', 1, 0, 0)
    
    for n in range(pygame.midi.get_count()):
        info = pygame.midi.get_device_info(n)
        device_line = 'Device ID: ' + str(n) + ' '
        for item in info:
            device_line += str(item) + ' '
        print(device_line)

def playNotes(event, device, notes, note_number, velocity):
    # play notes in 'notes' list if event = note_on (144), note off (128)
    # root note is note_number

    for note in notes:
        if event == 144:
            device.note_on(note_number + note, velocity)

        if event == 128:
            device.note_off(note_number + note, velocity)

def genChordNotes(chordtype):
    # generate chord notes - chordtype can be digit as string or chord symbol
            
    chords = [
        { "name" : "Major Triad", "symbol" : "M", "notes" : [0,4,7]},
        { "name" : "Minor Triad", "symbol" : "m", "notes" : [0,3,7]},
        { "name" : "Augmented Triad", "symbol" : "+", "notes" : [0,4,8]},
        { "name" : "Diminished Triad", "symbol" : "o", "notes" : [0,3,6]},
        
        { "name" : "Major Seventh", "symbol" : "M7", "notes" : [0,4,7,11]},
        { "name" : "Minor Seventh", "symbol" : "m7", "notes" : [0,3,7,10]},
        { "name" : "Augmented Seventh", "symbol" : "+7", "notes" : [0,4,8,12]},
        { "name" : "Diminished Seventh", "symbol" : "o7", "notes" : [0,3,6,9]},
        
        { "name" : "Major Ninth", "symbol" : "M9", "notes" : [0,4,7,11,14]},
        { "name" : "Minor Ninth", "symbol" : "m9", "notes" : [0,3,7,10,14]},
        { "name" : "Augmented Ninth", "symbol" : "+9", "notes" : [0,4,8,10,14]},
        { "name" : "Diminished Ninth", "symbol" : "o9", "notes" : [0,3,6,11,14]}
    ]

    if chordtype.isdigit():
        index = int(chordtype)
        print ('Chord type: ' + chords[index]["name"])
        return chords[index]["notes"]
    else:
        for chord in chords:
            if chord["symbol"] == chordtype:
                print ('Chord type: ' + chord["name"])
                return chord["notes"]

def readInput(input_device, output_device, mode, infile):
    # read midi loop Ctrl-C to exit
    
    chordtype = "0"
    if not mode == 'keys':
        with open(infile) as f:
            pjson = json.load(f)
        chords = pjson["chords"]
        chordfile_length = len(chords)
        chordtype = "M"
        
    notes = genChordNotes(chordtype)
    seq_count = 0
    output_device.set_instrument(0)
        
    try:
        while True:
            if input_device.poll():
                event = input_device.read(1)[0]
                # [[[144, 24, 120, 0], 1321]]
                # noteon, note, velocity
                data = event[0]
                timestamp = event[1]
                note_number = data[1]
                velocity = data[2]
                midievent = data[0] & 0xF0
                midichannel = data[0] & 0x0F

                # counts channels from 0 so channel10 is 9
                
                if mode == 'keys':
                    if midichannel == 0:
                        playNotes(midievent, output_device, notes, note_number, velocity)
                    if midichannel == 9:     
                        # default keylab pad channel 10; pads default to single notes C1 upwards
                        if midievent == 144:
                             chordtype = str(note_number % 12)
                             notes = genChordNotes(chordtype)
                             
                # TODO allow infile to change while looping
                if mode == 'pads':
                    
                    if midichannel == 0:    # allow main key action
                        main_notes = [0]
                        playNotes(midievent, output_device, main_notes, note_number, velocity)
                        
                    if midichannel == 9:
                        # default keylab pad channel 10; pads default to single notes C1 (#24) upwards; C2 (#36)

                        pad = note_number - 36
                        note = chords[pad]["note"]
                        root = genMidiNote(note)
                        if midievent == 144:   # could be causing left on notes
                            chordtype = chords[pad]["chordtype"]
                            notes = genChordNotes(chordtype)
                        playNotes(midievent, output_device, notes, root, velocity)   
                         
                if mode == 'seq':

                    if midichannel == 0:    # allow main key action
                        main_notes = [0]
                        playNotes(midievent, output_device, main_notes, note_number, velocity)
                        
                    if midichannel == 9:
                        # default keylab pad channel 10; pads default to single notes C1 upwards
                        # pad1 (index 0) plays chord and increments seq; pad2 resets seq; no decrement or repeat since handled by file
                        # TODO add sustain to note
                        
                        pad = note_number - 36
                        if pad == 1:    #reset seq and play first chord
                            seq_count = 0

                        note = chords[seq_count]["note"]
                        root = genMidiNote(note)
                        if midievent == 144:
                            chordtype = chords[seq_count]["chordtype"]
                            notes = genChordNotes(chordtype)
                        playNotes(midievent, output_device, notes, root, velocity)
                                
                        if midievent == 128:
                            print ('Sequence Step: ' + str(seq_count))
                            if pad == 0 or pad == 1:    # advance sequence
                                if (seq_count + 1) < chordfile_length:
                                    seq_count += 1
                                else:
                                    seq_count = 0   # wrap around

    except KeyboardInterrupt:
        input_device.close()
        output_device.close()
        print ('Chordgen terminated')

pygame.midi.init()

parser = argparse.ArgumentParser()
parser.add_argument("-i","--input", help="name of midi input device - use quotes if name has spaces")
parser.add_argument("-o","--output", help="name of midi output device - use quotes if name has spaces")
parser.add_argument("-p","--pads", help="pads had defined chords list in supplied file")
parser.add_argument("-s","--seq", help="pads trigger sequence of chords defined in supplied file")
args = parser.parse_args()

if not args.input and not args.output:
    getMidiDevices()
    sys.exit()

if not args.input:
    print ('Error: No input device specified')
    sys.exit()

if not args.output:
    print ('Error: No output device specified')
    sys.exit()
    
if not args.pads and not args.seq:
    mode = 'keys'    # keys
    infile = ''

if args.pads and not args.seq:
    mode = 'pads'    # pads trigger chords contained in filename
    if os.path.isfile(args.pads):
        infile = args.pads
    else:
        print ('Error: Input file not found')
        sys.exit()
    
if args.seq and not args.pads:
    mode = 'seq'    # sequencer generates chords in filename
    infile = args.seq
    if os.path.isfile(args.seq):
        infile = args.seq
    else:
        print ('Error: Input file not found')
        sys.exit()

# List Midi system devices
input_device = findMidiDevice(args.input, True)
if input_device < 0:
    sys.exit()
    
output_device = findMidiDevice(args.output, False)
if output_device < 0:
    sys.exit()

# Open midi input and output
my_input = pygame.midi.Input(input_device)     # keyboard ID
my_output = pygame.midi.Output(output_device)   # loopMidi ID

print ('Chordgen running in ' + mode + ' mode (Ctrl-C to exit)')

readInput(my_input, my_output, mode, infile)  # loop Ctrl-C to exit
