"""
Merged batch configuration.
This consists of:
 - Monte Carlo Learning with (Epsilon-Greedy, Upper Confidence Bound, Posterior Sampling)
 - Q-Learning with (Epsilon-Greedy, Upper Confidence Bound, Posterior Sampling)
 - Lévy Flight Episodic

In detail, exploration strategies specific configurations used:
 a. Epsilon-Greedy (EG): [indices 1-5, 28-32]
 	5 configurations with different exploration decay rates (0.9, 0.95, 0.99, 0.995, 0.999)
 b. Upper Confidence Bound (UCB): [indices 6-15, 33-42]
 	10 configurations with different exploration coefficients (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5)
 c. Posterior Sampling (PS): [indices 16-27, 43-54]
 	12 configurations with different initial variances (0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0) 
	and one configuration using Beta-Binomial Thompson Sampling (BBTS) with posterior reset disabled.

The indices:
 - MC starts from 1 to 27 (27 configs), 
 - QL from 28 to 54 (27 configs), 
 - Lévy Flight Episodic from 55 to 62 (8 configs).
"""

LIST_OF_CONFIGS = [
	# [ Monte Carlo Learning with Epsilon-Greedy ] (indices 1-5: 5)
	# 1
	{
		"alg": "mcn", "runs": 300, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.9,
			"eg_me": 0.1,
			"mcnm_fv": False,
		},
	},
	# 2
	{
		"alg": "mcn", "runs": 300, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.95,
			"eg_me": 0.1,
			"mcnm_fv": False,
		},
	},
	# 3
	{
		"alg": "mcn", "runs": 300, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.99,
			"eg_me": 0.1,
			"mcnm_fv": False,
		},
	},
	# 4
	{
		"alg": "mcn", "runs": 300, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.995,
			"eg_me": 0.1,
			"mcnm_fv": False,
		},
	},
	# 5
	{
		"alg": "mcn", "runs": 300, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
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
		"alg": "mcn", "runs": 300, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 0.25,
			"mcnm_fv": False,
		},
	},
	# 7
	{
		"alg": "mcn", "runs": 300, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 0.5,
			"mcnm_fv": False,
		},
	},
	# 8
	{
		"alg": "mcn", "runs": 300, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 0.75,
			"mcnm_fv": False,
		},
	},
	# 9
	{
		"alg": "mcn", "runs": 300, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 1.0,
			"mcnm_fv": False,
		},
	},
	# 10
	{
		"alg": "mcn", "runs": 300, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 1.25,
			"mcnm_fv": False,
		},
	},
	# 11
	{
		"alg": "mcn", "runs": 300, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 1.5,
			"mcnm_fv": False,
		},
	},
	# 12
	{
		"alg": "mcn", "runs": 300, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 1.75,
			"mcnm_fv": False,
		},
	},
	# 13
	{
		"alg": "mcn", "runs": 300, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 2.0,
			"mcnm_fv": False,
		},
	},
	# 14
	{
		"alg": "mcn", "runs": 300, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 2.25,
			"mcnm_fv": False,
		},
	},
	# 15
	{
		"alg": "mcn", "runs": 300, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
		"overrides": {
			"ucb_ec": 2.5,
			"mcnm_fv": False,
		},
	},

	# [ Monte Carlo Learning with Posterior Sampling ] (indices 16-27: 12)
	## [ Gaussian Thompson Sampling ] (indices 16-26: 11)
	# 16
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps_gts", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_iv": 0.5,
			"mcnm_fv": False,
		},
	},
	# 17
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps_gts", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_iv": 1.0,
			"mcnm_fv": False,
		},
	},
	# 18
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps_gts", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_iv": 2.0,
			"mcnm_fv": False,
		},
	},
	# 19
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps_gts", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_iv": 3.0,
			"mcnm_fv": False,
		},
	},
	# 20
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps_gts", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_iv": 4.0,
			"mcnm_fv": False,
		},
	},
	# 21
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps_gts", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_iv": 5.0,
			"mcnm_fv": False,
		},
	},
	# 22
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps_gts", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_iv": 6.0,
			"mcnm_fv": False,
		},
	},
	# 23
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps_gts", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_iv": 7.0,
			"mcnm_fv": False,
		},
	},
	# 24
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps_gts", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_iv": 8.0,
			"mcnm_fv": False,
		},
	},
	# 25
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps_gts", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_iv": 9.0,
			"mcnm_fv": False,
		},
	},
	# 26
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps_gts", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_iv": 10.0,
			"mcnm_fv": False,
		},
	},

	## [ Beta-Binomial Thompson Sampling ] (index 27: 1)
	# 27
	{
		"alg": "mcn", "runs": 300, "bp": "ps", "group": "mcn_ps", "id": "mcn1-bp=ps",
		"overrides": {
			"ps_betabinomial": True,
			"ps_reset": False,
			"mcnm_fv": False,
		},
	},

	# [ Q-Learning with Epsilon-Greedy ] (indices 28-32: 5)
	# 28
	{
		"alg": "ql", "runs": 300, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.9,
			"eg_me": 0.1,
		},
	},
	# 29
	{
		"alg": "ql", "runs": 300, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.95,
			"eg_me": 0.1,
		},
	},
	# 30
	{
		"alg": "ql", "runs": 300, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.99,
			"eg_me": 0.1,
		},
	},
	# 31
	{
		"alg": "ql", "runs": 300, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.995,
			"eg_me": 0.1,
		},
	},
	# 32
	{
		"alg": "ql", "runs": 300, "bp": "epsilon", "group": "ql_epsilon", "id": "ql5-bp=epsilon",
		"overrides": {
			"eg_ip": 1.0,
			"eg_ed": 0.999,
			"eg_me": 0.1,
		},
	},

	# [ Q-Learning with Upper Confidence Bound ] (indices 33-42: 10)
	# 33
	{
		"alg": "ql", "runs": 300, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 0.5,
		},
	},
	# 34
	{
		"alg": "ql", "runs": 300, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 0.25,
		},
	},
	# 35
	{
		"alg": "ql", "runs": 300, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 0.75,
		},
	},
	# 36
	{
		"alg": "ql", "runs": 300, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 1.0,
		},
	},
	# 37
	{
		"alg": "ql", "runs": 300, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 1.25,
		},
	},
	# 38
	{
		"alg": "ql", "runs": 300, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 1.5,
		},
	},
	# 39
	{
		"alg": "ql", "runs": 300, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 1.75,
		},
	},
	# 40
	{
		"alg": "ql", "runs": 300, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 2.0,
		},
	},
	# 41
	{
		"alg": "ql", "runs": 300, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 2.25,
		},
	},
	# 42
	{
		"alg": "ql", "runs": 300, "bp": "ucb", "group": "ql_ucb", "id": "ql5-bp=ucb",
		"overrides": {
			"ucb_ec": 2.5,
		},
	},

	# [ Q-Learning with Posterior Sampling ] (indices 43-54: 12)
	## [ Gaussian Thompson Sampling ] (indices 43-53: 11)
	# 43
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_gts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_iv": 0.5,
		},
	},
	# 44
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_gts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_iv": 1.0,
		},
	},
	# 45
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_gts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_iv": 2.0,
		},
	},
	# 46
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_gts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_iv": 3.0,
		},
	},
	# 47
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_gts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_iv": 4.0,
		},
	},
	# 48
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_gts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_iv": 5.0,
		},
	},
	# 49
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_gts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_iv": 6.0,
		},
	},
	# 50
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_gts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_iv": 7.0,
		},
	},
	# 51
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_gts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_iv": 8.0,
		},
	},
	# 52
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_gts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_iv": 9.0,
		},
	},
	# 53
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_gts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_iv": 10.0,
		},
	},
	## [ Beta-Binomial Thompson Sampling ] (index 54: 1)
	# 54
	{
		"alg": "ql", "runs": 300, "bp": "ps", "group": "ql_ps_bbts", "id": "ql5-bp=ps",
		"overrides": {
			"ps_betabinomial": True,
			"ps_reset": False,
		},
	},

	# [ Lévy Flight Episodic ] (indices 55-62: 8)
	# 55
	{
		"alg": "lfe", "runs": 300, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 0.25,
		},
	},
	# 56
	{
		"alg": "lfe", "runs": 300, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 0.5,
		},
	},
	# 57
	{
		"alg": "lfe", "runs": 300, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 0.75,
		},
	},
	# 58
	{
		"alg": "lfe", "runs": 300, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 1.0,
		},
	},
	# 59
	{
		"alg": "lfe", "runs": 300, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 1.25,
		},
	},
	# 60
	{
		"alg": "lfe", "runs": 300, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 1.5,
		},
	},
	# 61
	{
		"alg": "lfe", "runs": 300, "group": "lf", "id": "lfe",
		"overrides": {
			"lfe_la": 1.75,
		},
	},
	# 62
	{
		"alg": "lfe", "runs": 300, "group": "lf", "id": "lfe", 
		"overrides": {
			"lfe_la": 2,
		},
	},
]
