# Unturned Note Generator

A simple command line tool to generate unturned note objects from a single YAML or JSON file with support for multiple languages.

Example config

```yaml
name: Your map here
notes:
  - guid: bb3b06d0491049a693a106a6e42657d7
    id: 13500
    name: a note
    text:
      - language: english
        text:
          - line1
          - line2
```

## Installation

First, install Python

Download the [latest release](https://github.com/khakers/unturned-note-generator/releases/latest) and unzip it.

Open the unzipped folder, and using a terminal, run

    python setup.py install

You can access the tool by running the command `notegen`

## Usage

The CLI interface is **not** guaranteed to be stable.

Currently, the program will write to your config file after it finishes running, the result of which is that anything you add beyond the basic yaml structure will be wiped (i.e. comments).

    ❯ notegen --help
    Usage: notegen [OPTIONS] FOLDERPATH

    Options:
    -c, --config FILE            Specify the notes config file to use.
    -l, --language, --lang TEXT  Specify the languages to build notes for
                                [default: english]
    -d, --dry-run                Don't create notes files. Usefull to check what will be created and where.
    --help                       Show this message and exit.

To create a basic note, copy [example.yml](example.yml), and run the command `notegen --config ./example.yml ./notes`.
This will create a `notes` folder, within it, there should be a `first_note`, and `second_note` folder. In these folders, you'll find the .dat folders needed for unturned to load the notes. By default, only the english note text will be built, if you want to include other languages, you'll need to specify them with `--language lang`. To build all the text included in the example config, you'd need to use the command `notegen --config ./example.yml --language english --language tchinese ./notes`.

When building your own notes, it's recommended you build them into a distinct folder. for example `map/bundles/notes/`.
It's important to keep in mind that notes are currently tracked via their name, so if you change the name of a note, it's files won't be deleted.

If you don't specify a GUID, one will be generated for you.
