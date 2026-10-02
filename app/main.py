from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.exc import IntegrityError

from app.database import engine, SessionLocal
from app.models import Base, Player, ChallengeAttempt
from app.routes.auth import router as auth_router
from app.challenges import get_all_challenges, get_challenge


app = FastAPI(title="Damba Royal")


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# SESSIONS
# =========================================================

app.add_middleware(
    SessionMiddleware,
    secret_key="damba-royal-founders-era-secret-key-change-later"
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


# =========================================================
# TEMPLATES
# =========================================================

templates = Jinja2Templates(
    directory="app/templates"
)


# =========================================================
# HOME
# =========================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# =========================================================
# LOGIN PAGE
# =========================================================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


# =========================================================
# REGISTER PAGE
# =========================================================

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )


# =========================================================
# PLAYER DASHBOARD
# =========================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):

    player_id = request.session.get("player_id")

    if not player_id:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    db = SessionLocal()

    try:

        player = (
            db.query(Player)
            .filter(Player.id == player_id)
            .first()
        )

        if not player:

            request.session.clear()

            return RedirectResponse(
                url="/login",
                status_code=303
            )

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "player": player
            }
        )

    finally:

        db.close()


# =========================================================
# ROYAL LABYRINTH PAGE
# =========================================================

@app.get("/challenge", response_class=HTMLResponse)
async def challenge(request: Request):

    player_id = request.session.get("player_id")

    if not player_id:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="challenge.html",
        context={}
    )


# =========================================================
# NEXT ROYAL LABYRINTH MISSION
# =========================================================

@app.get("/api/challenges/next")
async def get_next_challenge(request: Request):

    # -----------------------------------------------------
    # AUTHENTICATION
    # -----------------------------------------------------

    player_id = request.session.get("player_id")

    if not player_id:

        return {
            "success": False,
            "error": "Not authenticated"
        }


    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # FIND COMPLETED MISSIONS
        # -------------------------------------------------

        completed_attempts = (
            db.query(ChallengeAttempt.challenge_id)
            .filter(
                ChallengeAttempt.player_id == player_id
            )
            .all()
        )


        completed_ids = {
            attempt.challenge_id
            for attempt in completed_attempts
        }


        # -------------------------------------------------
        # FIND FIRST UNCOMPLETED MISSION
        # -------------------------------------------------

        for challenge_data in get_all_challenges():

            challenge_id = challenge_data["id"]

            if challenge_id not in completed_ids:

                # -----------------------------------------
                # NEVER SEND CORRECT ANSWER TO BROWSER
                # -----------------------------------------

                public_challenge = {

                    "id": challenge_data["id"],

                    "title": challenge_data["title"],

                    "category": challenge_data["category"],

                    "description": challenge_data["description"],

                    "instruction": challenge_data["instruction"],

                    "target": challenge_data.get(
                        "target"
                    ),

                    "options": challenge_data.get(
                        "options",
                        []
                    ),

                    "display_sequence": challenge_data.get(
                        "display_sequence"
                    ),

                    "memory_sequence": challenge_data.get(
                        "memory_sequence"
                    ),

                    "time_limit": challenge_data.get(
                        "time_limit",
                        60
                    )
                }


                return {
                    "success": True,
                    "completed": False,
                    "challenge": public_challenge
                }


        # -------------------------------------------------
        # ALL AVAILABLE MISSIONS COMPLETED
        # -------------------------------------------------

        return {
            "success": True,
            "completed": True,
            "message": (
                "You have completed every available "
                "Royal Labyrinth mission."
            )
        }

    finally:

        db.close()


# =========================================================
# GENERIC MISSION COMPLETION
# =========================================================

