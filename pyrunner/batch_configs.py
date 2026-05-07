"""
The list of configurations for the batch runner. Starts from index 0.
"""

from decimal import Decimal

LIST_OF_CONFIGS = [
    # [ Q-Learning with Epsilon-Greedy
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999999,
            "eg_me": 0.1,
        }
    }, #6

    # [ Q-Learning with UCB ]
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 0.75,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 1.25,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 1.75,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 2.25,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 2.75,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 3.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
        }
    }, #18
#     {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
#         "overrides": {
#             "ucb_ec": 7.5,
#         }
#     },
#     {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
#         "overrides": {
#             "ucb_ec": 10.0,
#         }
#     },
#     {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
#         "overrides": {
#             "ucb_ec": 12.5,
#         }
#     },
#     {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
#         "overrides": {
#             "ucb_ec": 15.0,
#         }
#     },
#     {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
#         "overrides": {
#             "ucb_ec": 20.0,
#         }
#     }, #23

    # [ Q-Learning with Thompson Sampling ]
    {"alg": "ql", "runs": 500, "bp": "ts", "id": "ql5-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ts", "id": "ql5-bp=ts",
        "overrides": {
            "ts_iv": 2.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ts", "id": "ql5-bp=ts",
        "overrides": {
            "ts_iv": 5.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ts", "id": "ql5-bp=ts",
        "overrides": {
            "ts_iv": 10.0,
        }
    }, #22

    # [ Episodic Lévy Flight ]
    {"alg": "lfe", "runs": 500, "id": "lfe",
        "overrides": {
            "lfe_la": 0.25,
        }
    },
    {"alg": "lfe", "runs": 500, "id": "lfe",
        "overrides": {
            "lfe_la": 0.5,
        }
    },
    {"alg": "lfe", "runs": 500, "id": "lfe",
        "overrides": {
            "lfe_la": 0.75,
        }
    },
    {"alg": "lfe", "runs": 500, "id": "lfe",
        "overrides": {
            "lfe_la": 1.0,
        }
    },
    {"alg": "lfe", "runs": 500, "id": "lfe",
        "overrides": {
            "lfe_la": 1.25,
        }
    },
    {"alg": "lfe", "runs": 500, "id": "lfe",
        "overrides": {
            "lfe_la": 1.5,
        }
    },
    {"alg": "lfe", "runs": 500, "id": "lfe",
        "overrides": {
            "lfe_la": 1.75,
        }
    },
    {"alg": "lfe", "runs": 500, "id": "lfe",
        "overrides": {
            "lfe_la": 2,
        }
    }, #0

    # Additions #31
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999999999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999999999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999999999999,
            "eg_me": 0.1,
        }
    }, # 36
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": Decimal('0.99999999999999999'),
            "eg_me": 0.1,
        }
    }, # 37 beyond this use Decimal
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": Decimal('0.999999999999999999'),
            "eg_me": 0.1,
        }
    }, #39
]