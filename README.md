![The sorting office before the doors open: an empty scarred sorting table with a tied bundle seen from behind at its far end, a brass scale with its pan empty and level, rows of tables and pigeonhole grids behind, a stamp sheet lying face down, and tall windows full of dusty morning light](intro-banner.png)

# bde-Execution-Path-Visualizer

![A London sorting office in 1840 with sorting tables in rows, clerks holding tied bundles, pigeonholes filling the back wall, a letter held up close at the right with its Penny Black and red postmark, and the name bde-execution-path-visualizer on the carbon blue direction board above the central aisle](banner.png)

![A Penny Black stamp drawn square and close, straight scissor cut edges, the queen profile facing left in white against a black ground, corner letters in the lower squares, and a red postmark arc crossing its upper right, the heading plate](logo.png)

![Sorting office scene in three depths: pigeonholes brighten in turn along the far wall, bundles advance along the central table in short stops while a postmark arc fades in over each, dust drifts down in the near window shafts, and the brass scale pan sits level and still](scene.svg)

A command-line tool that writes a Graphviz dot file listing the call shaped names found in a script, as a flat list of edges from one MainScript node. There is no branching or control flow structure in the output: the name matcher also picks up keywords, so words such as `if` and `for` appear in the list as if they were calls, and no function definitions, conditions, or branch targets are represented. Optional steps before listing are jsbeautifier formatting, string decoding, and renaming underscore variables. String decoding covers base64 in the Python `b'...'` literal shape, and hex only inside a quoted `0x` literal such as `'0x41'`; numeric literals outside quotes are left alone. The script being listed is read as text and never run.

> **Postmarked note: no branches are drawn.** There is no branching or control flow structure in the output, and no function definitions, conditions, or branch targets are represented.

> **Postmarked note: keywords are listed as if they were calls.** The name matcher also picks up keywords, so words such as `if` and `for` appear in the list as if they were calls.

> **Postmarked note: the unexplained switch.** `-o` is listed with no description provided. This document does not guess that it names the output dot file.

![Section divider: a tied string line with a sealing wax dot at its centre](sep-heavy.svg)

## Install
`git clone https://github.com/ShadowStrikeHQ/bde-execution-path-visualizer`

![Section divider: a tied string line with a smaller wax dot off centre](sep-light.svg)

## Usage
`./bde-execution-path-visualizer [params]`

![Section divider: a tied string line with a sealing wax dot at its centre](sep-heavy.svg)

## Parameters
- `-h`: Show help message and exit
- `-o`: No description provided
- `-v`: Enable verbose logging
- `--beautify`: Beautify the input script before analysis.
- `--decode_strings`: Attempt to decode encoded strings: base64 in the Python `b'...'` literal shape, and hex only inside a quoted `0x` literal such as `'0x41'`. Numeric literals such as `0x10` outside quotes are left alone.
- `--rename_variables`: Attempt to rename obfuscated variables.

![Section divider: a tied string line with a sealing wax dot at its centre](sep-heavy.svg)

## License
Copyright (c) ShadowStrikeHQ