@app.post("/api/challenges/{challenge_id}/complete")
async def complete_challenge(
    request: Request,
    challenge_id: str,
    answer: str = Form(...),
    time_left: int = Form(0)
):

    # -----------------------------------------------------
    # AUTHENTICATION
    # -----------------------------------------------------

    player_id = request.session.get("player_id")

    if not player_id:

        return {
            "success": False,
            "error": "Not authenticated"
        }


    # -----------------------------------------------------
    # FIND CHALLENGE
    # -----------------------------------------------------

    challenge = get_challenge(
        challenge_id
    )

    if not challenge:

        return {
            "success": False,
            "error": "Challenge not found."
        }


    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # FIND PLAYER
        # -------------------------------------------------

        player = (
            db.query(Player)
            .filter(
                Player.id == player_id
            )
            .first()
        )

        if not player:

            return {
                "success": False,
                "error": "Player not found."
            }


        # -------------------------------------------------
        # CHECK FOR PREVIOUS ATTEMPT
        # -------------------------------------------------

        existing_attempt = (
            db.query(ChallengeAttempt)
            .filter(
                ChallengeAttempt.player_id == player_id,
                ChallengeAttempt.challenge_id == challenge_id
            )
            .first()
        )


        if existing_attempt:

            return {
                "success": False,
                "already_completed": True,
                "error": (
                    "You have already attempted "
                    f"{challenge_id}."
                )
            }


        # -------------------------------------------------
        # SERVER-SIDE ANSWER
        # -------------------------------------------------

        correct_answer = str(
            challenge["correct_answer"]
        )

        submitted_answer = str(
            answer
        ).strip()


        # -------------------------------------------------
        # SAFE TIME
        # -------------------------------------------------

        try:

            submitted_time = int(
                time_left
            )

        except (TypeError, ValueError):

            submitted_time = 0


        time_limit = int(
            challenge.get(
                "time_limit",
                60
            )
        )


        safe_time = max(
            0,
            min(
                submitted_time,
                time_limit
            )
        )


        # -------------------------------------------------
        # DETERMINE RESULT
        # -------------------------------------------------

        is_correct = (
            submitted_answer ==
            correct_answer
        )


        if is_correct:

            # -------------------------------------------------
            # NEW ROYAL SCORING SYSTEM
            # -------------------------------------------------

            scoring = challenge.get(
                "score",
                {}
            )

            base_score = int(
                scoring.get(
                    "correct",
                    50
                )
            )

            time_bonus_rate = float(
                scoring.get(
                    "time_bonus",
                    1
                )
            )

            max_time_bonus = int(
                scoring.get(
                    "max_time_bonus",
                    50
                )
            )

            calculated_time_bonus = int(
                safe_time * time_bonus_rate
            )

            time_bonus = min(
                calculated_time_bonus,
                max_time_bonus
            )

            score = (
                base_score
                + time_bonus
            )

            xp_awarded = int(
                challenge.get(
                    "xp_correct",
                    100
                )
            )

            tokens_awarded = int(
                challenge.get(
                    "tokens_correct",
                    50
                )
            )

        else:

            scoring = challenge.get(
                "score",
                {}
            )

            score = int(
                scoring.get(
                    "incorrect",
                    0
                )
            )

            xp_awarded = int(
                challenge.get(
                    "xp_incorrect",
                    10
                )
            )

            tokens_awarded = int(
                challenge.get(
                    "tokens_incorrect",
                    5
                )
            )


        # -------------------------------------------------
        # CREATE ATTEMPT
        # -------------------------------------------------

        attempt = ChallengeAttempt(

            player_id=player_id,

            challenge_id=challenge_id,

            answer=submitted_answer,

            correct=1 if is_correct else 0,

            score=score,

            xp_awarded=xp_awarded,

            tokens_awarded=tokens_awarded

        )


        db.add(
            attempt
        )


        # -------------------------------------------------
        # UPDATE PLAYER XP
        # -------------------------------------------------

        player.xp = (
            (player.xp or 0)
            + xp_awarded
        )


        # -------------------------------------------------
        # UPDATE ROYAL TOKENS
        # -------------------------------------------------

        player.royal_tokens = (
            (player.royal_tokens or 0)
            + tokens_awarded
        )


        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        try:

            db.commit()

        except IntegrityError:

            db.rollback()

            return {
                "success": False,
                "already_completed": True,
                "error": (
                    "Mission already completed."
                )
            }


        # -------------------------------------------------
        # REFRESH PLAYER
        # -------------------------------------------------

        db.refresh(
            player
        )


        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        return {

            "success": True,

            "already_completed": False,

            "mission_id": challenge_id,

            "correct": is_correct,

            "score": score,

            "xp_awarded": xp_awarded,

            "tokens_awarded": tokens_awarded,

            "total_xp": player.xp,

            "total_tokens": player.royal_tokens,

            "message": (

                "Royal mission conquered."

                if is_correct

                else

                "The mission remains unconquered. "
                "Your attempt has been recorded."

            )
        }

    finally:

        db.close()


# =========================================================
# PLAYER API
# =========================================================

@app.get("/api/player")
async def api_player(request: Request):

    player_id = request.session.get("player_id")

    if not player_id:

        return {
            "error": "Not authenticated"
        }


    db = SessionLocal()

    try:

        player = (
            db.query(Player)
            .filter(
                Player.id == player_id
            )
            .first()
        )

        if not player:

            return {
                "error": "Player not found"
            }


        return {

            "id": player.id,

            "royal_id": player.royal_id,

            "full_name": player.full_name,

            "email": player.email,

            "country": player.country,

            "alias": player.alias,

            "xp": player.xp,

            "royal_tokens": player.royal_tokens,

            "level": player.level,

            "badge": player.badge

        }

    finally:

        db.close()


# =========================================================
# AUTH ROUTES
# =========================================================

app.include_router(
    auth_router
)