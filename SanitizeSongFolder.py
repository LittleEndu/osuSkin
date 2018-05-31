import itertools
import os
import shutil


def main():
    deleted_bytes = 0
    files = len(os.listdir("."))
    index = 0
    ids = dict()
    dupes = dict()
    for i in os.listdir("."):
        song_id = "".join(itertools.takewhile(lambda a: a.isdigit(), i))
        if song_id:
            if song_id in ids:
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
                deleted_bytes += d
        if dupes:
            print("Getting rid of duplicates")
            for song_id in dupes:
                assert isinstance(dupes[song_id], dict)
                dict().values()
                to_delete_list = [i for i in dupes[song_id] if not dupes[song_id][i]] + [list(dupes[song_id].keys())[1]]
                to_delete = to_delete_list[0]
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(to_delete):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        total_size += os.path.getsize(fp)
                shutil.rmtree(to_delete)
                deleted_bytes += total_size

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
        files_to_keep.append(f.lower())
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
        if "/" in i or i == i.lower():
            continue
        all_files_there = False
        if not is_dupe:
            print(f"{i} was missin in {song_folder}")
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
                if line.startswith("0,0"):
                    background = "".join(itertools.takewhile(lambda a: a != '"', line[5:]))
                    break
            else:
                if line == "[Events]\n":
                    found_events = True
                    continue
        return [background, audio]


if __name__ == "__main__":
    main()
