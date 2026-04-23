"""
The list of configurations for the batch runner. Starts from index 0.
"""

LIST_OF_CONFIGS = [
    # [ mcn with Epsilon-Greedy
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
#     {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
#         "overrides": {
#             "eg_ip": 1.0,
#             "eg_ed": 0.9999999,
#             "eg_me": 0.1,
#             "mcnm_fv": True,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
#         "overrides": {
#             "eg_ip": 1.0,
#             "eg_ed": 0.99999999,
#             "eg_me": 0.1,
#             "mcnm_fv": True,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
#         "overrides": {
#             "eg_ip": 1.0,
#             "eg_ed": 0.999999999,
#             "eg_me": 0.1,
#             "mcnm_fv": True,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
#         "overrides": {
#             "eg_ip": 1.0,
#             "eg_ed": 0.9999999999,
#             "eg_me": 0.1,
#             "mcnm_fv": True,
#         }
#     },
     #6

    # [ Q-Learning with UCB ]
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "mcnm_fv": True,
        }
    },
#     {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
#         "overrides": {
#             "ucb_ec": 0.75,
#             "mcnm_fv": True,
#         }
#     },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "mcnm_fv": True,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "mcnm_fv": True,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "mcnm_fv": True,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcnm_fv": True,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 7.5,
            "mcnm_fv": True,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 10.0,
            "mcnm_fv": True,
        }
    },
#     {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
#         "overrides": {
#             "ucb_ec": 2.5,
#             "mcnm_fv": True,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
#         "overrides": {
#             "ucb_ec": 2.75,
#             "mcnm_fv": True,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
#         "overrides": {
#             "ucb_ec": 3.0,
#             "mcnm_fv": True,
#         }
#     },
 #18
#     {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
#         "overrides": {
#             "ucb_ec": 7.5,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
#         "overrides": {
#             "ucb_ec": 10.0,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
#         "overrides": {
#             "ucb_ec": 12.5,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
#         "overrides": {
#             "ucb_ec": 15.0,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
#         "overrides": {
#             "ucb_ec": 20.0,
#         }
#     }, #23

    # [ Q-Learning with Thompson Sampling ]
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
            "mcnm_fv": True,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 2.0,
            "mcnm_fv": True,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 5.0,
            "mcnm_fv": True,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 10.0,
            "mcnm_fv": True,
        }
    },
    

    # [ Monte Carlo Every Visit ]
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
#     {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
#         "overrides": {
#             "eg_ip": 1.0,
#             "eg_ed": 0.9999999,
#             "eg_me": 0.1,
#             "mcnm_fv": False,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
#         "overrides": {
#             "eg_ip": 1.0,
#             "eg_ed": 0.99999999,
#             "eg_me": 0.1,
#             "mcnm_fv": False,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
#         "overrides": {
#             "eg_ip": 1.0,
#             "eg_ed": 0.999999999,
#             "eg_me": 0.1,
#             "mcnm_fv": False,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
#         "overrides": {
#             "eg_ip": 1.0,
#             "eg_ed": 0.9999999999,
#             "eg_me": 0.1,
#             "mcnm_fv": False,
#         }
#     },

    # [ Q-Learning with UCB ]
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "mcnm_fv": False,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "mcnm_fv": False,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "mcnm_fv": False,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "mcnm_fv": False,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcnm_fv": False,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 7.5,
            "mcnm_fv": False,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 10.0,
            "mcnm_fv": False,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
            "mcnm_fv": False,
        }
    },
#     {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
#         "overrides": {
#             "ucb_ec": 2.75,
#             "mcnm_fv": False,
#         }
#     },
#     {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
#         "overrides": {
#             "ucb_ec": 3.0,
#             "mcnm_fv": False,
#         }
#     },
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcnm_fv": False,
        }
    },

    # [ Q-Learning with Thompson Sampling ]
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
            "mcnm_fv": False,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 2.0,
            "mcnm_fv": False,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 5.0,
            "mcnm_fv": False,
        }
    },
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 10.0,
            "mcnm_fv": False,
        }
    } #22
]