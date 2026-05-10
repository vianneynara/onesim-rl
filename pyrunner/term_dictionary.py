ALG_BASE_SETTINGS_PATH = {
    "ql": "settings/skripsi/randomsearch-qlearn.cfg",
    "ql-c-ms@0": "settings/skripsi/randomsearch-qlearn-ql-c-ms@0.cfg",
    "ql-c-ms@1": "settings/skripsi/randomsearch-qlearn-ql-c-ms@1.cfg",
    "ql-p-ms@0": "settings/skripsi/randomsearch-qlearn-ql-p-ms@0.cfg",
    "ql-p-ms@1": "settings/skripsi/randomsearch-qlearn-ql-p-ms@1.cfg",
    "mc": "settings/skripsi/randomsearch-mc.cfg",
    "lfe": "settings/skripsi/randomsearch-lf-episodic.cfg",
    "lfe-c-ms@0": "settings/skripsi/randomsearch-lf-episodic-lfe-c-ms@0.cfg",
    "lfe-c-ms@1": "settings/skripsi/randomsearch-lf-episodic-lfe-c-ms@1.cfg",
    "lfe-p-ms@0": "settings/skripsi/randomsearch-lf-episodic-lfe-p-ms@0.cfg",
    "lfe-p-ms@1": "settings/skripsi/randomsearch-lf-episodic-lfe-p-ms@1.cfg",
}

ALG_ABBREVIATIONS = {
    "ql": "QLearningMovement",
    "mc": "MCMovement",
    "lfe": "LevyFlightEpisodic",
}

BEHAVIOR_PACKAGES = {
    "epsilon": "movement.rl.behavior.EpsilonGreedyBehavior",
    "ucb": "movement.rl.behavior.UCBBehavior",
    "ts": "movement.rl.behavior.ThompsonSamplingBehavior"
}

KEY_ABBREVIATIONS = {
    # [ Agent movement settings ]
    "amm": "Group1.movementModel",
    "tmm": "Group2.movementModel",

    # [ Report settings ]
    "r_dir": "Report.reportDir",

    # [ QLearningMovement settings ]
    "qlm_bp": "QLearningMovement.behaviorPolicy",
    "qlm_lr": "QLearningMovement.learningRate",
    "qlm_df": "QLearningMovement.discountFactor",
    "qlm_iq": "QLearningMovement.initialQValue",
    "qlm_tp": "QLearningMovement.targetPrefix",
    "qlm_sp": "QLearningMovement.stepPenalty",
    "qlm_fr": "QLearningMovement.foundReward",
    "qlm_as": "QLearningMovement.agentSpeed",

    # [ Monte-Carlo Movement settings ]
    "mcm_bp": "MCMovement.behaviorPolicy",
    "mcm_lr": "MCMovement.learningRate",
    "mcm_df": "MCMovement.discountFactor",
    "mcm_iq": "MCMovement.initialQValue",
    "mcm_tp": "MCMovement.targetPrefix",
    "mcm_sp": "MCMovement.stepPenalty",
    "mcm_fr": "MCMovement.foundReward",
    "mcm_as": "MCMovement.agentSpeed",
    "mcm_fv": "MCMovement.firstVisit",

    # [ Lévy Flight Episodic Movement settings ]
    "lfe_la": "LevyFlightEpisodic.levyAlpha",
    "lfe_xm": "LevyFlightEpisodic.xm",
    "lfe_tp": "LevyFlightEpisodic.targetPrefix",
    "lfe_fs": "LevyFlightEpisodic.flightSpeed",
    "lfe_sp": "LevyFlightEpisodic.stepPenalty",
    "lfe_fr": "LevyFlightEpisodic.foundReward",

    # [ EpsilonGreedyBehavior settings ]
    "eg_ip": "BehaviorPolicy.EpsilonGreedy.epsilon",
    "eg_ed": "BehaviorPolicy.EpsilonGreedy.epsilonDecay",
    "eg_me": "BehaviorPolicy.EpsilonGreedy.minEpsilon",
    "eg_de": "BehaviorPolicy.EpsilonGreedy.decayEpisodically",

    # [ UCBBehavior settings ]
    "ucb_ec": "BehaviorPolicy.UCB.explorationConstant",

    # [ TSBehavior settings ]
    "ts_iv": "BehaviorPolicy.TS.initialVariance",

    # [ EpisodicPersistenceManager settings ]
    "epm_ep": "EpisodicPersistenceManager.episodeNumber",
    "epm_path": "EpisodicPersistenceManager.persistencePath",
    "epm_saves": "EpisodicPersistenceManager.saveEpisodically",

    # [ Movement model settings ]
    "m_seed": "MovementModel.seed",
    "m_ws": "MovementModel.worldSize",

}