"""
Merged batch configuration.
This consists of:
 - Monte Carlo Learning with (Epsilon-Greedy, Upper Confidence Bound, Posterior Sampling)
 - Q-Learning with (Epsilon-Greedy, Upper Confidence Bound, Posterior Sampling)
 - Lévy Flight Episodic

In detail, exploration strategies specific configurations used:
 a. Epsilon-Greedy (EG): [indices 1-5, 17-21]
 	5 configurations with different exploration decay rates (0.9, 0.95, 0.99, 0.995, 0.999)
 b. Upper Confidence Bound (UCB): [indices 6-15, 22-31]
 	10 configurations with different exploration coefficients (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5)
 c. Posterior Sampling (PS): [indices 16, 32]
 	one configuration using Beta-Binomial Thompson Sampling (BBTS) with posterior reset disabled.

The indices:
 - MC starts from 1 to 16 (16 configs),
 - QL from 17 to 32 (16 configs),
 - Lévy Flight Episodic from 33 to 40 (8 configs).
"""

LIST_OF_CONFIGS = [
	# [ Monte Carlo Learning with Epsilon-Greedy ] (indices 1-5: 5)
	# 1
	{
		"alg": "mcn", "runs": 100, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.9,
			"eg_me": 0.1,
			"mcnm_fv": False,
		},
	},
	# 2
	{
		"alg": "mcn", "runs": 100, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.95,
			"eg_me": 0.1,
			"mcnm_fv": False,
		},
	},
	# 3
	{
		"alg": "mcn", "runs": 100, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.99,
			"eg_me": 0.1,
			"mcnm_fv": False,
		},
	},
	# 4
	{
		"alg": "mcn", "runs": 100, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.995,
			"eg_me": 0.1,
			"mcnm_fv": False,
		},
	},
	# 5
	{
		"alg": "mcn", "runs": 100, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.999,
			"eg_me": 0.1,
			"mcnm_fv": False,
		},
	},

	# [ Monte Carlo Learning with Upper Confidence Bound ] (indices 6-15: 10)
	# 6
	{
		"alg": "mcn", "runs": 100, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 0.25,
			"mcnm_fv": False,
		},
	},
	# 7
	{
		"alg": "mcn", "runs": 100, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 0.5,
			"mcnm_fv": False,
		},
	},
	# 8
	{
		"alg": "mcn", "runs": 100, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 0.75,
			"mcnm_fv": False,
		},
	},
	# 9
	{
		"alg": "mcn", "runs": 100, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 1.0,
			"mcnm_fv": False,
		},
	},
	# 10
	{
		"alg": "mcn", "runs": 100, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 1.25,
			"mcnm_fv": False,
		},
	},
	# 11
	{
		"alg": "mcn", "runs": 100, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 1.5,
			"mcnm_fv": False,
		},
	},
	# 12
	{
		"alg": "mcn", "runs": 100, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 1.75,
			"mcnm_fv": False,
		},
	},
	# 13
	{
		"alg": "mcn", "runs": 100, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 2.0,
			"mcnm_fv": False,
		},
	},
	# 14
	{
		"alg": "mcn", "runs": 100, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 2.25,
			"mcnm_fv": False,
		},
	},
	# 15
	{
		"alg": "mcn", "runs": 100, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 2.5,
			"mcnm_fv": False,
		},
	},

	# [ Monte Carlo Learning with Posterior Sampling ] (index 16: 1)
	## [ Beta-Binomial Thompson Sampling ] (index 16: 1)
	# 16
	{
		"alg": "mcn", "runs": 100, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_betabinomial": True,
			"ps_reset": False,
			"mcnm_fv": False,
		},
	},

	# [ Q-Learning with Epsilon-Greedy ] (indices 17-21: 5)
	# 17
	{
		"alg": "ql", "runs": 100, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.9,
			"eg_me": 0.1,
		},
	},
	# 18
	{
		"alg": "ql", "runs": 100, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.95,
			"eg_me": 0.1,
		},
	},
	# 19
	{
		"alg": "ql", "runs": 100, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.99,
			"eg_me": 0.1,
		},
	},
	# 20
	{
		"alg": "ql", "runs": 100, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.995,
			"eg_me": 0.1,
		},
	},
	# 21
	{
		"alg": "ql", "runs": 100, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.999,
			"eg_me": 0.1,
		},
	},

	# [ Q-Learning with Upper Confidence Bound ] (indices 22-31: 10)
	# 22
	{
		"alg": "ql", "runs": 100, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 0.5,
		},
	},
	# 23
	{
		"alg": "ql", "runs": 100, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 0.25,
		},
	},
	# 24
	{
		"alg": "ql", "runs": 100, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 0.75,
		},
	},
	# 25
	{
		"alg": "ql", "runs": 100, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 1.0,
		},
	},
	# 26
	{
		"alg": "ql", "runs": 100, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 1.25,
		},
	},
	# 27
	{
		"alg": "ql", "runs": 100, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 1.5,
		},
	},
	# 28
	{
		"alg": "ql", "runs": 100, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 1.75,
		},
	},
	# 29
	{
		"alg": "ql", "runs": 100, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 2.0,
		},
	},
	# 30
	{
		"alg": "ql", "runs": 100, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 2.25,
		},
	},
	# 31
	{
		"alg": "ql", "runs": 100, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 2.5,
		},
	},

	# [ Q-Learning with Posterior Sampling ] (index 32: 1)
	## [ Beta-Binomial Thompson Sampling ] (index 32: 1)
	# 32
	{
		"alg": "ql", "runs": 100, "bp": "ps", "group": "ql_ps", "id": "ql5-bp=ps",
		"overrides": {
			"ps_betabinomial": True,
			"ps_reset": False,
		},
	},

	# [ Lévy Flight Episodic ] (indices 33-40: 8)
	# 33
	{
		"alg": "lfe", "runs": 100, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 0.25,
		},
	},
	# 34
	{
		"alg": "lfe", "runs": 100, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 0.5,
		},
	},
	# 35
	{
		"alg": "lfe", "runs": 100, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 0.75,
		},
	},
	# 36
	{
		"alg": "lfe", "runs": 100, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 1.0,
		},
	},
	# 37
	{
		"alg": "lfe", "runs": 100, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 1.25,
		},
	},
	# 38
	{
		"alg": "lfe", "runs": 100, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 1.5,
		},
	},
	# 39
	{
		"alg": "lfe", "runs": 100, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 1.75,
		},
	},
	# 40
	{
		"alg": "lfe", "runs": 100, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 2,
		},
	},
]