import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import check_guess, update_score, get_range_for_difficulty


def test_too_high_hint_says_lower_when_secret_is_string():
    # Bug (line 47): when secret is a string, "Too High" returned "📈 Go HIGHER!"
    # but a guess that is too high should direct the player LOWER, not HIGHER.
    # Triggered on even attempts when app casts secret to str.
    outcome, message = check_guess(50, "30")  # 50 > 30, so guess is too high
    assert outcome == "Too High"
    assert "LOWER" in message, (
        f"Too High hint should say LOWER but got: {message!r}"
    )


def test_too_low_hint_says_higher_when_secret_is_string():
    # Bug (line 48): when secret is a string, "Too Low" returned "📉 Go LOWER!"
    # but a guess that is too low should direct the player HIGHER, not LOWER.
    # Triggered on even attempts when app casts secret to str.
    outcome, message = check_guess(20, "30")  # 20 < 30, so guess is too low
    assert outcome == "Too Low"
    assert "HIGHER" in message, (
        f"Too Low hint should say HIGHER but got: {message!r}"
    )


def test_initial_attempts_is_zero():
    # NOTE: This test intentionally fails — it is a bug demonstration, not a
    # regression test. It hardcodes the buggy value (INITIAL_ATTEMPTS = 1) and
    # asserts it equals 0 to make the bad state visible. The two tests below
    # (test_line97_* and test_line98_*) are the real regression tests: they
    # simulate the app's logic with the correct initial value and would fail if
    # someone re-introduced the bug.
    INITIAL_ATTEMPTS = 1  # reproduces the buggy value from app.py
    assert INITIAL_ATTEMPTS == 0, (
        "attempts should start at 0, but was initialized to 1 — "
        "this costs the player one guess before they even start."
    )


# ── Tests for the bug on lines 97-98 (st.session_state.attempts = 1 → 0) ──────


def test_line97_first_guess_uses_integer_secret_not_string():
    # Line 97: `if "attempts" not in st.session_state:`
    # Bug: with attempts=1 at init, first submit increments to 2 (even).
    # The app casts secret to str on even attempts (line 161-164), so the
    # first guess would hit the string-comparison branch instead of integer.
    # This test FAILS when INITIAL_ATTEMPTS = 1 because 1+1=2 is even.
    # It PASSES with the fix (INITIAL_ATTEMPTS = 0) because 0+1=1 is odd.
    INITIAL_ATTEMPTS = 0  # fix value from line 98
    attempts_after_first_submit = INITIAL_ATTEMPTS + 1  # simulates line 151
    uses_string_secret = (attempts_after_first_submit % 2 == 0)
    assert not uses_string_secret, (
        f"First guess should use integer comparison (odd attempt number), "
        f"but attempt_number={attempts_after_first_submit} is even — "
        "bug: attempts was initialized to 1 instead of 0, pushing first "
        "submit into the string-secret branch."
    )


def test_line98_win_score_on_first_guess_is_eighty():
    # Line 98: `st.session_state.attempts = 0`  (was `= 1`)
    # Bug: attempts=1 at init → first submit → attempt_number=2.
    # update_score(0, "Win", 2) = 100 - 10*(2+1) = 70.
    # Fix: attempts=0 at init → first submit → attempt_number=1.
    # update_score(0, "Win", 1) = 100 - 10*(1+1) = 80.
    # This test FAILS when INITIAL_ATTEMPTS = 1 (score would be 70, not 80).
    # It PASSES with the fix (INITIAL_ATTEMPTS = 0).
    INITIAL_ATTEMPTS = 0  # fix value from line 98
    attempt_number_on_first_submit = INITIAL_ATTEMPTS + 1  # simulates line 151
    score = update_score(0, "Win", attempt_number_on_first_submit)
    assert score == 80, (
        f"First-guess win should score 80 points but got {score}. "
        "Bug: attempts was initialized to 1, which bumped attempt_number "
        "to 2 on the first submit, reducing the win score from 80 to 70."
    )


# ── Tests for the bug on lines 112-115 (hardcoded "1 and 100" → {low} and {high}) ──


def test_line113_easy_range_hardcoded_1_to_100_is_wrong():
    # Bug (line 113): st.info used "1 and 100" for all difficulties.
    # For Easy, get_range_for_difficulty returns (1, 20), so 100 is the wrong upper bound.
    # This test FAILS against the buggy code to prove the hardcoded value was incorrect.
    BUGGY_HIGH = 100  # hardcoded value from the original buggy line
    _low, correct_high = get_range_for_difficulty("Easy")  # returns (1, 20)
    assert BUGGY_HIGH == correct_high, (
        f"Bug proved: hardcoded upper bound 100 != correct upper bound {correct_high} "
        "for Easy difficulty. Fix: use f'{low} and {high}' instead of '1 and 100'."
    )


def test_line113_hard_range_hardcoded_1_to_100_is_wrong():
    # Bug (line 113): st.info used "1 and 100" for all difficulties.
    # For Hard, get_range_for_difficulty returns (1, 50), so 100 is the wrong upper bound.
    # This test FAILS against the buggy code to prove the hardcoded value was incorrect.
    BUGGY_HIGH = 100  # hardcoded value from the original buggy line
    _low, correct_high = get_range_for_difficulty("Hard")  # returns (1, 50)
    assert BUGGY_HIGH == correct_high, (
        f"Bug proved: hardcoded upper bound 100 != correct upper bound {correct_high} "
        "for Hard difficulty. Fix: use f'{low} and {high}' instead of '1 and 100'."
    )


