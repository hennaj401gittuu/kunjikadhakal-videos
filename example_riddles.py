# Build to Survive - long-form pilot: riddle compilation
import math
FORMAT = "long"
SKY = "#2F8FCB"
TITLE_TEXT = "Can You Survive These 15 Riddles?"

L, M, R = (2.2, 7.8), (5.0, 5.0), (7.8, 2.2)       # option spots: left, middle, right on screen
SPOTS = [L, M, R]
WORDS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve", "thirteen", "fourteen", "fifteen"]


def opts(h=2.2, spots=None):
    """Option markers float at height h (put them above the tallest object)."""
    return [option(n + 1, p[0], p[1], h) for n, p in enumerate(spots or SPOTS)]


def flat(xs):
    out = []
    for x in xs:
        out += flat(x) if isinstance(x, (list, tuple)) else [x]
    return out


def base(style="grass", extra=()):
    return [ground(0, 0, 10, 10, style, depth=2.2), sun(), clouds(3)] + flat(extra)


def hut(x, y, z=0.0, wall="#E9C990", roofc="#C0392B", id=None):
    return [box(x - 0.8, y - 0.8, z, 1.6, 1.6, 1.2, color=wall), roof(x - 0.8, y - 0.8, z + 1.2, 1.6, 1.6, 0.8, color=roofc, style="gable_x")]


def stilts(x, y, h):
    return [cyl(x + dx, y + dy, 0, 0.09, h, color="#8D6E4A") for dx in (-0.7, 0.7) for dy in (-0.7, 0.7)]


def tent(x, y, door="x", color="#E67E22"):
    out = [roof(x - 0.9, y - 0.6, 0, 1.8, 1.2, 1.1, color=color, style="gable_x", over=0)]
    if door == "x":
        out.append(poly([(x + 0.9, y - 0.25, 0), (x + 0.9, y + 0.25, 0), (x + 0.9, y, 0.75)], "#4A2F1C"))
    else:
        out.append(poly([(x - 0.3, y + 0.6, 0), (x + 0.3, y + 0.6, 0), (x + 0.3, y + 0.3, 0.55), (x - 0.3, y + 0.3, 0.55)], "#4A2F1C"))
    return out


def fire(x, y, good=True, wet=False):
    out = []
    if good:
        out += [rock(x + 0.55 * math.cos(a), y + 0.55 * math.sin(a), 0, 0.35, color="#7F8C8D") for a in [k * 0.9 for k in range(7)]]
    out += [cone(x, y, 0, 0.35, 0.55, color="#8D6E4A")]
    if not wet:
        out += [cone(x, y, 0.15, 0.28, 0.75, color="#F39C12"), cone(x, y, 0.2, 0.16, 0.55, color="#FFD54F")]
    else:
        out += [water(x - 0.8, y - 0.8, 0.01, 1.6, 1.6, color="#5D8AA8")]
    return out


def riddle(n, question, setup_line, scene, reveal_line, ans_pt, rr=1.0, extra_reveal=(), style="grass", sky_fx=(), h=2.4, spots=None):
    """card -> scene + question -> 7 s timer -> answer."""
    return [
        beat(f"Riddle number {WORDS[n - 1]}.", card(f"RIDDLE {n}", [], style="sky"), cut=True),
        beat(setup_line, *base(style, list(sky_fx) + scene), qbar(question), *opts(h, spots), score(f"{n} / 15"), cut=True),
        beat("You have ten seconds.", timer(10), hold=10.0),
        beat(reveal_line, reveal(*ans_pt, r=rr), *extra_reveal),
    ]


B = [
    beat("Fifteen survival riddles. Out in the wild, one wrong choice can cost you everything. Count how many you get right.",
         card("CAN YOU SURVIVE?", ["15 survival riddles", "10 seconds each", "Count your correct answers"], style="dark")),
]

