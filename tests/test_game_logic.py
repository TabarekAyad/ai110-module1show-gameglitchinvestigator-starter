from logic_utils import check_guess, update_score

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result, _ = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result, _ = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result, _ = check_guess(40, 50)
    assert result == "Too Low"

# ── update_score: Too High symmetry fix ──

def test_too_high_deducts_on_even_attempt():
    # Fix: even-attempt Too High no longer rewards +5; deducts 5 like all wrong guesses.
    assert update_score(100, "Too High", attempt_number=0) == 95

def test_too_high_deducts_on_odd_attempt():
    assert update_score(100, "Too High", attempt_number=1) == 95

def test_too_low_deducts():
    assert update_score(100, "Too Low", attempt_number=0) == 95

def test_too_high_and_too_low_equal_penalty():
    # Both wrong-guess outcomes must have identical impact.
    assert update_score(100, "Too High", attempt_number=0) == update_score(100, "Too Low", attempt_number=0)

# ── update_score: Win off-by-one fix ──

def test_win_attempt_0_scores_100():
    # Fix: attempt 0 (0-indexed first guess) now gives full 100 pts.
    assert update_score(0, "Win", attempt_number=0) == 100

def test_win_attempt_1_scores_90():
    assert update_score(0, "Win", attempt_number=1) == 90

def test_win_attempt_9_scores_10_floor():
    # Points floor at 10 regardless of late attempt number.
    assert update_score(0, "Win", attempt_number=9) == 10

def test_win_late_attempt_never_below_floor():
    assert update_score(0, "Win", attempt_number=99) == 10
