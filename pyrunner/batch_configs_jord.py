"""
"""

LIST_OF_CONFIGS = [
    # =========================================================================
    # [ First Visit (mcnm_fv=True) ]
    # =========================================================================

    # --- Epsilon-Greedy | fv=True ---

    # 1
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },

    # 2
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.991,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },

    # 3
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.992,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },

    # 4
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.993,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },

    # 5
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.994,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },

    # 6
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9954,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },

    # 7
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.996,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },

    # 8
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.997,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },

    # 9
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.998,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },

    # 10
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },

    # --- UCB | fv=True ---

    # 11
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "mcnm_fv": True,
        }
    },

    # 12
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.75,
            "mcnm_fv": True,
        }
    },

    # 13
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "mcnm_fv": True,
        }
    },

    # 14
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "mcnm_fv": True,
        }
    },

    # 15
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "mcnm_fv": True,
        }
    },

    # 16
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.25,
            "mcnm_fv": True,
        }
    },

    # 17
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
            "mcnm_fv": True,
        }
    },

    # 18
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.75,
            "mcnm_fv": True,
        }
    },

    # 19
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 3.0,
            "mcnm_fv": True,
        }
    },

    # 20
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcnm_fv": True,
        }
    },

    # --- Posterior Sampling | fv=True ---

    # 21
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 0.5,
            "mcnm_fv": True,
        }
    },

    # 22
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 1.0,
            "mcnm_fv": True,
        }
    },

    # 23
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 2.0,
            "mcnm_fv": True,
        }
    },

    # 24
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 3.0,
            "mcnm_fv": True,
        }
    },

    # 25
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 4.0,
            "mcnm_fv": True,
        }
    },

    # 26
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 5.0,
            "mcnm_fv": True,
        }
    },

    # 27
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 6.0,
            "mcnm_fv": True,
        }
    },

    # 28
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 7.0,
            "mcnm_fv": True,
        }
    },

    # 29
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 8.0,
            "mcnm_fv": True,
        }
    },

    # 30
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 9.0,
            "mcnm_fv": True,
        }
    },

    # 31
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 10.0,
            "mcnm_fv": True,
        }
    },

    # 32
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_betabinomial": True,
            "ps_reset": True,
            "mcnm_fv": True,
        }
    },

    # 33
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_betabinomial": True,
            "ps_reset": False,
            "mcnm_fv": True,
        }
    },


    # =========================================================================
    # [ Every Visit (mcnm_fv=False) ]
    # =========================================================================

    # --- Epsilon-Greedy | fv=False ---

    # 34
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },

    # 35
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.991,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },

    # 36
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.992,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },

    # 37
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.993,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },

    # 38
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.994,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },

    # 39
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9954,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },

    # 40
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.996,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },

    # 41
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.997,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },

    # 42
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.998,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },

    # 43
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },

    # --- UCB | fv=False ---

    # 44
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "mcnm_fv": False,
        }
    },

    # 45
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.75,
            "mcnm_fv": False,
        }
    },

    # 46
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "mcnm_fv": False,
        }
    },

    # 47
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "mcnm_fv": False,
        }
    },

    # 48
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "mcnm_fv": False,
        }
    },

    # 49
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.25,
            "mcnm_fv": False,
        }
    },

    # 50
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
            "mcnm_fv": False,
        }
    },

    # 51
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.75,
            "mcnm_fv": False,
        }
    },

    # 52
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 3.0,
            "mcnm_fv": False,
        }
    },

    # 53
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcnm_fv": False,
        }
    },

    # --- Posterior Sampling | fv=False ---

    # 54
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 0.5,
            "mcnm_fv": False,
        }
    },

    # 55
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 1.0,
            "mcnm_fv": False,
        }
    },

    # 56
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 2.0,
            "mcnm_fv": False,
        }
    },

    # 57
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 3.0,
            "mcnm_fv": False,
        }
    },

    # 58
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 4.0,
            "mcnm_fv": False,
        }
    },

    # 59
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 5.0,
            "mcnm_fv": False,
        }
    },

    # 60
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 6.0,
            "mcnm_fv": False,
        }
    },

    # 61
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 7.0,
            "mcnm_fv": False,
        }
    },

    # 62
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 8.0,
            "mcnm_fv": False,
        }
    },

    # 63
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 9.0,
            "mcnm_fv": False,
        }
    },

    # 64
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_iv": 10.0,
            "mcnm_fv": False,
        }
    },

    # 65
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_betabinomial": True,
            "ps_reset": True,
            "mcnm_fv": False,
        }
    },

    # 66
    {"alg": "mcn", "runs": 500, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
        "overrides": {
            "ps_betabinomial": True,
            "ps_reset": False,
            "mcnm_fv": False,
        }
    },
]