# 1 - which path leads to water
B += riddle(1, "Which path leads to water?",
    "You're lost in the desert with an empty bottle. Three paths lead away from camp. Only one ends at water.",
    [poly([(0.5, 9.5, 0.01), (1.2, 9.5, 0.01), (2.6, 7.4, 0.01), (2.0, 7.2, 0.01)], "#C9A66C"),
     poly([(4.6, 9.5, 0.01), (5.3, 9.5, 0.01), (5.3, 5.4, 0.01), (4.7, 5.4, 0.01)], "#C9A66C"),
     poly([(7.8, 9.5, 0.01), (8.4, 9.4, 0.01), (8.2, 2.6, 0.01), (7.6, 2.6, 0.01)], "#C9A66C"),
     cone(2.2, 7.8, 0, 0.6, 1.4, color="#B4874E"), rock(1.6, 7.0, 0, 0.7, color="#B4874E"),
     tree(4.6, 4.6, 0, 0.8, "palm"), tree(5.6, 4.4, 0, 0.7, "palm"), tree(5.3, 5.7, 0, 0.5, "bush"),
     critter(5.0, 4.0, 3.2, 0.9, "bird", color="#34495E", n=3, spread=0.8),
     cone(7.6, 2.0, 0, 0.3, 1.2, color="#7CB342"), cone(8.3, 2.5, 0, 0.25, 0.9, color="#7CB342")],
    "Path two. Green palm trees only grow where there's water underground, and birds fly toward water to drink.",
    (5.0, 5.0, 1.5), rr=1.4, style="desert", h=3.6)

# 2 - flood shelter
B += riddle(2, "Which hut survives the flood?",
    "Heavy rain is coming, and the river always floods in this season. Three families built three huts.",
    [water(0, 0, 0.02, 10, 1.4, color="#3FA7E0"), water(0, 0, 0.02, 1.4, 10, color="#3FA7E0")]
    + hut(2.2, 7.8) + stilts(5.0, 5.0, 1.6) + hut(5.0, 5.0, z=1.6, roofc="#2E86C1") + hut(7.8, 2.2, roofc="#27AE60")
    + [tree(7.0, 1.4, 0, 0.9, "round")],
    "Hut two. It stands on stilts, so floodwater flows underneath it. The others sit right on the riverbank.",
    (5.0, 5.0, 2.2), rr=1.5, sky_fx=[fx("rain")], h=4.6)

# 3 - who is lying (wet / dry)
B += riddle(3, "Who is lying?",
    "Three hikers reach camp. Each one says: I just swam across the river to get here. One of them is lying.",
    [water(0, 0, 0.02, 10, 1.6, color="#3FA7E0"),
     person(2.2, 7.8, 0, 1.7, jacket="#E74C3C", wet=True),
     person(5.0, 5.0, 0, 1.7, jacket="#27AE60", hat="cap", wet=False),
     person(7.8, 2.2, 0, 1.7, jacket="#8E44AD", backpack=True, wet=True),
     tent(4.0, 8.0, color="#F39C12")],
    "Hiker two. Anyone who just swam across a river would be dripping wet. His clothes are completely dry.",
    (5.0, 5.0, 1.0), rr=1.0, h=3.6)

# 4 - safe rope bridge: the gorge runs away from the camera, bridges cross it left-to-right on screen
def bridge(c, snapped=False):
    left, right = (c - 1.6, c + 1.6), (c + 1.6, c - 1.6)
    out = []
    for off in (-0.22, 0.22):
        a_ = (left[0] + off, left[1] + off, 0.75); m_ = (c + off, c + off, 0.0); b_ = (right[0] + off, right[1] + off, 0.75)
        if snapped and off > 0:
            out.append(line3([a_, (c - 0.5 + off, c + 0.5 + off, 0.15), (c - 0.35 + off, c + 0.35 + off, -1.4)], "#5D4037", 5))
        else:
            out.append(line3([a_, m_, b_], "#5D4037", 5))
    out.append(line3([(left[0], left[1], 0.3), (c, c, -0.35), (right[0], right[1], 0.3)], "#BCAAA4", 18))
    return out


