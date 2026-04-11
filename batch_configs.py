"""
The list of configurations for the batch runner. Starts from index 0.
"""

LIST_OF_CONFIGS = [
    # [ Q-Learning with Epsilon-Greedy
    {
        "alg": "ql",
        "runs": 5,
        "bp": "epsilon",
        "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
        }
    },

    # [ Q-Learning with UCB ]
    {
        "alg": "ql",
        "runs": 5,
        "bp": "ucb",
        "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
        }
    },

    # [ Q-Learning with Thompson Sampling ]
    {
        "alg": "ql",
        "runs": 5,
        "bp": "ts",
        "id": "ql5-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
        }
    }
]