#!/usr/bin/env python3
"""Myk Quiz web application server. Uses only the Python standard library."""

import argparse
import hmac
import json
import os
import secrets
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
DATA_DIR = Path(os.environ.get("MYK_DATA_DIR", ROOT / "data"))
QUESTION_FILE = DATA_DIR / "questions.json"
QUESTION_LOCK = threading.Lock()
ROOM_LOCK = threading.Lock()
ADMIN_SESSIONS = {}
ROOMS = {}
SESSION_LIFETIME = 8 * 60 * 60
ROOM_LIFETIME = 6 * 60 * 60
ROOM_CODE_CHARACTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

SEED_QUESTIONS = [
    {
        "id": "py-list-comprehension",
        "question": "Which expression creates a list of squares from 0 to 4 in Python?",
        "options": ["[x ** 2 for x in range(5)]", "{x ** 2 for x in range(5)}", "square(x) * 5", "list(range(5))"],
        "correct_answer": 0,
        "category": "Python",
        "difficulty": "Easy",
        "explanation": "A list comprehension combines an expression and a for-clause inside square brackets.",
    },
    {
        "id": "js-constant",
        "question": "Which keyword declares a block-scoped variable that cannot be reassigned?",
        "options": ["var", "let", "const", "static"],
        "correct_answer": 2,
        "category": "JavaScript",
        "difficulty": "Easy",
        "explanation": "Use const for a block-scoped binding that should not be reassigned.",
    },
    {
        "id": "git-commit",
        "question": "Which Git command records staged changes in the repository history?",
        "options": ["git push", "git commit", "git fetch", "git status"],
        "correct_answer": 1,
        "category": "Tools",
        "difficulty": "Easy",
        "explanation": "git commit creates a new commit from the changes in the staging area.",
    },
    {
        "id": "html-semantic",
        "question": "Which HTML element represents the main content of a page?",
        "options": ["<section>", "<header>", "<main>", "<aside>"],
        "correct_answer": 2,
        "category": "Web",
        "difficulty": "Easy",
        "explanation": "The main element identifies the dominant content of the document body.",
    },
    {
        "id": "css-flex",
        "question": "Which CSS declaration turns an element into a flex container?",
        "options": ["position: flex", "display: flex", "flex: display", "layout: flex"],
        "correct_answer": 1,
        "category": "Web",
        "difficulty": "Easy",
        "explanation": "Setting display to flex enables the flex formatting context for its children.",
    },
    {
        "id": "sql-filter",
        "question": "Which SQL clause filters rows before they are grouped?",
        "options": ["HAVING", "ORDER BY", "WHERE", "GROUP BY"],
        "correct_answer": 2,
        "category": "Databases",
        "difficulty": "Easy",
        "explanation": "WHERE filters individual rows; HAVING filters groups after aggregation.",
    },
    {
        "id": "python-tuple",
        "question": "Which Python data type is immutable?",
        "options": ["list", "dict", "set", "tuple"],
        "correct_answer": 3,
        "category": "Python",
        "difficulty": "Easy",
        "explanation": "A tuple cannot be changed after it has been created.",
    },
    {
        "id": "http-201",
        "question": "What does HTTP status code 201 usually mean?",
        "options": ["Request accepted, no response yet", "Resource created", "Not modified", "Unauthorized"],
        "correct_answer": 1,
        "category": "Web",
        "difficulty": "Medium",
        "explanation": "201 Created indicates that a request succeeded and created a resource.",
    },
    {
        "id": "js-array-map",
        "question": "What does JavaScript's Array.map() return?",
        "options": ["A new transformed array", "The first matching item", "A boolean", "The original array, changed in place"],
        "correct_answer": 0,
        "category": "JavaScript",
        "difficulty": "Medium",
        "explanation": "map() applies a callback to each item and returns a new array.",
    },
    {
        "id": "git-branch",
        "question": "Which Git command creates and switches to a new branch?",
        "options": ["git branch --list", "git switch -c feature", "git merge feature", "git reset feature"],
        "correct_answer": 1,
        "category": "Tools",
        "difficulty": "Medium",
        "explanation": "git switch -c creates a branch and checks it out in one step.",
    },
    {
        "id": "python-is",
        "question": "In Python, what does the `is` operator compare?",
        "options": ["Whether two values are equal", "Whether two names refer to the same object", "Whether a value is truthy", "Whether types are compatible"],
        "correct_answer": 1,
        "category": "Python",
        "difficulty": "Medium",
        "explanation": "is tests object identity; use == to compare values.",
    },
    {
        "id": "css-specificity",
        "question": "Which selector generally has the highest CSS specificity?",
        "options": [".card", "article", "#card", "*"],
        "correct_answer": 2,
        "category": "Web",
        "difficulty": "Medium",
        "explanation": "An ID selector has higher specificity than a class, element, or universal selector.",
    },
    {
        "id": "sql-index",
        "question": "What is a common trade-off when adding a database index?",
        "options": ["Faster reads but more storage and slower writes", "Smaller tables but slower reads", "It removes the need for transactions", "It prevents duplicate values in every column"],
        "correct_answer": 0,
        "category": "Databases",
        "difficulty": "Hard",
        "explanation": "Indexes speed up many reads, but consume storage and must be maintained on writes.",
    },
    {
        "id": "js-promise",
        "question": "Which Promise method runs after either fulfillment or rejection?",
        "options": ["then()", "catch()", "finally()", "resolve()"],
        "correct_answer": 2,
        "category": "JavaScript",
        "difficulty": "Medium",
        "explanation": "finally() runs when a promise settles, regardless of its outcome.",
    },
    {
        "id": "python-generator",
        "question": "Which keyword makes a Python function produce a generator value?",
        "options": ["return", "yield", "async", "lambda"],
        "correct_answer": 1,
        "category": "Python",
        "difficulty": "Hard",
        "explanation": "A function containing yield produces values lazily as a generator.",
    },
    {
        "id": "http-method",
        "question": "Which HTTP method is conventionally used to retrieve a resource?",
        "options": ["POST", "PATCH", "GET", "DELETE"],
        "correct_answer": 2,
        "category": "Web",
        "difficulty": "Easy",
        "explanation": "GET requests representation of a resource and should not change server state.",
    },
    {
        "id": "git-rebase",
        "question": "What is the usual purpose of `git rebase`?",
        "options": ["Move or replay commits onto another base", "Delete the remote repository", "Create a release tag", "Restore deleted files only"],
        "correct_answer": 0,
        "category": "Tools",
        "difficulty": "Hard",
        "explanation": "Rebase reapplies commits onto a new base, creating a more linear history.",
    },
    {
        "id": "db-primary-key",
        "question": "What does a primary key guarantee in a relational table?",
        "options": ["Every row has a unique, non-null identifier", "Every column is indexed", "Rows are stored alphabetically", "Values are encrypted"],
        "correct_answer": 0,
        "category": "Databases",
        "difficulty": "Easy",
        "explanation": "A primary key uniquely identifies each row and cannot be null.",
    },
    {
        "id": "js-event-loop",
        "question": "In JavaScript, where are callbacks from completed timers queued?",
        "options": ["The call stack", "The task queue", "The heap only", "The parser queue"],
        "correct_answer": 1,
        "category": "JavaScript",
        "difficulty": "Hard",
        "explanation": "Timer callbacks are queued as tasks and run when the call stack is clear.",
    },
    {
        "id": "python-exception",
        "question": "Which Python block runs whether or not an exception occurred?",
        "options": ["except", "else", "finally", "raise"],
        "correct_answer": 2,
        "category": "Python",
        "difficulty": "Medium",
        "explanation": "A finally block is used for cleanup that should happen in either outcome.",
    },
]


