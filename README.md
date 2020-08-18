# chordgen

For all you Arturia KeyLab Mark 1 users out there that can’t use the pad matrix to play chords here’s a partial solution. The only way to make use of the chord pads that I could find was with Arturia's Analog Lab V1. 
Subsequent versions dropped chord support so the pad keys became somewhat redundant. Annoyingly the KeyLab Mark2 versions apparently support one-finger-chords. So here’s a bit of python fun for Mark1 users to get some use out of those chord pads after all.

In fact the python code should work with any midi keyboard that has built in pads though you may have to figure out what midi messages the pad keys generate. 
Arturia Keylab makes decoding the pads easy with their Midi Control Centre that configures pad functions. 
The pads default to playing single notes across the scale on Midi Channel 10 so you don’t need to change anything. 
If you are using other control templates you need to restore the default pad functions for the python code to work.

You need Python 2.7 or 3.X to execute chordgen.py. Install the pygame module to provide midi support from here https://pypi.org/project/pygame/. 
Chordgen.py has only been tested in a Windows environment and you need to have Tobias Erichsen’s loopMidi running in the background. 
Get loopMidi from here http://www.tobias-erichsen.de/wp-content/uploads/2020/01/loopMIDISetup_1_0_16_27.zip. Using loopMidi add a named port eg ‘MyMidi’.

Chordgen 1.1 now has four modes: midi-info, one-finger-chords, pads and sequencer.

Midi info is supplied by the following command:
`python chordgen.py`
and will display all the midi ports on your system with output similar to this:
```
Device ID: 0 MMSystem Microsoft MIDI Mapper 0 1 0
Device ID: 1 MMSystem Bome MIDI Translator 1 1 0 0
Device ID: 2 MMSystem KeyLab 49 1 0 0
Device ID: 3 MMSystem MyMidi 1 0 0
Device ID: 4 MMSystem Microsoft GS Wavetable Synth 0 1 0
Device ID: 5 MMSystem Bome MIDI Translator 1 0 1 0
Device ID: 6 MMSystem KeyLab 49 0 1 0
Device ID: 7 MMSystem MyMidi 0 1 0
```
Identify the Keylab name to be your midi input, in my case ID 2 ‘Keylab 49 1 0 0’. Identify your loopMidi port for midi output, in my case ID 7 ‘MyMidi 0 1 0’. Note if the last element of the Device string is a ‘1’ then the midi port is already opened by another application.
You can now use midi input and output as arguments for the following chordgen commands.

One-finger-chords are generated by the following command:
`python chordgen.py -i "<input midi port>" -o “<output midi port>" `

This mode provides one-finger-chords across the whole keyboard. The pad matrix is used to select the chord to play eg major, minor, augmented or diminished, triads, sevenths or ninths as shown below:
![Alt text](padmap.png?raw=true)

Just leave the python running in the background and open say a DAW and connect to a VST. Make sure the VST gets its midi input from MyMidi and you should hear major triads the first time you hit a key. Change chord type by hitting the relevant pad as shown in the map above.

Pad mode is entered as follows:
`python chordgen.py -i "<input midi port>" -o “<output midi port>" –p <assign-pad-file>`

Pad mode is the mode most similar to that supplied by Arturia’s Analog Lab 1. The assign-pad-file has a simple json structure and assigns chords to pads. The “pad”:N value pair is simply used to make the file more readable since chords are assigned from pad1 to 16 in the order they appear in the file. The Chordtype options currently consists of major “M”, minor “m”, augmented “+” and diminished “o”. No suffix is required for triads eg major triad is just “M” whereas for sevenths and ninths you can add a 7 or 9 suffix.
```
{
    "chords": [
        {
            "pad" : 1,
            "chordtype": "M",
            "note" : "C5"
        },
        {
            "pad" : 2,
            "chordtype": "M",
            "note" : "Db5"
        },
. . . pads 3 to 10
        {
            "pad" : 11,
            "chordtype": "M9",
            "note" : "Bb5"
        },
        {
            "pad" : 12,
            "chordtype": "m9",
            "note" : "B5"
        }
    ]
}
```
Make sure a VST is running with midi input set to `output midi port`. Pressing a pad will the play the assigned chord. Main keys on the keyboard remain active for melody.

Sequence mode is entered as follows:
`python chordgen.py -i "<input midi port>" -o “<output midi port>" –s <gen-sequence-file>`

Sequence mode steps through a chord sequence defined in the gen-sequence-file. The gen-sequence-file has a simple json structure and generates the chord sequence. The “step”:N value pair is simply used to make the file more readable since chords are added to the playing sequence in the order they appear in the file. The Chordtype list is the same as that shown for Pad mode.
```
{
    "chords": [
        {
            "step" : 1,
            "chordtype": "M",
            "note" : "C5"
        },
        {
            "step" : 2,
            "chordtype": "M",
            "note" : "Db5"
        },
. . . as many intermediate steps as required to a last step, in this case 16
	{
            "step" : 16,
            "chordtype": "M",
            "note" : "B5"
        }
    ]
}
```
Once the python is running the chord sequence is stepped through by pressing pad1. The sequence can be reset back to the start by pressing pad2. Main keys on the keyboard remain active for melody.
