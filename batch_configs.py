"""
The list of configurations for the batch runner. Starts from index 0.
"""

LIST_OF_CONFIGS = [
    # [ Q-Learning with Epsilon-Greedy
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999,
            "eg_me": 0.1,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999,
            "eg_me": 0.1,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999999,
            "eg_me": 0.1,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999999,
            "eg_me": 0.1,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999999,
            "eg_me": 0.1,
            "mcm_fv": True,
        }
    }, #6

    # [ Q-Learning with UCB ]
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.75,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 7.5,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 10.0,
            "mcm_fv": True,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
            "mcm_fv": True,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 2.75,
            "mcm_fv": True,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 3.0,
            "mcm_fv": True,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcm_fv": True,
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
    {"alg": "mc", "runs": 500, "bp": "ts", "id": "mc1-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ts", "id": "mc1-bp=ts",
        "overrides": {
            "ts_iv": 2.0,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ts", "id": "mc1-bp=ts",
        "overrides": {
            "ts_iv": 5.0,
            "mcm_fv": True,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ts", "id": "mc1-bp=ts",
        "overrides": {
            "ts_iv": 10.0,
            "mcm_fv": True,
        }
    },
    
    
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999,
            "eg_me": 0.1,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999,
            "eg_me": 0.1,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999999,
            "eg_me": 0.1,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999999,
            "eg_me": 0.1,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "epsilon", "id": "mc1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999999,
            "eg_me": 0.1,
            "mcm_fv": False,
        }
    },

    # [ Q-Learning with UCB ]
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 7.5,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ucb", "id": "mc1-bp=ucb",
        "overrides": {
            "ucb_ec": 10.0,
            "mcm_fv": False,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
            "mcm_fv": False,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 2.75,
            "mcm_fv": False,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 3.0,
            "mcm_fv": False,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcm_fv": False,
        }
    },

    # [ Q-Learning with Thompson Sampling ]
    {"alg": "mc", "runs": 500, "bp": "ts", "id": "mc1-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ts", "id": "mc1-bp=ts",
        "overrides": {
            "ts_iv": 2.0,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ts", "id": "mc1-bp=ts",
        "overrides": {
            "ts_iv": 5.0,
            "mcm_fv": False,
        }
    },
    {"alg": "mc", "runs": 500, "bp": "ts", "id": "mc1-bp=ts",
        "overrides": {
            "ts_iv": 10.0,
            "mcm_fv": False,
        }
    } #22
]