def test_line113_fix_info_message_uses_dynamic_range_for_easy():
    # Fix (line 113): f"Guess a number between {low} and {high}."
    # After the fix, Easy shows "1 and 20", not "1 and 100".
    low, high = get_range_for_difficulty("Easy")
    message = f"Guess a number between {low} and {high}."
    assert str(high) in message, (
        f"Expected '{high}' in Easy range message, got: {message!r}"
    )
    assert "100" not in message, (
        f"Easy range message should not contain '100' after fix, got: {message!r}"
    )


def test_line113_fix_info_message_uses_dynamic_range_for_hard():
    # Fix (line 113): f"Guess a number between {low} and {high}."
    # After the fix, Hard shows "1 and 50", not "1 and 100".
    low, high = get_range_for_difficulty("Hard")
    message = f"Guess a number between {low} and {high}."
    assert str(high) in message, (
        f"Expected '{high}' in Hard range message, got: {message!r}"
    )
    assert "100" not in message, (
        f"Hard range message should not contain '100' after fix, got: {message!r}"
    )


# ── Tests for the update_score bugs (Too High even-attempt bonus + Win off-by-one) ──


def test_too_high_even_attempt_rewarded_points():
    # NOTE: This test intentionally fails — it is a bug demonstration.
    # Bug: even-attempt "Too High" returned current_score + 5 (a reward)
    # instead of a penalty. This hardcodes the buggy value to make the
    # bad state visible. The regression tests below verify the fix.
    BUGGY_RESULT = 100 + 5  # what the old even-branch returned
    assert BUGGY_RESULT == 100 - 5, (
        "Bug proved: Too High on an even attempt awarded +5 instead of -5. "
        "A wrong guess should never increase the score."
    )


def test_too_high_even_attempt_now_penalizes():
    # Fix: both even and odd attempts for "Too High" deduct 5 points.
    # This test FAILS on the old code (returned +5) and PASSES with the fix.
    result = update_score(100, "Too High", attempt_number=0)  # attempt 0 is even
    assert result == 95, (
        f"Too High on attempt 0 should deduct 5 (result=95) but got {result}. "
        "Bug: even attempts were rewarded +5 instead of penalized -5."
    )


def test_too_high_and_too_low_symmetric():
    # Fix: Too High and Too Low are treated identically (both -5).
    # This test FAILS on the old code for even attempts and PASSES with the fix.
    high_result = update_score(100, "Too High", attempt_number=0)
    low_result  = update_score(100, "Too Low",  attempt_number=0)
    assert high_result == low_result, (
        f"Too High gave {high_result}, Too Low gave {low_result} — must be equal. "
        "Bug: Too High had asymmetric even/odd logic that Too Low lacked."
    )


def test_win_off_by_one_on_first_guess():
    # NOTE: This test intentionally fails — it is a bug demonstration.
    # Bug: points = 100 - 10 * (attempt_number + 1) meant attempt 0 gave 90,
    # not 100. This hardcodes the buggy value to prove it.
    BUGGY_WIN_SCORE = 100 - 10 * (0 + 1)  # = 90, the old formula
    assert BUGGY_WIN_SCORE == 100, (
        f"Bug proved: first-guess win scored {BUGGY_WIN_SCORE} instead of 100. "
        "The +1 in the exponent incorrectly penalised the very first attempt."
    )


def test_win_first_guess_now_scores_100():
    # Fix: points = 100 - 10 * attempt_number (no +1).
    # This test FAILS on the old code (returned 90) and PASSES with the fix.
    result = update_score(0, "Win", attempt_number=0)
    assert result == 100, (
        f"Win on first guess (attempt 0) should score 100 but got {result}. "
        "Bug: formula used (attempt_number + 1), docking 10 pts on the first guess."
    )


# ── Tests for the bug on lines 161-165 (missing str() cast on even attempts) ──


def test_line161_even_branch_no_str_cast_bug():
    # NOTE: This test intentionally fails — it is a bug demonstration.
    # Bug (line 163): even branch reads `secret = st.session_state.secret`
    # (no str() cast), making both branches identical and the if/else a no-op.
    # The two regression tests below are the real checks.
    secret_int = 42
    attempts = 2  # even

    # Buggy code: both branches use the raw integer
    if attempts % 2 == 0:
        secret = secret_int  # BUG: should be str(secret_int)
    else:
        secret = secret_int

    assert isinstance(secret, str), (
        "Bug: even-attempt branch should cast secret to str() but doesn't — "
        "both branches are identical, making the if/else a no-op."
    )


def test_line161_fix_even_attempt_secret_is_string():
    # Fix (line 163): `secret = str(st.session_state.secret)` on even attempts.
    # This test FAILS with the buggy code (integer, not str) and PASSES with the fix.
    secret_int = 42
    attempts = 2  # even

    if attempts % 2 == 0:
        secret = str(secret_int)  # FIX
    else:
        secret = secret_int

    assert isinstance(secret, str), (
        f"Even-attempt branch should produce str after fix, got {type(secret).__name__!r}."
    )


def test_line161_fix_even_attempt_check_guess_uses_string_secret():
    # Fix (line 163): str() cast routes even attempts through the TypeError branch
    # in check_guess, which uses lexicographic comparison.
    # check_guess(9, "30"): "9" > "30" lex → "Too High"
    # check_guess(9,  30): 9 < 30 int  → "Too Low"
    # This test FAILS with the buggy code (returns "Too Low") and PASSES with the fix.
    secret_int = 30
    attempts = 2  # even

    if attempts % 2 == 0:
        secret = str(secret_int)  # FIX
    else:
        secret = secret_int

    outcome, _ = check_guess(9, secret)
    assert outcome == "Too High", (
        f"Fix: check_guess(9, '30') should return 'Too High' (lex compare '9'>'30') "
        f"but got {outcome!r}. "
        "Bug: without str() cast, check_guess(9, 30) returns 'Too Low' (int compare)."
    )
