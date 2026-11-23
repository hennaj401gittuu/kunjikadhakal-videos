HOOK = ["HE ASKED POLICE ONE QUESTION", "THE ANSWER CAUGHT HIM"]
# Cover image (cover.py): 2-3 huge lines (last line in the accent colour), kicker strip, evidence object, stamp, accent 0-5
COVER = {"lines": ["CAUGHT BY A", "FLOPPY", "DISK"], "kicker": "BTK  \u2022  WICHITA 2005", "obj": "floppy", "tag": "SOLVED", "accent": 3}
S = []
def seg(scene, text, **p): S.append((scene, p, text.strip()))
seg("quote", "For thirty years, a serial killer in Wichita, Kansas, taunted police with letters. Then he asked them one question.", q="“Can I communicate with floppy and not be traced?”", who="BTK, JANUARY 2005")
seg("newspaper", "He told them: if it's safe, place an ad in the newspaper saying, Rex, it will be OK. Police ran the ad. It was a lie.", head="REX, IT WILL BE OK", sub="Classified ad, The Wichita Eagle, January 2005")
seg("evidence", "On February 16th, 2005, a purple floppy disk arrived at a Wichita TV station.", items=[["letter","Package to KSAS-TV"],["photo","Floppy disk, Feb 16, 2005"]])
seg("file", "Investigators checked the hidden data on the disk. The file had been saved on a computer at Christ Lutheran Church, by a user named Dennis.", head="DIGITAL FORENSICS • DISK FILE", lines=["Last saved: Christ Lutheran Church","User account: DENNIS"], status="TRACED")
seg("reveal", "One search showed the church council's president: Dennis Rader. A DNA test confirmed it.", name="DENNIS RADER", info="CHURCH COUNCIL PRESIDENT • WICHITA, KS")
seg("cell", "He was arrested on February 25th, 2005, and sentenced to ten consecutive life terms. Follow for a new solved case every day.", txt="10 LIFE SENTENCES")
