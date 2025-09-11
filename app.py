import os
import signal
import sys
from types import FrameType

from flask import Flask, render_template, request, redirect, url_for, session, flash, abort

from puzzles import PUZZLES


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    TOTAL_MISTERIS = len(PUZZLES)

    def _get_progress():
        return session.get("current_misteri", 1)

    def _set_progress(misteri: int):
        session["current_misteri"] = misteri

    @app.before_request
    def ensure_progress_initialized():
        if "current_misteri" not in session:
            _set_progress(1)

    @app.get("/")
    def portada():
        return render_template("portada.html")

    @app.get("/misteris")
    def index():
        current = _get_progress()
        return render_template("index.html", current_misteri=current, total_misteris=TOTAL_MISTERIS, puzzle=PUZZLES)

    @app.get("/misteri/<int:misteri>")
    def misteri(misteri: int):
        current = _get_progress()
        if misteri < 1 or misteri > TOTAL_MISTERIS:
            abort(404)
        if misteri > current:
            flash("No pots saltar-te un misteri... Rumia-hi una mica!", "warning")
            return redirect(url_for("misteri", misteri=current))
        if misteri < current:
            return redirect(url_for("misteri", misteri=current))

        puzzle = PUZZLES[misteri - 1]
        return render_template(
            "misteri.html",
            misteri=misteri,
            total_misteris=TOTAL_MISTERIS,
            prompt=puzzle["prompt"],
            media_type=puzzle["media_type"],
            media=puzzle["media"],
            key=puzzle["key"],
            hint=puzzle.get("hint"),
            placeholder=puzzle.get("placeholder", "Enter the key"),
        )

    @app.post("/misteri/<int:misteri>/check")
    def check(misteri: int):
        current = _get_progress()
        if misteri != current:
            flash("Encara no estàs en aquest misteri.", "warning")
            return redirect(url_for("misteri", misteri=current))
        if misteri < 1 or misteri > TOTAL_MISTERIS:
            abort(404)

        user_key = (request.form.get("key") or "").strip().lower()
        correct = [k.lower() for k in PUZZLES[misteri - 1]["answers"]]
        if user_key in correct:
            if misteri == TOTAL_MISTERIS:
                _set_progress(TOTAL_MISTERIS + 1)
                return redirect(url_for("victory"))
            else:
                _set_progress(misteri + 1)
                flash("Genial! Següent misteri…", "success")
                return redirect(url_for("misteri", misteri=misteri + 1))
        else:
            flash("No del tot. Torna a intentar-ho o utilitza la pista", "danger")
            return redirect(url_for("misteri", misteri=misteri))

    @app.get("/resolt")
    def victory():
        if _get_progress() <= TOTAL_MISTERIS:
            return redirect(url_for("misteri", misteri=_get_progress()))
        return render_template("victory.html", total_misteris=TOTAL_MISTERIS)

    @app.get("/reset")
    def reset():
        session.clear()
        flash("Progrés resetejat.", "info")
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