B += riddle(4, "Which bridge is safe?",
    "You must cross a deep gorge. There are three old rope bridges. Look closely at how each one is tied.",
    [poly([(1, 0, 0.02), (10, 9, 0.02), (10, 10, 0.02), (9, 10, 0.02), (0, 1, 0.02), (0, 0, 0.02)], "#2C1E16")]
    + bridge(2.0) + [tree(2.0 - 1.9, 2.0 + 1.9, 0, 0.7, "round"), tree(2.0 + 1.9, 2.0 - 1.9, 0, 0.7, "round")]
    + bridge(5.0) + [tree(5.0 - 1.9, 5.0 + 1.9, 0, 0.7, "round"), rock(5.0 + 1.75, 5.0 - 1.75, 0, 0.5, color="#BDC3C7")]
    + bridge(8.0, snapped=True) + [tree(8.0 - 1.9, 8.0 + 1.9, 0, 0.7, "round"), tree(8.0 + 1.9, 8.0 - 1.9, 0, 0.7, "round")],
    "Bridge one. Bridge two is tied to a tiny loose rock, and bridge three has a snapped rope hanging down.",
    (2.0, 2.0, 0.0), rr=1.9, h=1.4, spots=[(0.3, 3.7), (3.3, 6.7), (6.3, 9.7)])

# 5 - tent facing the wind
B += riddle(5, "Which tent stays warm tonight?",
    "A cold wind is blowing hard from the right. Three campers pitched their tents. Look at the doors.",
    tent(2.2, 7.8, door="y", color="#E67E22") + tent(5.0, 5.0, door="x", color="#27AE60") + tent(7.8, 2.2, door="x", color="#2E86C1")
    + [arrows([(11.5, 4.0, 1.2), (8.0, 4.4, 1.0)], "#FFFFFF", 9, id="w1"), arrows([(11.5, 0.5, 0.9), (9.2, 1.6, 0.9)], "#FFFFFF", 9, id="w2")],
    "Tent one. Its door faces away from the wind. The other two doors face straight into it, so the wind blows right inside.",
    (2.2, 7.8, 0.6), rr=1.2, sky_fx=[fx("wind")])

# 6 - safe water
B += riddle(6, "Which water is safest to drink?",
    "Your bottle is empty again. Three water sources: a still green pond, a fast stream over rocks, and the sea.",
    [water(1.0, 6.8, 0.02, 2.4, 2.4, color="#7A9A3A"), critter(2.4, 7.6, 0.02, 0.6, "insect", color="#2C3E50", n=4, spread=0.8),
     water(4.4, 2.0, 0.02, 1.2, 6.0, color="#3FA7E0"), rock(4.6, 3.0, 0, 0.6), rock(5.3, 4.3, 0, 0.5), rock(4.7, 6.6, 0, 0.55),
     arrows([(5.0, 2.2, 0.1), (5.0, 7.8, 0.1)], "#CDEFFF", 6, id="flow"),
     water(6.6, 0, 0.02, 3.4, 3.6, color="#1F618D")],
    "The stream. Moving water carries fewer germs than a still pond, and salty sea water makes you thirstier. Still boil it if you can.",
    (5.0, 5.0, 0.3), rr=1.3)

# 7 - campfire
B += riddle(7, "Which fire keeps burning?",
    "Night is coming and it's getting cold. Three people try to build a fire. Only one will last until morning.",
    fire(2.2, 7.8, good=False, wet=True) + fire(5.0, 5.0, good=True) + [rock(5.9, 4.0, 0, 1.1, color="#7F8C8D")]
    + fire(7.8, 2.2, good=False) + [arrows([(11.5, 0.8, 1.0), (8.8, 1.8, 0.9)], "#FFFFFF", 9, id="gust")],
    "Fire two. It has a ring of stones, sits on dry ground, and a big rock blocks the wind. Fire one is in a puddle, and fire three is in the open wind.",
    (5.0, 5.0, 0.4), rr=1.1, sky_fx=[fx("night")])

