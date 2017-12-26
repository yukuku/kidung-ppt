# converted from java 20141126
# converted py2 to py3 20171226

import re

abbrs = [
    "Gen",
    "Exod",
    "Lev",
    "Num",
    "Deut",
    "Josh",
    "Judg",
    "Ruth",
    "1Sam",
    "2Sam",
    "1Kgs",
    "2Kgs",
    "1Chr",
    "2Chr",
    "Ezra",
    "Neh",
    "Esth",
    "Job",
    "Ps",
    "Prov",
    "Eccl",
    "Song",
    "Isa",
    "Jer",
    "Lam",
    "Ezek",
    "Dan",
    "Hos",
    "Joel",
    "Amos",
    "Obad",
    "Jonah",
    "Mic",
    "Nah",
    "Hab",
    "Zeph",
    "Hag",
    "Zech",
    "Mal",
    "Matt",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Rom",
    "1Cor",
    "2Cor",
    "Gal",
    "Eph",
    "Phil",
    "Col",
    "1Thess",
    "2Thess",
    "1Tim",
    "2Tim",
    "Titus",
    "Phlm",
    "Heb",
    "Jas",
    "1Pet",
    "2Pet",
    "1John",
    "2John",
    "3John",
    "Jude",
    "Rev",
]


def abbrToKitab0(abbr):
    for i, abbr in enumerate(abbrs):
        if abbr == abbrs[i]: return i

    raise ValueError("abbr not found: " + abbr)


def verifyMultiOsis(line):
    items = re.split(r'\s*;\s*', line)
    for item in items:
        # may have "-"
        osisIds = re.split(r'\s*-\s*', item)
        if len(osisIds) != 1 and len(osisIds) != 2:
            raise ValueError("line invalid: " + line)

        for osisId in osisIds:
            parts = re.split(r'\.', osisId)
            if len(parts) != 2 and len(parts) != 3:
                raise ValueError("osisId invalid: " + osisId + " in " + line)

            bookName = parts[0]
            chapter_1 = int(parts[1])
            verse_1 = 0 if len(parts) < 3 else int(parts[2])

            bookId = abbrToKitab0(bookName)  # throws RunEx when fails


def getTokenPertama(baris):
    token = re.split(r"\s+", baris, maxsplit=1)
    return token[0]


def getTokenKedua(baris):
    token = re.split(r"\s+", baris, maxsplit=1)
    return token[1]


