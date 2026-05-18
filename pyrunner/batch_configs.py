"""
The list of configurations for the batch runner. Starts from index 0.
"""

LIST_OF_CONFIGS = [
    # [ Q-Learning with Epsilon-Greedy ] (indices 1-10)
    # Decay formula: epsilon = max(0.1, epsilon × d) | 500 episodes: 0.99x (fast), 0.994-0.996 (balanced), 0.997-0.999x (slow)
    {"alg": "ql", "runs": 750, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.9,        # Faster decay
         "eg_ed": 0.99,        # Alternative: fast decay (ε ≈ 0.0066)
         # "eg_ed": 0.999,       # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.91,       # Faster decay
         "eg_ed": 0.991,       # Alternative: fast decay
         # "eg_ed": 0.9991,
         #          # "eg_de": true,      # Alternative: slow decay
         "eg_me": 0.1,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.92,        # Faster decay
         "eg_ed": 0.992,       # Alternative: fast decay
         # "eg_ed": 0.9992,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.93,        # Faster decay
         "eg_ed": 0.993,       # Alternative: fast decay
         # "eg_ed": 0.9993,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },

    {"alg": "ql", "runs": 750, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.94,        # Faster decay
         "eg_ed": 0.994,       # Alternative: fast decay
         # "eg_ed": 0.9994,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.95,        # Faster decay
         "eg_ed": 0.9954,      # Alternative: fast decay
         # "eg_ed": 0.9995,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.96,        # Faster decay
         "eg_ed": 0.996,       # Alternative: fast decay
         # "eg_ed": 0.9996,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.97,        # Faster decay
         "eg_ed": 0.997,       # Alternative: fast decay
         # "eg_ed": 0.9997,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.98,        # Faster decay
         "eg_ed": 0.998,       # Alternative: fast decay
         # "eg_ed": 0.9998,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.99       # Faster decay
         "eg_ed": 0.999,       # Alternative: fast decay
         # "eg_ed": 0.9999,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },

    # [ Q-Learning with UCB ] (indices 11-22)
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 0.5,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 0.75,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 1.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 1.25,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 1.5,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 1.75,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 2.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 2.25,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 2.5,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 2.75,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 3.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
     "overrides": {
         "ucb_ec": 5.0,
     }
     },

    # [ Q-Learning with Thompson Sampling ] (indices 23-33 (34,35 uses Bayesian))
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 0.5,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 1.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 2.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 3.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 4.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 5.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 6.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 7.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 8.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 9.0,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 10.0,
     }
     },
    ## Additional Thompson Sampling that use purer bayesian (alpha-beta) with BetaDistribution sampling
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_bayesian": True,
         "ts_reset": True,
     }
     },
    {"alg": "ql", "runs": 750, "bp": "ts", "group": "ql_ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_bayesian": True,
         "ts_reset": False,
     }
     },

    # [ Episodic Lévy Flight ] (indices 36-43)
    {"alg": "lfe", "runs": 750, "group": "lf", "id": "lfe",
     "overrides": {
         "lfe_la": 0.25,
     }
     },
    {"alg": "lfe", "runs": 750, "group": "lf", "id": "lfe",
     "overrides": {
         "lfe_la": 0.5,
     }
     },
    {"alg": "lfe", "runs": 750, "group": "lf", "id": "lfe",
     "overrides": {
         "lfe_la": 0.75,
     }
     },
    {"alg": "lfe", "runs": 750, "group": "lf", "id": "lfe",
     "overrides": {
         "lfe_la": 1.0,
     }
     },
    {"alg": "lfe", "runs": 750, "group": "lf", "id": "lfe",
     "overrides": {
         "lfe_la": 1.25,
     }
     },
    {"alg": "lfe", "runs": 750, "group": "lf", "id": "lfe",
     "overrides": {
         "lfe_la": 1.5,
     }
     },
    {"alg": "lfe", "runs": 750, "group": "lf", "id": "lfe",
     "overrides": {
         "lfe_la": 1.75,
     }
     },
    {"alg": "lfe", "runs": 750, "group": "lf", "id": "lfe",
     "overrides": {
         "lfe_la": 2,
     }
     },
]
