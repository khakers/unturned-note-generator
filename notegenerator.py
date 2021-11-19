import json
from typing import List
from click.exceptions import FileError
from jinja2.loaders import FileSystemLoader
from pathvalidate.error import ValidationError
import yaml
from yaml.loader import FullLoader
from uuid import uuid4
import config
import pathlib
import random
import click

from jinja2 import Environment, select_autoescape

from pathvalidate import sanitize_filename, validate_filepath


from marshmallow import Schema, fields
from marshmallow_dataclass import class_schema

from rich.console import Console
from rich.progress import track, Progress
from rich.traceback import install
install(show_locals=True)


# TODO
# Changing names will lead to duplicate notes, could filter them by searching for duplicate GUIDS (this would be slow) or storing a table somewhere with a list of notes matched to GUIDs
# Dedup command, will search through the given notes folder and remove duplicates by checking GUIDs, the folders with duplicate GUIDs and the correct name will be kept


def load_yaml_config(file: pathlib.Path) -> config.Map:
    return config.Map.Schema().load(yaml.load(file.read_bytes(), Loader=FullLoader))


def save_yaml_config(file: pathlib.Path, map_data: config.Map):
    file.write_text(yaml.dump(data=config.Map.Schema().dump(obj=map_data)))


def load_json_config(file: pathlib.Path) -> config.Map:
    return config.Map.Schema().loads(file.read_text())


def save_json_config(file: pathlib.Path, map_data: config.Map):
    file.write_text(json.dumps(
        config.Map.Schema().dump(obj=map_data), indent=2))


def smart_load_config(file: pathlib.Path) -> config.Map:
    file = file.resolve()
    extension = file.parts[-1].rsplit('.')[-1]
    if extension == "yaml" or extension == "yml":
        console.print("loading yaml config")
        return load_yaml_config(file)
    elif extension == "json":
        console.print("loading json config")
        return load_json_config(file)
    else:
        raise FileError(file, "Could not determine file type")


def smart_save_config(file: pathlib.Path, map: config.Map):
    file = file.resolve()
    extension = file.parts[-1].rsplit('.')[-1]
    if extension == "yaml" or extension == "yml":
        return save_yaml_config(file=file, map_data=map)
    elif extension == "json":
        return save_json_config(file=file, map_data=map)
    raise FileError(file, "Could not determine file type")


def generate_guid() -> str:
    return str(uuid4()).replace('-', '')


console = Console()

env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)


def do_dry_run(data: config.Map, languages: List[str], notes_folder: pathlib.Path):
    notes_folder = notes_folder.resolve()
    if not notes_folder.exists():
        console.print(f"Creating folder {notes_folder}")

    with Progress() as progress:

        note_task = progress.add_task(
            "generating notes...", total=len(data.notes))

        for note in data.notes:
            if note.id == None:
                progress.console.print(
                    f'WARNING! "{note.name}" does not have an ID specified', style="bold red")
                # note.id = random.randrange(10000, 65536)
                # console.print(
                #     f"It has been randomly assigned the ID {note.id}. You should change this.")
            name = sanitize_filename(note.name.strip().replace(" ", "_"))
            if not (pathlib.Path(notes_folder, name).exists()):
                progress.console.print(
                    f"Note dir at {pathlib.Path(notes_folder, name)}")
                # os.mkdir(pathlib.Path(notes_folder, name))
            if not note.guid:
                # note.guid = generate_guid()
                progress.console.print(
                    f"{note.name} would have a GUID generated")
            progress.console.print(
                f"Generating file {pathlib.Path(notes_folder, name, f'{name}.dat')}")
            # pathlib.Path(notes_folder, name, f"{name}.dat").write_text(
            #     template.render(note=note, length=len(note.text[1].text)))

            for lang in note.text:
                if lang.language in languages:
                    progress.console.print(
                        f"Generating file {pathlib.Path(notes_folder, name, f'{lang.language}.dat')}")
                else:
                    progress.console.print(f"skipping {lang.language} ")
                # pathlib.Path(notes_folder, name, f"{lang.language}.dat").write_text(
                #     lang_template.render(language=lang, name=note.name))
            progress.update(note_task, advance=1)
    return


@click.command()
@click.option('-c', '--config', help="Specify the notes config file to use. Must be yml or json", default=pathlib.Path("./map.yml"), type=click.Path(file_okay=True, dir_okay=False, readable=True, writable=True, exists=True, path_type=pathlib.Path))
@click.option('-l', '--language', '--lang', help="Specify the languages to build notes for.", show_default=True, default=["english"], multiple=True)
@click.option('-d', '--dry-run', default=False, is_flag=True, help="Don't create notes files. Usefull to check what will be created and where.")
@click.argument('folderpath', type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=pathlib.Path))
def build(config: pathlib.Path, language: List, dry_run: bool, folderpath: pathlib.Path):
    # check to ensure path is not problematic
    try:
        validate_filepath(folderpath.resolve(), platform='auto')
    except ValidationError as err:
        console.print("Invalid path to notes folder", style="bold red")
        console.print(err, style="bold red")
        exit(2)

    folderpath = folderpath.resolve()
    config = config.resolve()

    if not (config.exists() and config.is_file):
        console.bell()
        console.print(
            f"Config file \"{config}\" either does not exist, or is a directory!", style="bold red")

    map = smart_load_config(config)

    template = env.get_template("note.dat")
    lang_template = env.get_template("language.dat")

    if dry_run:
        console.print("Doing a dry run...", style='bold')
        do_dry_run(data=map, languages=language, notes_folder=folderpath)
        exit(0)

    if not folderpath.exists():
        folderpath.mkdir()

    console.print(f"Building notes in {folderpath}")
    with Progress() as progress:

        note_task = progress.add_task(
            "generating notes...", total=len(map.notes))

        for note in map.notes:

            if note.id == None:
                progress.console.print(
                    f'WARNING! "{note.name}" does not have an ID specified', style="bold red")
                note.id = random.randrange(10000, 65535)
                progress.console.print(
                    f"It has been randomly assigned the ID {note.id}. You should change this.")
            if note.id > 65535:
                progress.console.print(
                    f'WARNING! "{note.name}" has and ID greater than that allowed by unturned', style="bold red")
            elif note.id < 2000:
                progress.console.print(
                    f'WARNING! "{note.name}" has an ID less than the recommended minumum', style="bold red")

            # Get a safe file name from the notes name
            name = sanitize_filename(note.name.strip().replace(" ", "_"))
            note_path = pathlib.Path(folderpath, name)

            if not (note_path.exists()):
                note_path.mkdir()

            if not note.guid:
                note.guid = generate_guid()

            pathlib.Path(note_path, f"{name}.dat").write_text(
                template.render(note=note, length=len(note.text[1].text)))

            for lang in note.text:
                if lang.language in language:
                    pathlib.Path(note_path, f"{lang.language}.dat").write_text(
                        lang_template.render(language=lang, name=note.name))
            progress.update(note_task, advance=1)

    console.log("saving config file")
    smart_save_config(map=map, file=config)
