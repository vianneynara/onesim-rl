"""
The list of configurations for the batch runner. Starts from index 0.
"""

LIST_OF_CONFIGS = [
    # [ Q-Learning with Epsilon-Greedy ] (indices 1-15)
    # Decay formula: epsilon = max(0.1, epsilon × d) | 500 episodes: 0.99x (fast), 0.994-0.996 (balanced), 0.997-0.999x (slow)
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.9,
         "eg_ed": 0.99,        # Alternative: fast decay (ε ≈ 0.0066)
         # "eg_ed": 0.999,       # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.99,
         "eg_ed": 0.991,       # Alternative: fast decay
         # "eg_ed": 0.9991,
         #          # "eg_de": true,      # Alternative: slow decay
         "eg_me": 0.1,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.999,
         "eg_ed": 0.992,       # Alternative: fast decay
         # "eg_ed": 0.9992,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.9999,
         "eg_ed": 0.993,       # Alternative: fast decay
         # "eg_ed": 0.9993,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },

    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.99999,
         "eg_ed": 0.994,       # Alternative: fast decay
         # "eg_ed": 0.9994,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.999999,
         "eg_ed": 0.9954,      # Alternative: fast decay
         # "eg_ed": 0.9995,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.9999999,
         "eg_ed": 0.996,       # Alternative: fast decay
         # "eg_ed": 0.9996,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.99999999,
         "eg_ed": 0.997,       # Alternative: fast decay
         # "eg_ed": 0.9997,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.999999999,
         "eg_ed": 0.998,       # Alternative: fast decay
         # "eg_ed": 0.9998,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.9999999999,
         "eg_ed": 0.999,       # Alternative: fast decay
         # "eg_ed": 0.9999,      # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.99999999999,
         "eg_ed": 0.9991,      # Alternative: fast decay
         # "eg_ed": 0.99991,     # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.999999999999,
         "eg_ed": 0.9992,      # Alternative: fast decay
         # "eg_ed": 0.99992,     # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.9999999999999,
         "eg_ed": 0.9993,      # Alternative: fast decay
         # "eg_ed": 0.99993,     # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.99999999999999,
         "eg_ed": 0.9994,      # Alternative: fast decay
         # "eg_ed": 0.99994,     # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
     "overrides": {
         "eg_ip": 1.0,
         # "eg_ed": 0.999999999999999,
         "eg_ed": 0.9995,      # Alternative: fast decay
         # "eg_ed": 0.99995,     # Alternative: slow decay
         "eg_me": 0.1,
         # "eg_de": true,
     }
     },

    # [ Q-Learning with UCB ] (indices 16-27)
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
     },

    # [ Q-Learning with Thompson Sampling ] (indices 28-32)
    {"alg": "ql", "runs": 500, "bp": "ts", "id": "ql5-bp=ts",
     "overrides": {
         "ts_iv": 0.5,
     }
     },
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
     },

    # [ Episodic Lévy Flight ] (indices 33-40)
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
     },
]
