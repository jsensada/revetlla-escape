import os
import signal
import sys
from types import FrameType

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort

from puzzles import PUZZLES


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    TOTAL_LEVELS = len(PUZZLES)

    def _get_progress():
        return session.get("current_level", 1)

    def _set_progress(level: int):
        session["current_level"] = level

    @app.before_request
    def ensure_progress_initialized():
        if "current_level" not in session:
            _set_progress(1)

    @app.get("/")
    def index():
        current = _get_progress()
        return render_template("index.html", current_level=current, total_levels=TOTAL_LEVELS)

    @app.get("/level/<int:level>")
    def level(level: int):
        current = _get_progress()
        if level < 1 or level > TOTAL_LEVELS:
            abort(404)
        if level > current:
            flash("You can't skip levels. Solve the current one first!", "warning")
            return redirect(url_for("level", level=current))
        if level < current:
            return redirect(url_for("level", level=current))

        puzzle = PUZZLES[level - 1]
        return render_template(
            "level.html",
            level=level,
            total_levels=TOTAL_LEVELS,
            prompt=puzzle["prompt"],
            hint=puzzle.get("hint"),
            placeholder=puzzle.get("placeholder", "Enter the key"),
        )

    @app.post("/level/<int:level>/check")
    def check(level: int):
        current = _get_progress()
        if level != current:
            flash("You're not on this level yet.", "warning")
            return redirect(url_for("level", level=current))
        if level < 1 or level > TOTAL_LEVELS:
            abort(404)

        user_key = (request.form.get("key") or "").strip().lower()
        correct = [k.lower() for k in PUZZLES[level - 1]["answers"]]
        if user_key in correct:
            if level == TOTAL_LEVELS:
                _set_progress(TOTAL_LEVELS + 1)
                return redirect(url_for("victory"))
            else:
                _set_progress(level + 1)
                flash("Unlocked! Moving to the next room…", "success")
                return redirect(url_for("level", level=level + 1))
        else:
            flash("Not quite. Try again or use the hint.", "danger")
            return redirect(url_for("level", level=level))

    @app.get("/victory")
    def victory():
        if _get_progress() <= TOTAL_LEVELS:
            return redirect(url_for("level", level=_get_progress()))
        return render_template("victory.html", total_levels=TOTAL_LEVELS)

    @app.get("/reset")
    def reset():
        session.clear()
        flash("Progress reset.", "info")
        return redirect(url_for("index"))

    return app


app = create_app()

def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    sys.exit(0)


if __name__ == "__main__":

    signal.signal(signal.SIGINT, shutdown_handler)
    app.run(host="localhost", port=8080, debug=True)
else:
    signal.signal(signal.SIGTERM, shutdown_handler)