# 8 - which trail reaches camp
B += riddle(8, "Which trail reaches the camp?",
    "Three trails start at the bottom. Follow them with your eyes. Which one actually reaches the tent?",
    [line3([(2.2, 9.6, 0.02), (3.5, 7.0, 0.02), (6.5, 6.8, 0.02), (8.6, 4.2, 0.02), (8.2, 1.2, 0.02)], "#8E44AD", 9),
     line3([(5.0, 9.6, 0.02), (4.0, 7.2, 0.02), (2.0, 5.0, 0.02), (2.6, 2.0, 0.02), (4.6, 1.0, 0.02)], "#E67E22", 9),
     line3([(7.8, 9.6, 0.02), (6.4, 7.8, 0.02), (5.0, 5.0, 0.02), (6.0, 3.0, 0.02), (6.6, 2.4, 0.02)], "#2E86C1", 9)]
    + tent(8.2, 1.0, color="#27AE60") + [tree(4.8, 0.8, 0, 0.9, "pine"), rock(6.7, 2.2, 0, 1.8)],
    "Trail one, the purple one. The orange trail ends at a tree, and the blue trail ends at a big rock.",
    (8.2, 1.2, 0.5), rr=1.3, h=0.9, spots=[(2.2, 9.6), (5.0, 9.6), (7.8, 9.6)])

# 9 - packed for the desert
B += riddle(9, "Who packed right for the desert?",
    "Three friends are about to walk across the desert. Only one of them is ready for the heat.",
    [person(2.2, 7.8, 0, 1.7, jacket="#2C3E50", pants="#1B2631"),
     person(5.0, 5.0, 0, 1.7, jacket="#F5E6C8", pants="#D9B77A", hat="straw", backpack=True),
     person(7.8, 2.2, 0, 1.7, jacket="#E74C3C", pants="#3498DB", pose="cheer")],
    "Friend two. A wide hat and light-coloured clothes keep the sun off, and the backpack carries water. Dark clothes soak up heat.",
    (5.0, 5.0, 1.0), rr=1.0, style="desert", sky_fx=[fx("heat")], h=3.6)

# 10 - lightning
B += riddle(10, "Where is it least dangerous in a lightning storm?",
    "A thunderstorm catches you in the open with no buildings or cars around. Where should you be?",
    [tree(2.2, 7.4, 0, 1.4, "round"), person(2.6, 8.0, 0, 1.5, jacket="#E74C3C"),
     box(3.8, 3.8, 0, 2.4, 2.4, 1.8, color="#6BBF4E", top="#7CCB5C"), person(5.0, 5.0, 1.8, 1.5, jacket="#2E86C1", pose="cheer"),
     person(7.8, 2.2, 0, 1.2, jacket="#27AE60", pose="sit")],
    "Spot three. Crouch low on open ground, away from tall things. Lightning strikes the tallest point: the lone tree and the hilltop.",
    (7.8, 2.2, 0.4), rr=1.0, sky_fx=[fx("rain"), fx("night")], h=5.4)

# 11 - bear-proof camp
B += riddle(11, "Which camp is safe from bears?",
    "You're camping in bear country. Three campers stored their food in three different ways.",
    tent(2.2, 7.8, color="#E67E22") + [box(1.0, 7.4, 0, 0.5, 0.5, 0.4, color="#C0392B")]
    + tent(5.0, 5.0, color="#27AE60") + [tree(4.2, 6.2, 0, 1.2, "pine"), tree(6.2, 4.0, 0, 1.2, "pine"),
       line3([(4.2, 6.2, 3.0), (5.2, 5.2, 2.6), (6.2, 4.0, 3.0)], "#8D6E4A", 3), box(5.0, 5.0, 2.0, 0.4, 0.4, 0.5, color="#C0392B")]
    + tent(7.8, 2.2, color="#2E86C1") + [box(8.9, 2.0, 0, 0.5, 0.5, 0.4, color="#C0392B"),
       critter(9.0, 0.6, 0, 1.6, "quadruped", color="#5D4037", face=-1)],
    "Camp two. The food hangs high between two trees, out of reach. Food left on the ground brings bears right to your tent.",
    (5.0, 5.0, 2.2), rr=0.9, h=4.2)

# 12 - sandbag wall
B += riddle(12, "Which sandbag wall holds back the flood?",
    "Floodwater is rising toward the village. Three teams built sandbag walls with the same number of bags.",
    [water(0, 0, 0.05, 10, 1.4, color="#3FA7E0"),
     box(1.2, 7.0, 0, 2.0, 0.4, 1.8, color="#C9A66C"),
     box(4.0, 4.4, 0, 2.0, 1.2, 0.5, color="#C9A66C"), box(4.0, 4.6, 0.5, 2.0, 0.8, 0.5, color="#BFA060"), box(4.0, 4.8, 1.0, 2.0, 0.4, 0.4, color="#C9A66C"),
     box(6.8, 1.8, 0, 2.0, 0.6, 0.6, color="#C9A66C")],
    "Wall two. It's shaped like a pyramid: wide at the bottom, narrow at the top. A tall thin wall tips over, and a low wall gets washed over.",
    (5.0, 5.0, 0.6), rr=1.4)