def load_questions():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not QUESTION_FILE.exists():
        QUESTION_FILE.write_text(json.dumps(SEED_QUESTIONS, indent=2), encoding="utf-8")
    try:
        items = json.loads(QUESTION_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Could not read data/questions.json") from exc
    if not isinstance(items, list):
        raise RuntimeError("data/questions.json must contain a JSON array")
    return items


def save_questions(items):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary = QUESTION_FILE.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(QUESTION_FILE)


class MykRequestHandler(SimpleHTTPRequestHandler):
    server_version = "MykQuiz/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/meta":
            with QUESTION_LOCK:
                items = load_questions()
            self.send_json(200, {
                "categories": sorted({item["category"] for item in items}),
                "question_count": len(items),
            })
            return
        if parsed.path.startswith("/api/rooms/"):
            self.get_room(parsed.path.split("/"))
            return
        if parsed.path == "/api/questions":
            self.get_questions(parse_qs(parsed.query))
            return
        if parsed.path == "/api/admin/questions":
            if not self.require_admin():
                return
            with QUESTION_LOCK:
                self.send_json(200, load_questions())
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        payload = self.read_json()
        if payload is None:
            return
        if path == "/api/admin/login":
            self.admin_login(payload)
        elif path == "/api/admin/questions":
            if self.require_admin():
                self.add_question(payload)
        elif path == "/api/answer":
            self.check_answer(payload)
        elif path == "/api/rooms":
            self.create_room(payload)
        elif path.startswith("/api/rooms/"):
            self.update_room(path.split("/"), payload)
        else:
            self.send_json(404, {"error": "Not found"})

    def create_room(self, payload):
        category = payload.get("category", "All")
        try:
            question_count = int(payload.get("question_count", 10))
        except (TypeError, ValueError):
            self.send_json(400, {"error": "Choose between 1 and 30 questions."})
            return
        if not isinstance(category, str) or not 1 <= question_count <= 30:
            self.send_json(400, {"error": "Choose a valid topic and between 1 and 30 questions."})
            return
        with QUESTION_LOCK:
            questions = load_questions()
        if category != "All":
            questions = [item for item in questions if item["category"] == category]
        if not questions:
            self.send_json(400, {"error": "There are no questions in this topic yet. Add questions or choose another topic."})
            return
        secrets.SystemRandom().shuffle(questions)
        selected = questions[:question_count]
        code = ""
        host_token = secrets.token_urlsafe(32)
        with ROOM_LOCK:
            self.remove_expired_rooms()
            while not code or code in ROOMS:
                code = "".join(secrets.choice(ROOM_CODE_CHARACTERS) for _ in range(6))
            ROOMS[code] = {
                "host_token": host_token,
                "created_at": time.time(),
                "last_activity": time.time(),
                "questions": selected,
                "index": -1,
                "deadline": None,
                "players": {},
                "status": "lobby",
            }
        self.send_json(201, {"code": code, "token": host_token, "question_count": len(selected)})

    def join_room(self, payload):
        code = payload.get("code", "")
        name = payload.get("name", "")
        if not isinstance(code, str) or not isinstance(name, str):
            self.send_json(400, {"error": "Enter a room code and player name."})
            return
        code = code.strip().upper()
        name = name.strip()
        if not 2 <= len(name) <= 24:
            self.send_json(400, {"error": "Your name must be between 2 and 24 characters."})
            return
        with ROOM_LOCK:
            self.remove_expired_rooms()
            room = ROOMS.get(code)
            if room is None:
                self.send_json(404, {"error": "Room not found. Check the code with your host."})
                return
            if room["status"] != "lobby":
                self.send_json(409, {"error": "This quiz has already started. Ask your host to create a new room."})
                return
            if len(room["players"]) >= 200:
                self.send_json(409, {"error": "This room has reached its 200-player limit."})
                return
            if any(player["name"].casefold() == name.casefold() for player in room["players"].values()):
                self.send_json(409, {"error": "That name is already in this room. Choose another."})
                return
            token = secrets.token_urlsafe(32)
            room["players"][token] = {"name": name, "score": 0, "answers": {}}
            room["last_activity"] = time.time()
        self.send_json(201, {"code": code, "token": token})

    def get_room(self, path_parts):
        if len(path_parts) != 4 or path_parts[3] == "":
            self.send_json(404, {"error": "Not found"})
            return
        code = path_parts[3].upper()
        token = self.room_token()
        with ROOM_LOCK:
            self.remove_expired_rooms()
            room = ROOMS.get(code)
            if room is None:
                self.send_json(404, {"error": "Room not found or expired."})
                return
            is_host = secrets.compare_digest(room["host_token"], token)
            player = room["players"].get(token)
            if not is_host and player is None:
                self.send_json(403, {"error": "This device is not signed in to that room."})
                return
            room["last_activity"] = time.time()
            self.send_json(200, self.room_snapshot(room, is_host, player))

    def update_room(self, path_parts, payload):
        if len(path_parts) == 4 and path_parts[3].upper() == "JOIN":
            self.join_room(payload)
            return
        if len(path_parts) != 5:
            self.send_json(404, {"error": "Not found"})
            return
        code = path_parts[3].upper()
        action = path_parts[4].lower()
        if action == "answer":
            self.submit_room_answer(code, payload)
            return
        if action not in ("start", "next"):
            self.send_json(404, {"error": "Not found"})
            return
        token = self.room_token()
        with ROOM_LOCK:
            self.remove_expired_rooms()
            room = ROOMS.get(code)
            if room is None:
                self.send_json(404, {"error": "Room not found or expired."})
                return
            if not secrets.compare_digest(room["host_token"], token):
                self.send_json(403, {"error": "Only the host can control this quiz."})
                return
            now = time.time()
            room["last_activity"] = now
            if action == "start":
                if room["status"] != "lobby":
                    self.send_json(409, {"error": "This quiz has already started."})
                    return
                room["status"] = "active"
                room["index"] = 0
                room["deadline"] = now + 15
            else:
                if room["status"] != "active":
                    self.send_json(409, {"error": "There is no active question to advance."})
                    return
                if room["index"] + 1 >= len(room["questions"]):
                    room["status"] = "finished"
                    room["deadline"] = None
                else:
                    room["index"] += 1
                    room["deadline"] = now + 15
            self.send_json(200, self.room_snapshot(room, True, None))

    def submit_room_answer(self, code, payload):
        answer = payload.get("answer")
        token = self.room_token()
        if isinstance(answer, bool) or not isinstance(answer, int) or answer not in range(4):
            self.send_json(400, {"error": "Choose an answer from 1 to 4."})
            return
        with ROOM_LOCK:
            self.remove_expired_rooms()
            room = ROOMS.get(code)
            if room is None:
                self.send_json(404, {"error": "Room not found or expired."})
                return
            player = room["players"].get(token)
            if player is None:
                self.send_json(403, {"error": "Only a joined player can submit an answer."})
                return
            if room["status"] != "active":
                self.send_json(409, {"error": "The host has not opened a question yet."})
                return
            index = room["index"]
            if time.time() >= room["deadline"]:
                self.send_json(409, {"error": "Time is up for this question."})
                return
            if index in player["answers"]:
                self.send_json(409, {"error": "You have already answered this question."})
                return
            correct = answer == room["questions"][index]["correct_answer"]
            player["answers"][index] = {"answer": answer, "correct": correct}
            if correct:
                player["score"] += 100
            room["last_activity"] = time.time()
            self.send_json(200, {
                "correct": correct,
                "correct_answer": room["questions"][index]["correct_answer"],
                "explanation": room["questions"][index].get("explanation", ""),
            })

    def room_snapshot(self, room, is_host, player):
        now = time.time()
        index = room["index"]
        question = None
        revealed = False
        my_answer = None
        if index >= 0:
            source = room["questions"][index]
            question = {key: source[key] for key in ("question", "options", "category", "difficulty")}
            revealed = room["status"] == "finished" or (
                room["status"] == "active" and now >= room["deadline"]
            )
            if is_host or revealed:
                question["correct_answer"] = source["correct_answer"]
                question["explanation"] = source.get("explanation", "")
            if player is not None:
                my_answer = player["answers"].get(index)
                if my_answer is not None:
                    my_answer = dict(my_answer)
                    if room["deadline"] is not None and now < room["deadline"] and room["status"] == "active":
                        my_answer["correct_answer"] = source["correct_answer"]
                        my_answer["explanation"] = source.get("explanation", "")
        player_list = []
        for item in room["players"].values():
            answer = item["answers"].get(index) if index >= 0 else None
            player_list.append({
                "name": item["name"],
                "score": item["score"],
                "answered": answer is not None,
                "passed": answer["correct"] if answer is not None else None,
            })
        player_list.sort(key=lambda item: (-item["score"], item["name"].casefold()))
        return {
            "code": next((code for code, candidate in ROOMS.items() if candidate is room), ""),
            "role": "host" if is_host else "player",
            "status": room["status"],
            "index": index,
            "total": len(room["questions"]),
            "question": question,
            "revealed": revealed,
            "remaining_seconds": max(0, int(room["deadline"] - now + 0.999)) if room["deadline"] else 0,
            "my_answer": my_answer,
            "players": player_list,
            "score": player["score"] if player is not None else None,
        }

    def room_token(self):
        authorization = self.headers.get("Authorization", "")
        return authorization.removeprefix("Bearer ").strip()

    def remove_expired_rooms(self):
        cutoff = time.time() - ROOM_LIFETIME
        expired = [code for code, room in ROOMS.items() if room["last_activity"] < cutoff]
        for code in expired:
            del ROOMS[code]

    def get_questions(self, query):
        category = query.get("category", ["All"])[0]
        try:
            limit = max(1, min(20, int(query.get("limit", ["10"])[0])))
        except ValueError:
            self.send_json(400, {"error": "limit must be a number"})
            return
        with QUESTION_LOCK:
            items = load_questions()
        if category != "All":
            items = [item for item in items if item["category"] == category]
        secrets.SystemRandom().shuffle(items)
        selected = items[:limit]
        public_items = [
            {key: item[key] for key in ("id", "question", "options", "category", "difficulty")}
            for item in selected
        ]
        self.send_json(200, {"questions": public_items, "total": len(items)})

    def admin_login(self, payload):
        expected = os.environ.get("MYK_ADMIN_PASSWORD", "")
        supplied = payload.get("password", "")
        if not expected:
            self.send_json(503, {"error": "Admin login is disabled. Set MYK_ADMIN_PASSWORD and restart the server."})
            return
        if not isinstance(supplied, str) or not hmac.compare_digest(supplied, expected):
            self.send_json(401, {"error": "Incorrect admin password."})
            return
        token = secrets.token_urlsafe(32)
        ADMIN_SESSIONS[token] = time.time() + SESSION_LIFETIME
        self.send_json(200, {"token": token})

    def require_admin(self):
        authorization = self.headers.get("Authorization", "")
        token = authorization.removeprefix("Bearer ").strip()
        expiry = ADMIN_SESSIONS.get(token)
        if expiry is None or expiry < time.time():
            ADMIN_SESSIONS.pop(token, None)
            self.send_json(401, {"error": "Admin sign-in required."})
            return False
        return True

    def add_question(self, payload):
        question = payload.get("question")
        options = payload.get("options")
        category = payload.get("category")
        difficulty = payload.get("difficulty")
        correct = payload.get("correct_answer")
        explanation = payload.get("explanation", "")
        if (
            not isinstance(question, str) or not question.strip() or len(question) > 500
            or not isinstance(options, list) or len(options) != 4
            or any(not isinstance(option, str) or not option.strip() or len(option) > 200 for option in options)
            or not isinstance(category, str) or not category.strip() or len(category) > 40
            or difficulty not in ("Easy", "Medium", "Hard")
            or isinstance(correct, bool) or not isinstance(correct, int) or correct not in range(4)
            or not isinstance(explanation, str) or len(explanation) > 500
        ):
            self.send_json(400, {"error": "Add a question, four answers, category, difficulty and a valid correct answer."})
            return
        new_item = {
            "id": secrets.token_hex(12),
            "question": question.strip(),
            "options": [option.strip() for option in options],
            "correct_answer": correct,
            "category": category.strip(),
            "difficulty": difficulty,
            "explanation": explanation.strip(),
        }
        with QUESTION_LOCK:
            items = load_questions()
            items.append(new_item)
            save_questions(items)
        self.send_json(201, {"id": new_item["id"]})

    def check_answer(self, payload):
        question_id = payload.get("question_id")
        answer = payload.get("answer")
        if not isinstance(question_id, str) or isinstance(answer, bool) or not isinstance(answer, int) or answer not in range(4):
            self.send_json(400, {"error": "A question_id and answer from 0 to 3 are required."})
            return
        with QUESTION_LOCK:
            items = load_questions()
        item = next((question for question in items if question["id"] == question_id), None)
        if item is None:
            self.send_json(404, {"error": "Question not found."})
            return
        self.send_json(200, {
            "correct": answer == item["correct_answer"],
            "correct_answer": item["correct_answer"],
            "explanation": item.get("explanation", ""),
        })

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"error": "Invalid content length."})
            return None
        if length < 1 or length > 16_384:
            self.send_json(400, {"error": "Request body is empty or too large."})
            return None
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "Request body must be valid JSON."})
            return None
        if not isinstance(payload, dict):
            self.send_json(400, {"error": "Request body must be a JSON object."})
            return None
        return payload

    def send_json(self, status, value):
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description="Run the Myk programming quiz web app.")
    default_host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    parser.add_argument("--host", default=os.environ.get("MYK_HOST", default_host), help="Host interface (use 0.0.0.0 to serve on a network)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")), help="HTTP port")
    args = parser.parse_args()
    load_questions()
    server = ThreadingHTTPServer((args.host, args.port), MykRequestHandler)
    print("Myk Quiz is ready at http://{}:{}/".format(args.host, args.port))
    if not os.environ.get("MYK_ADMIN_PASSWORD"):
        print("Admin is disabled. Set MYK_ADMIN_PASSWORD to enable question management.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Myk Quiz.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
