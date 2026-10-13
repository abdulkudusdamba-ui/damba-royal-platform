import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

TEST_DATABASE = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = (
    f"sqlite:///{Path(TEST_DATABASE.name) / 'test_damba_royal.db'}"
)
os.environ["SESSION_SECRET"] = "test-session-key-not-for-production"

from fastapi.testclient import TestClient

from app.challenges import get_challenge
from app.database import SessionLocal
from app.live.models import LiveRoom
from app.main import app


class LiveCompetitionTests(unittest.TestCase):
    account_number = 0

    @classmethod
    def tearDownClass(cls):
        TEST_DATABASE.cleanup()

    def player(self):
        type(self).account_number += 1
        number = type(self).account_number
        client = TestClient(app)
        account = {
            "full_name": f"Test Player {number}",
            "email": f"player{number}@example.test",
            "country": "Ghana",
            "alias": f"Challenger{number}",
            "password": f"test-password-{number}"
        }
        registered = client.post(
            "/auth/register",
            data=account,
            follow_redirects=False
        )
        self.assertEqual(registered.status_code, 303)
        logged_in = client.post(
            "/auth/login",
            data={
                "email": account["email"],
                "password": account["password"]
            },
            follow_redirects=False
        )
        self.assertEqual(logged_in.status_code, 303)
        self.assertEqual(client.get("/api/player").json()["level"], "Unranked")
        self.addCleanup(client.close)
        return client

    def ready_match(self):
        host = self.player()
        guest = self.player()
        created = host.post("/api/live/rooms")
        self.assertEqual(created.status_code, 200)
        room_code = created.json()["room_code"]
        joined = guest.post(
            "/api/live/rooms/join",
            data={"room_code": room_code}
        )
        self.assertEqual(joined.status_code, 200)
        self.assertEqual(host.post(
            f"/api/live/rooms/{room_code}/ready"
        ).status_code, 200)
        self.assertEqual(host.post(
            f"/api/live/rooms/{room_code}/start"
        ).status_code, 409)
        self.assertEqual(guest.post(
            f"/api/live/rooms/{room_code}/ready"
        ).status_code, 200)
        return host, guest, room_code

    def test_new_training_missions_have_server_defined_answer_options(self):
        for challenge_id in ("mission-019", "mission-020", "mission-021"):
            challenge = get_challenge(challenge_id)
            self.assertIsNotNone(challenge)
            option_ids = {
                str(option["id"])
                for option in challenge["options"]
            }
            self.assertIn(challenge["correct_answer"], option_ids)
            self.assertGreaterEqual(len(option_ids), 2)

    def test_host_guest_readiness_membership_and_shared_match(self):
        host, guest, room_code = self.ready_match()
        self.assertEqual(guest.post(
            f"/api/live/rooms/{room_code}/start"
        ).status_code, 403)

        intruder = self.player()
        self.assertEqual(intruder.get(
            f"/api/live/rooms/{room_code}"
        ).status_code, 403)
        self.assertEqual(intruder.get(
            f"/live/{room_code}"
        ).status_code, 403)
        self.assertEqual(intruder.get(
            f"/live/{room_code}/match"
        ).status_code, 403)
        self.assertEqual(intruder.post(
            "/api/live/rooms/join",
            data={"room_code": room_code}
        ).status_code, 409)

        started = host.post(f"/api/live/rooms/{room_code}/start")
        self.assertEqual(started.status_code, 200)
        self.assertEqual(guest.get(
            f"/live/{room_code}/match"
        ).status_code, 200)

        host_state = host.get(
            f"/api/live/rooms/{room_code}/match"
        ).json()
        guest_state = guest.get(
            f"/api/live/rooms/{room_code}/match"
        ).json()
        self.assertEqual(host_state["status"], "active")
        self.assertEqual(
            host_state["challenge"],
            guest_state["challenge"]
        )
        self.assertEqual(
            host_state["deadline_at"],
            guest_state["deadline_at"]
        )
        self.assertNotIn(
            "correct_answer",
            host_state["challenge"]
        )

    def test_server_scoring_and_duplicate_submission_rejection(self):
        host, guest, room_code = self.ready_match()
        self.assertEqual(host.post(
            f"/api/live/rooms/{room_code}/start"
        ).status_code, 200)
        challenge = host.get(
            f"/api/live/rooms/{room_code}/match"
        ).json()["challenge"]
        server_challenge = get_challenge(challenge["id"])
        correct_answer = server_challenge["correct_answer"]
        wrong_answer = next(
            str(option["id"])
            for option in challenge["options"]
            if str(option["id"]) != correct_answer
        )

        self.assertEqual(host.post(
            f"/api/live/rooms/{room_code}/answer",
            data={"answer": ""}
        ).status_code, 422)
        first = host.post(
            f"/api/live/rooms/{room_code}/answer",
            data={"answer": correct_answer}
        )
        self.assertEqual(first.status_code, 200)
        waiting = host.get(
            f"/api/live/rooms/{room_code}/match"
        ).json()
        self.assertEqual(waiting["status"], "active")
        self.assertNotIn("result", waiting)
        self.assertNotIn("correct_answer", waiting["challenge"])
        self.assertEqual(host.post(
            f"/api/live/rooms/{room_code}/answer",
            data={"answer": correct_answer}
        ).status_code, 409)
        self.assertEqual(guest.post(
            f"/api/live/rooms/{room_code}/answer",
            data={"answer": wrong_answer}
        ).status_code, 200)

        host_result = host.get(
            f"/api/live/rooms/{room_code}/match"
        ).json()
        guest_result = guest.get(
            f"/api/live/rooms/{room_code}/match"
        ).json()
        self.assertEqual(host_result["status"], "complete")
        self.assertEqual(
            host_result["result"]["correct_answer"],
            correct_answer
        )
        self.assertTrue(host_result["result"]["your_correct"])
        db = SessionLocal()
        try:
            room = db.query(LiveRoom).filter(
                LiveRoom.room_code == room_code
            ).first()
            scoring = server_challenge["score"]
            expected_bonus = min(
                scoring["max_time_bonus"],
                int(
                    max(
                        0,
                        (room.deadline_at - room.host_answered_at).total_seconds()
                    ) * scoring["time_bonus"]
                )
            )
            self.assertEqual(
                host_result["result"]["your_score"],
                scoring["correct"] + expected_bonus
            )
            self.assertEqual(
                host_result["result"]["points_available"],
                scoring["correct"] + scoring["max_time_bonus"]
            )
        finally:
            db.close()
        self.assertFalse(guest_result["result"]["your_correct"])
        self.assertEqual(guest_result["result"]["your_score"], 0)

    def test_deadline_rejects_late_answers_and_completes_round(self):
        host, guest, room_code = self.ready_match()
        self.assertEqual(host.post(
            f"/api/live/rooms/{room_code}/start"
        ).status_code, 200)

        db = SessionLocal()
        try:
            room = db.query(LiveRoom).filter(
                LiveRoom.room_code == room_code
            ).first()
            room.deadline_at = (
                datetime.now(timezone.utc).replace(tzinfo=None)
                - timedelta(seconds=1)
            )
            db.commit()
        finally:
            db.close()

        late_answer = host.post(
            f"/api/live/rooms/{room_code}/answer",
            data={"answer": "1"}
        )
        self.assertEqual(late_answer.status_code, 409)
        self.assertEqual(
            host.get(
                f"/api/live/rooms/{room_code}/match"
            ).json()["status"],
            "complete"
        )


if __name__ == "__main__":
    unittest.main()
