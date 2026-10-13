"""
Damba Royal
Royal Labyrinth Challenge Engine

Founders Era challenge catalog.

Design principles:
- Global accessibility
- Adventure and strategy over school-style mathematics
- Short, replayable challenges
- Server-side answer validation
- Compatible with the existing challenge API
"""

CHALLENGES = [

    # ============================================================
    # ROYAL GATES
    # ============================================================

    {
        "id": "mission-001",
        "title": "The Royal Gate",
        "category": "Royal Gates",
        "description": "One symbol matches the symbol shown above the gates.",
        "instruction": "Choose the gate carrying the matching symbol.",
        "target": "🔺",
        "options": [
            {"id": "1", "label": "Gate I 🔵"},
            {"id": "2", "label": "Gate II 🔺"},
            {"id": "3", "label": "Gate III 🟢"},
        ],
        "correct_answer": "2",
        "time_limit": 60,
        "score": {
            "correct": 50,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 50,
        },
        "xp_correct": 100,
        "tokens_correct": 50,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-007",
        "title": "The Twin Gate",
        "category": "Royal Gates",
        "description": "Only one gate repeats the exact symbol pair.",
        "instruction": "Find the gate with the same symbol pair.",
        "target": "◆ ●",
        "options": [
            {"id": "1", "label": "Gate I ◆ ▲"},
            {"id": "2", "label": "Gate II ● ◆"},
            {"id": "3", "label": "Gate III ◆ ●"},
        ],
        "correct_answer": "3",
        "time_limit": 45,
        "score": {
            "correct": 60,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 40,
        },
        "xp_correct": 110,
        "tokens_correct": 55,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-008",
        "title": "The Silent Gate",
        "category": "Royal Gates",
        "description": "The royal symbol appears once in the sequence.",
        "instruction": "Choose the gate containing the missing symbol.",
        "target": "⭐",
        "options": [
            {"id": "1", "label": "Gate I 🌙"},
            {"id": "2", "label": "Gate II ⭐"},
            {"id": "3", "label": "Gate III ☀️"},
        ],
        "correct_answer": "2",
        "time_limit": 40,
        "score": {
            "correct": 70,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 35,
        },
        "xp_correct": 120,
        "tokens_correct": 60,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    # ============================================================
    # OBSERVATION
    # ============================================================

    {
        "id": "mission-002",
        "title": "The Three Royal Symbols",
        "category": "Observation Chamber",
        "description": "Study the sequence carefully.",
        "instruction": "Which option completes the displayed sequence?",
        "display_sequence": "◆ ● ▲ ◆",
        "options": [
            {"id": "1", "label": "◆"},
            {"id": "2", "label": "●"},
            {"id": "3", "label": "▲"},
        ],
        "correct_answer": "1",
        "time_limit": 45,
        "score": {
            "correct": 55,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 40,
        },
        "xp_correct": 100,
        "tokens_correct": 50,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-004",
        "title": "The Watcher",
        "category": "Observation Chamber",
        "description": "Three gates are displayed. Only one contains the different symbol.",
        "instruction": "Find the gate that is different.",
        "options": [
            {"id": "1", "label": "Gate I ◆"},
            {"id": "2", "label": "Gate II ◆"},
            {"id": "3", "label": "Gate III ●"},
        ],
        "correct_answer": "3",
        "time_limit": 40,
        "score": {
            "correct": 60,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 35,
        },
        "xp_correct": 110,
        "tokens_correct": 55,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-009",
        "title": "The Hidden Difference",
        "category": "Observation Chamber",
        "description": "Most symbols are identical. One is different.",
        "instruction": "Spot the symbol that breaks the pattern.",
        "display_sequence": "● ● ● ▲ ●",
        "options": [
            {"id": "1", "label": "Position 2"},
            {"id": "2", "label": "Position 4"},
            {"id": "3", "label": "Position 5"},
        ],
        "correct_answer": "2",
        "time_limit": 35,
        "score": {
            "correct": 70,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 30,
        },
        "xp_correct": 120,
        "tokens_correct": 60,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    # ============================================================
    # MEMORY
    # ============================================================

    {
        "id": "mission-003",
        "title": "The Memory Chamber",
        "category": "Memory Chamber",
        "description": "Remember the order of the four royal symbols.",
        "instruction": "Which symbol appeared fourth?",
        "memory_sequence": "🟡 🔷 🟣 🟢",
        "options": [
            {"id": "1", "label": "Yellow 🟡"},
            {"id": "2", "label": "Blue Diamond 🔷"},
            {"id": "3", "label": "Purple 🟣"},
            {"id": "4", "label": "Green 🟢"},
        ],
        "correct_answer": "4",
        "time_limit": 45,
        "score": {
            "correct": 65,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 40,
        },
        "xp_correct": 120,
        "tokens_correct": 60,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-010",
        "title": "The Royal Recall",
        "category": "Memory Chamber",
        "description": "A short sequence will test your memory.",
        "instruction": "Which symbol appeared second?",
        "memory_sequence": "🌙 🔥 👁️ ⭐",
        "options": [
            {"id": "1", "label": "Moon 🌙"},
            {"id": "2", "label": "Fire 🔥"},
            {"id": "3", "label": "Eye 👁️"},
            {"id": "4", "label": "Star ⭐"},
        ],
        "correct_answer": "2",
        "time_limit": 40,
        "score": {
            "correct": 70,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 35,
        },
        "xp_correct": 125,
        "tokens_correct": 65,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-011",
        "title": "The Vanishing Symbols",
        "category": "Memory Chamber",
        "description": "Remember the sequence before it disappears.",
        "instruction": "Which symbol appeared third?",
        "memory_sequence": "🔵 ⭐ 🟢 🔺",
        "options": [
            {"id": "1", "label": "Blue 🔵"},
            {"id": "2", "label": "Star ⭐"},
            {"id": "3", "label": "Green 🟢"},
            {"id": "4", "label": "Triangle 🔺"},
        ],
        "correct_answer": "3",
        "time_limit": 35,
        "score": {
            "correct": 75,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 30,
        },
        "xp_correct": 130,
        "tokens_correct": 70,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    # ============================================================
    # STRATEGY
    # ============================================================

    {
        "id": "mission-005",
        "title": "The Strategist",
        "category": "Strategy Chamber",
        "description": "One path reveals information before you commit.",
        "instruction": "Which choice gives you more information before moving?",
        "options": [
            {"id": "1", "label": "Unknown Path ❔"},
            {"id": "2", "label": "Revealed Path 👁️"},
        ],
        "correct_answer": "2",
        "time_limit": 45,
        "score": {
            "correct": 60,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 40,
        },
        "xp_correct": 110,
        "tokens_correct": 55,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-012",
        "title": "The Risk Gate",
        "category": "Strategy Chamber",
        "description": "You can choose a safe route or a risky shortcut.",
        "instruction": "Which choice is safer when the goal is to protect your current progress?",
        "options": [
            {"id": "1", "label": "Safe Route 🛡️"},
            {"id": "2", "label": "Unknown Shortcut ⚡"},
        ],
        "correct_answer": "1",
        "time_limit": 40,
        "score": {
            "correct": 70,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 35,
        },
        "xp_correct": 125,
        "tokens_correct": 65,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-013",
        "title": "The Two Doors",
        "category": "Strategy Chamber",
        "description": "One door gives a guaranteed small reward. The other offers a larger reward but may fail.",
        "instruction": "Which door guarantees a reward?",
        "options": [
            {"id": "1", "label": "Golden Door — guaranteed 🟡"},
            {"id": "2", "label": "Shadow Door — uncertain 🌑"},
        ],
        "correct_answer": "1",
        "time_limit": 35,
        "score": {
            "correct": 75,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 30,
        },
        "xp_correct": 130,
        "tokens_correct": 70,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    # ============================================================
    # MAZE
    # ============================================================

    {
        "id": "mission-006",
        "title": "The Hidden Path",
        "category": "Maze Chamber",
        "description": "Only one route leads through the chamber.",
        "instruction": "Choose the path marked by the correct royal clue.",
        "options": [
            {"id": "1", "label": "Path of Fire 🔥"},
            {"id": "2", "label": "Path of Wisdom 👁️"},
            {"id": "3", "label": "Path of Shadows 🌑"},
        ],
        "correct_answer": "2",
        "time_limit": 50,
        "score": {
            "correct": 65,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 45,
        },
        "xp_correct": 120,
        "tokens_correct": 60,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-014",
        "title": "The Forked Corridor",
        "category": "Maze Chamber",
        "description": "A corridor divides into three paths.",
        "instruction": "Choose the path that follows the visible sequence.",
        "target": "🔺 → 🔵 → 🟢",
        "options": [
            {"id": "1", "label": "Path A 🔺"},
            {"id": "2", "label": "Path B 🔵"},
            {"id": "3", "label": "Path C 🟢"},
        ],
        "correct_answer": "3",
        "time_limit": 45,
        "score": {
            "correct": 70,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 40,
        },
        "xp_correct": 125,
        "tokens_correct": 65,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-015",
        "title": "The Shadow Corridor",
        "category": "Maze Chamber",
        "description": "The maze gives you three possible directions.",
        "instruction": "Choose the only path that does not return to the entrance.",
        "options": [
            {"id": "1", "label": "North Gate ⬆️"},
            {"id": "2", "label": "East Gate ↗️"},
            {"id": "3", "label": "Return Gate ↩️"},
        ],
        "correct_answer": "2",
        "time_limit": 40,
        "score": {
            "correct": 75,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 35,
        },
        "xp_correct": 130,
        "tokens_correct": 70,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    # ============================================================
    # PATTERN / REACTION
    # ============================================================

    {
        "id": "mission-016",
        "title": "The Royal Rhythm",
        "category": "Pattern & Reaction",
        "description": "The symbols follow a repeating rhythm.",
        "instruction": "Which symbol comes next?",
        "display_sequence": "🔴 🔵 🔴 🔵",
        "options": [
            {"id": "1", "label": "🔴"},
            {"id": "2", "label": "🔵"},
            {"id": "3", "label": "🟢"},
        ],
        "correct_answer": "1",
        "time_limit": 30,
        "score": {
            "correct": 80,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 25,
        },
        "xp_correct": 135,
        "tokens_correct": 70,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-017",
        "title": "The Rising Pattern",
        "category": "Pattern & Reaction",
        "description": "The sequence changes according to a simple visual rule.",
        "instruction": "Choose the next symbol.",
        "display_sequence": "◆ ◆ ● ◆ ◆ ●",
        "options": [
            {"id": "1", "label": "◆"},
            {"id": "2", "label": "●"},
            {"id": "3", "label": "▲"},
        ],
        "correct_answer": "1",
        "time_limit": 30,
        "score": {
            "correct": 85,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 25,
        },
        "xp_correct": 140,
        "tokens_correct": 75,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-018",
        "title": "The Final Signal",
        "category": "Pattern & Reaction",
        "description": "The royal signal alternates between two symbols.",
        "instruction": "Identify the next signal.",
        "display_sequence": "⭐ 🌙 ⭐ 🌙 ⭐",
        "options": [
            {"id": "1", "label": "⭐"},
            {"id": "2", "label": "🌙"},
            {"id": "3", "label": "☀️"},
        ],
        "correct_answer": "2",
        "time_limit": 25,
        "score": {
            "correct": 90,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 20,
        },
        "xp_correct": 150,
        "tokens_correct": 80,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-019",
        "title": "The Scribe's Seals",
        "category": "Archive Chamber",
        "description": (
            "Three seals guard the royal archive: Sun, Moon, and Crown. "
            "The scribe has left two clues for the correct order."
        ),
        "instruction": (
            "The Sun is left of the Moon, and the Crown is right of the Moon. "
            "Which sequence follows both clues?"
        ),
        "options": [
            {"id": "1", "label": "Sun → Moon → Crown"},
            {"id": "2", "label": "Moon → Sun → Crown"},
            {"id": "3", "label": "Crown → Sun → Moon"},
        ],
        "correct_answer": "1",
        "time_limit": 50,
        "score": {
            "correct": 90,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 40,
        },
        "xp_correct": 150,
        "tokens_correct": 75,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-020",
        "title": "Signal at Dusk",
        "category": "Pattern & Reaction",
        "description": (
            "The watchkeeper repeats a three-beat signal so the night "
            "guards can recognize the safe passage."
        ),
        "instruction": "Which two marks come next in the repeating call?",
        "display_sequence": "🔔 · 🛡️ · 🐎 | 🔔 · 🛡️ · 🐎",
        "options": [
            {"id": "1", "label": "Bell → Shield"},
            {"id": "2", "label": "Shield → Horse"},
            {"id": "3", "label": "Horse → Bell"},
        ],
        "correct_answer": "1",
        "time_limit": 40,
        "score": {
            "correct": 95,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 30,
        },
        "xp_correct": 155,
        "tokens_correct": 80,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },

    {
        "id": "mission-021",
        "title": "The Council's Wager",
        "category": "Strategy Chamber",
        "description": (
            "A caravan is carrying its only royal token through an unfamiliar "
            "district. The council must choose between a known route and a shortcut."
        ),
        "instruction": (
            "If protecting the token is the priority, which route avoids "
            "taking an unknown risk?"
        ),
        "options": [
            {"id": "1", "label": "Inspected passage — confirmed clear"},
            {"id": "2", "label": "Unmapped shortcut — conditions unknown"},
        ],
        "correct_answer": "1",
        "time_limit": 45,
        "score": {
            "correct": 85,
            "incorrect": 0,
            "time_bonus": 1,
            "max_time_bonus": 35,
        },
        "xp_correct": 145,
        "tokens_correct": 75,
        "xp_incorrect": 10,
        "tokens_incorrect": 5,
    },
]


def get_all_challenges():
    """
    Return the complete Royal Labyrinth challenge catalog.
    """
    return CHALLENGES


def get_challenge(challenge_id: str):
    """
    Return one challenge by ID.
    """
    for challenge in CHALLENGES:
        if challenge["id"] == challenge_id:
            return challenge

    return None