def parse_book_content(content):
    xlagu = []  # new ArrayList<Song>()

    # init
    song = {}  # new Song()
    modeLirik = False
    nobaitTerakhir = 0
    song['lyrics'] = []  # new ArrayList<Lyric>()
    lyric = None
    xlagu.append(song)
    verse = None  # new ketika ketemu *

    bariske = 0
    for baris in content.splitlines():
        bariske += 1

        baris = baris.strip()
        if not len(baris): continue
        if baris.startswith("//"): continue

        if not modeLirik:
            if song not in xlagu:
                xlagu.append(song)

            tokenPertama = getTokenPertama(baris)
            if tokenPertama == "no" or tokenPertama == 'code':
                song['code'] = getTokenKedua(baris)
            elif tokenPertama == "judul" or tokenPertama == 'title':
                song['title'] = getTokenKedua(baris)
            elif tokenPertama == "judul_asli" or tokenPertama == 'title_original':
                song['title_original'] = getTokenKedua(baris)
            elif tokenPertama == "tune":
                song['tune'] = getTokenKedua(baris)
            elif tokenPertama == "lirik" or tokenPertama == 'authors_lyric':
                lirik_s = getTokenKedua(baris)
                xlirik = re.split(r';\s*', lirik_s)
                song['authors_lyric'] = xlirik
            elif tokenPertama == "musik" or tokenPertama == 'authors_music':
                musik_s = getTokenKedua(baris)
                xmusik = re.split(r';\s*', musik_s)
                song['authors_music'] = xmusik
            elif tokenPertama == "ayat" or tokenPertama == 'scriptureReferences':
                val = getTokenKedua(baris)
                verifyMultiOsis(val)  # throws RunEx when fails
                song['scriptureReferences'] = val
            elif tokenPertama == "tempo":
                print("ignored: {}".format(baris))
            else:
                if re.match(r"[1-7]=[ABCDEFG](is|s|es)?(, [1-7]=[ABCDEFG](is|s|es)?)*", baris):
                    song['keySignature'] = baris
                elif re.match(r"([0-9]+/[0-9]+,\s*)*[0-9]+/[0-9]+", baris):
                    song['timeSignature'] = baris
                elif baris.startswith("*"):
                    modeLirik = True
                else:
                    raise ValueError("baris " + str(bariske) + " ga dikenal: " + baris)

        # ga boleh pake else
        if modeLirik:
            if baris.startswith("=="):
                song = {'lyrics': []}
                lyric = None  # init again, because this is a new song
                nobaitTerakhir = 0
                modeLirik = False
            else:
                if baris.startswith("*version") or baris.startswith("*versi"):  # explicit new lyric
                    if baris.startswith("*version"):
                        caption = baris[8:].strip()
                    else:
                        caption = baris[6:].strip()
                    if not len(caption): caption = None

                    lyric = {'caption': caption, 'verses': []}  # new Lyric()
                    song['lyrics'].append(lyric)
                    nobaitTerakhir = 0
                elif baris.startswith("*reff") or baris.startswith("*ref"):
                    if lyric is None:  # suddenly this, without explicit new lyric
                        lyric = {'verses': []}  # new Lyric()
                        song['lyrics'].append(lyric)

                    verse = {}  # new Verse()
                    lyric['verses'].append(verse)
                    verse['lines'] = []  # new ArrayList<String>()

                    if baris == '*reff' or baris == '*ref':  # no explicit ordering
                        ordering = 1
                    else:
                        if baris.startswith('*reff'):
                            ordering = int(baris[5:])
                        else:  # starts with '*ref'
                            ordering = int(baris[4:])

                    verse['kind'] = 'VerseKind.REFRAIN'
                    verse['ordering'] = ordering
                elif baris.startswith("*text"):
                    if lyric is None:  # suddenly this, without explicit new lyric
                        lyric = {'verses': []}  # new Lyric()
                        song['lyrics'].append(lyric)

                    verse = {}  # new Verse()
                    lyric['verses'].append(verse)
                    verse['lines'] = []  # new ArrayList<String>()

                    if len(baris) == 5:
                        ordering = 1
                    else:
                        ordering = int(baris[5:])

                    verse['kind'] = 'VerseKind.TEXT'
                    verse['ordering'] = ordering
                elif baris.startswith("*"):
                    if lyric is None:  # suddenly this, without explicit new lyric
                        lyric = {'verses': []}  # new Lyric()
                        song['lyrics'].append(lyric)

                    no = int(baris[1:])

                    # create a new lyric *automatically* if the current verse number is lesser or equal to
                    # the last verse number
                    if no <= nobaitTerakhir:
                        lyric = {'verses': []}  # new Lyric()
                        song['lyrics'].append(lyric)

                    verse = {}  # new Verse()
                    lyric['verses'].append(verse)
                    verse['lines'] = []  # new ArrayList<String>()
                    verse['kind'] = 'VerseKind.NORMAL'
                    verse['ordering'] = no
                    nobaitTerakhir = no
                else:
                    # lirik normal
                    verse['lines'].append(baris)

    return xlagu


def parse_infos_content(content):
    lines = content.splitlines()
    books = {}  # key: book name, value: info
    book_info = None

    for line in lines:
        line = line.strip()

        if not line: continue

        if line.startswith('=='):
            if book_info: books[book_info['name']] = book_info
            book_info = None

        else:
            if book_info is None:
                book_info = {}

            tokenPertama = getTokenPertama(line)
            if tokenPertama == 'name':
                book_info['name'] = getTokenKedua(line)
            elif tokenPertama == 'title':
                book_info['title'] = getTokenKedua(line)
            elif tokenPertama == 'copyright':
                book_info['copyright'] = getTokenKedua(line)
            elif tokenPertama == 'groups':
                book_info['groups'] = getTokenKedua(line).split(',')
            else:
                raise ValueError('unknown command in line: ' + line)

    # last one
    if book_info: books[book_info['name']] = book_info

    return books
