from automation_master import RewardPolicy, RewardSignals


def test_reward_is_capped_and_explainable():
    result = RewardPolicy().score(
        RewardSignals(
            current_interest=1,
            coverage_gap=1,
            deadline_pressure=1,
            utility=1,
            independent_review_value=1,
        )
    )
    assert result.score == 100
    assert result.proposed_credits == 20
    assert result.components["coverage_gap"] == 24
    assert "bounded=100.000" in result.explanation


def test_reward_exploration_decay_and_hysteresis():
    policy = RewardPolicy()
    exploration = policy.score(RewardSignals(utility=0.1))
    assert exploration.score == policy.exploration_floor

    fresh = policy.score(RewardSignals(utility=1))
    stale = policy.score(RewardSignals(utility=1, stale_epochs=3))
    assert stale.score < fresh.score

    held = policy.score(RewardSignals(utility=0.5), previous_score=15)
    assert held.score == 15
    stepped = policy.score(RewardSignals(utility=1), previous_score=5)
    assert stepped.score == 20


def test_penalties_cannot_produce_negative_credit():
    result = RewardPolicy().score(
        RewardSignals(
            cost_per_useful_result=1,
            no_work_rate=1,
            error_rate=1,
            redundancy=1,
        )
    )
    assert result.score == 0
    assert result.proposed_credits == 0