# 13 - snow shelter
B += riddle(13, "Which shelter is warmest in a blizzard?",
    "A blizzard traps you on a snowy mountain overnight. Three shelters. Which one keeps you warmest?",
    tent(2.2, 7.8, color="#E74C3C")
    + [cone(5.0, 5.0, 0, 1.4, 1.6, color="#EAF2F8"), poly([(5.6, 5.95, 0), (6.3, 5.55, 0), (6.1, 5.4, 0.55), (5.7, 5.7, 0.6)], "#34495E"),
       box(7.0, 1.6, 0, 1.6, 0.2, 1.2, color="#8D6E4A"), box(7.0, 1.6, 0, 0.2, 1.4, 0.8, color="#8D6E4A")],
    "The snow cave. Snow is full of trapped air, so it blocks the wind and holds in your body heat. A thin tent loses heat fast.",
    (5.0, 5.0, 0.8), rr=1.5, style="snow", sky_fx=[fx("snow")], h=2.8)

# 14 - rescue signal
B += riddle(14, "Where will rescuers see you?",
    "A rescue helicopter is searching for you. You build a big S O S out of rocks. Where should you put it?",
    [tree(1.4, 7.0, 0, 1.0, "pine"), tree(2.6, 8.4, 0, 1.0, "pine"), tree(2.0, 6.2, 0, 1.0, "pine"), tree(3.0, 7.4, 0, 0.9, "pine"),
     rock(2.2, 7.8, 0, 0.3, color="#ECF0F1"),
     rock(4.4, 4.8, 0, 0.35, color="#ECF0F1"), rock(4.8, 4.4, 0, 0.35, color="#ECF0F1"), rock(5.2, 5.0, 0, 0.35, color="#ECF0F1"),
     rock(5.4, 5.6, 0, 0.35, color="#ECF0F1"), rock(5.8, 5.2, 0, 0.35, color="#ECF0F1"),
     box(7.0, 1.0, 0, 2.2, 1.6, 1.8, color="#7F8C8D"), poly([(9.2, 1.6, 0), (9.2, 2.4, 0), (9.2, 2.4, 1.0), (9.2, 1.6, 1.0)], "#1C2833")],
    "Spot two, the open clearing. From the sky, trees hide everything underneath them, and a cave hides you completely.",
    (5.0, 5.0, 0.2), rr=1.4, h=3.2)

# 15 - rain collector
B += riddle(15, "Which collects the most rainwater?",
    "Rain is finally falling, and you need drinking water. Three ways to catch it. Which one fills up fastest?",
    [cyl(2.2, 7.8, 0, 0.18, 0.4, color="#ECF0F1"),
     poly([(3.6, 3.6, 1.4), (6.4, 3.6, 1.4), (6.4, 6.4, 1.4), (3.6, 6.4, 1.4)], "#2E86C1", outline="#1B4F72"),
     cyl(5.0, 5.0, 0, 0.45, 0.8, color="#95A5A6"), line3([(5.0, 5.0, 1.4), (5.0, 5.0, 0.8)], "#2E86C1", 6),
     cyl(7.8, 2.2, 0, 0.22, 0.6, color="#A9CCE3")],
    "The tarp. It catches rain from a big area and funnels it all into one bucket. A cup or a bottle only catches what falls into its tiny opening.",
    (5.0, 5.0, 1.0), rr=1.5, sky_fx=[fx("rain")], h=2.4)

B += [
    beat("So, how many did you get right? Zero to five, you'd be lost. Six to ten, you're a survivor. Eleven or more, you're a survival expert. Tell us your score in the comments.",
         card("HOW MANY DID YOU GET?", ["0-5:  Lost in the wild", "6-10:  Survivor", "11-15:  Survival expert", "Comment your score!"], style="dark"), cut=True),
]
