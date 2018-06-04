import ast
import itertools
import json
import os
import shutil

import requests
from apikey import APIKEY, APIURL


def main():
    deleted_bytes = 0
    files = len(os.listdir("."))
    index = 0
    ids = dict()
    dupes = dict()
    missings = set()
    for i in os.listdir("."):
        song_id = "".join(itertools.takewhile(lambda a: a.isdigit(), i))
        if not song_id:
            continue
        if song_id:
            if song_id in ids:
                # Structure: Dictionary of SongIDs with values of (Dictionary of filenames with values of booleans)
                # Boolean contains the value whether all files were there or not
                dupe_dict = dupes.setdefault(song_id, dict())
                dupe_dict[i] = False
                dupe_dict[ids[song_id]] = False
            else:
                ids[song_id] = i
    try:
        for i in os.listdir("."):
            is_dupe = False
            song_id = "".join(itertools.takewhile(lambda a: a.isdigit(), i))
            if song_id in dupes:
                is_dupe = True
            index += 1
            if index % 50 == 0:
                print(f"{index}/{files}: So far, {deleted_bytes} bytes have been deleted")
            if os.path.isdir(i):
                d, f = process_song(i, is_dupe)
                if is_dupe:
                    dupes[song_id][i] = f
                elif not f:
                    missings.add(song_id)
                deleted_bytes += d
        if dupes:
            print("Getting rid of duplicates")
            for song_id in dupes:
                this_song = dupes[song_id]
                to_delete_list = [dd for dd in this_song if not this_song[dd]]
                if len(to_delete_list) == len(this_song):
                    missings.add(song_id)
                    to_delete_list = to_delete_list[1:]
                if not to_delete_list:
                    to_delete_list += list(this_song.keys())[1:]
                for to_delete in to_delete_list:
                    total_size = 0
                    for dirpath, dirnames, filenames in os.walk(to_delete):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            total_size += os.path.getsize(fp)
                    shutil.rmtree(to_delete)
                    deleted_bytes += total_size
        if missings:
            session = requests.session()
            print("Re-Downloading ranked beatmaps with missing assets")
            for i in missings:
                response = session.get(APIURL + "get_beatmaps", params={'k': APIKEY, "s": i})
                if response.status_code != 200:
                    print(f"API responded with {response.status_code}")
                    text = response.text.splitlines()
                    if len(text) < 10:
                        print(*text, sep="\n")
                    else:
                        print("Response text won't be printed because it's big")
                    break
                else:
                    beatmapset = json.loads(response.text, encoding="utf-8")
                    if beatmapset[0]['approved'] != '1':
                        print(f"Skipping {i} because it's not ranked")
                        continue
                os.startfile(f"https://osu.ppy.sh/beatmapsets/{i}/download?noVideo=1")
            print("Make sure to de-dupe again, just in case")
    finally:
        print(f"In the end, {deleted_bytes} bytes were deleted")
        print(f"We ended on {i}")


def process_song(song_folder, is_dupe=False):
    files_to_keep = []
    for i in os.listdir(song_folder):
        if i.endswith(".osu"):
            files_to_keep += [i] + get_osu_files(song_folder, i)
    for f in files_to_keep[:]:
        if not f:
            continue
        while "/" in f:
            index = f.find("/")
            f = f[index + 1:]
        files_to_keep.append(f)
    files_to_keep = [i.lower() if i else None for i in files_to_keep]
    deleted_bytes = 0
    files_found = set([i for i in files_to_keep[:] if i])
    for path, dirs, names in os.walk(song_folder):
        for name in names:
            if name.lower() not in files_to_keep:
                file_path = os.path.join(path, name)
                deleted_bytes += os.path.getsize(file_path)
                try:
                    os.remove(file_path)
                except:
                    print(f"Was not able to delete {file_path}")
            for i in list(files_found)[:]:
                if i.lower() == name.lower():
                    files_found.remove(i)
    all_files_there = True
    for i in files_found:
        if "/" in i:
            continue
        all_files_there = False
        if not is_dupe:
            print(f"{i} was missing in {song_folder}")
    return deleted_bytes, all_files_there


def get_osu_files(song_folder, osu_file):
    with open(os.path.join(song_folder, osu_file), encoding="UTF-8") as osu:
        lines = osu.readlines()
        background = None
        audio = None
        found_events = False
        for line in lines:
            if line.startswith("AudioFilename: "):
                audio = line[15:-1]
            if found_events:
                try:
                    literal = ast.literal_eval(f"[{line}]")
                    if all(isinstance(i, int) for i in literal[:2]):
                        if isinstance(literal[2], str):
                            background = literal[2]
                            break
                except:
                    continue
            else:
                if line == "[Events]\n":
                    found_events = True
                    continue
        return [background, audio]


if __name__ == "__main__":
    main()
