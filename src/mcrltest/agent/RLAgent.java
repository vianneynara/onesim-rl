package mcrltest.agent;

import core.Settings;
import mcrltest.policy.BehaviorPolicy;
import mcrltest.qModel.RLModel;
import mcrltest.utils.QTable;

import java.util.Random;

public class RLAgent {

    public static final String RLAGENT_NS = "RLAgent";

    public static final String BEHAVIOR_POLICY_S = "behaviorPolicy";
    public static final String RL_MODEL_S = "rlModel";

    public static final String TARGET_PREFIX_S = "targetPrefix";
    public static final String STEP_PENALTY_S = "stepPenalty";
    public static final String FOUND_REWARD_S = "foundReward";
    public static final String SPEED_S = "agentSpeed";
    public static final String TARGET_COOLDOWN_S = "targetCooldown";

    protected final String targetPrefix;
    protected final double stepPenalty;
    protected final double foundReward;
    protected final double speed;
    protected final double targetCooldown;

    private final BehaviorPolicy policy;
    private final RLModel rlModel;
    private final Random random;

    public RLAgent(Settings s) {

        Settings rlSettings = new Settings(RLAGENT_NS);

        /* -------- POLICY -------- */

        String policyClass = rlSettings.getSetting(
                BEHAVIOR_POLICY_S,
                "mcrltest.policy.EpsilonGreedyPolicy"
        );

        this.policy = (BehaviorPolicy) s.createIntializedObject(policyClass);

        /* -------- RL MODEL -------- */

        String modelClass = rlSettings.getSetting(
                RL_MODEL_S,
                "mcrltest.qModel.QLearningModel"
        );

        this.rlModel = (RLModel) s.createIntializedObject(modelClass);

        /* -------- PARAMETERS -------- */

        this.targetPrefix = rlSettings.getSetting(TARGET_PREFIX_S);
        this.stepPenalty = rlSettings.getDouble(STEP_PENALTY_S, -0.01);
        this.foundReward = rlSettings.getDouble(FOUND_REWARD_S, 10.0);
        this.speed = rlSettings.getDouble(SPEED_S, 1.0);
        this.targetCooldown = rlSettings.getDouble(TARGET_COOLDOWN_S, 0);

        this.random = new Random();
    }

    /* ===============================
       ACTION SELECTION
       =============================== */

    public int selectAction(int state) {

        QTable qTable = rlModel.getQTable();

        return policy.selectAction(state, qTable, random);
    }

    /* ===============================
       LEARNING
       =============================== */

    public void learn(int state, int action, double reward, int nextState) {

        rlModel.update(state, action, reward, nextState);

        policy.update(state, action, reward, random);
    }

    /* ===============================
       GETTERS
       =============================== */

    public double getStepPenalty() {
        return stepPenalty;
    }

    public double getFoundReward() {
        return foundReward;
    }

    public double getSpeed() {
        return speed;
    }

    public double getTargetCooldown() {
        return targetCooldown;
    }

    public String getTargetPrefix() {
        return targetPrefix;
    }

    public Random getRandom() {
        return random;
    }

    public QTable getQTable(){
        return rlModel.getQTable();
    }
}