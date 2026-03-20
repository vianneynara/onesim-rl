package mcrltest.agent;

import core.Settings;
import mcrltest.policy.BehaviorPolicy;
import mcrltest.policy.EpsilonPolicy;
import mcrltest.qModel.RLModel;
import mcrltest.utils.QTable;

import java.util.Random;

public class RLAgent {

    public static final String RLAGENT_NS = "RLAgent";

    /* ===============================
       SETTINGS KEYS
       =============================== */

    public static final String BEHAVIOR_POLICY_S = "behaviorPolicy";
    public static final String RL_MODEL_S = "rlModel";

    public static final String TARGET_PREFIX_S = "targetPrefix";
    public static final String STEP_PENALTY_S = "stepPenalty";
    public static final String FOUND_REWARD_S = "foundReward";
    public static final String SPEED_S = "agentSpeed";
    public static final String TARGET_COOLDOWN_S = "targetCooldown";

    /* persistence */

    public static final String ENABLE_PERSISTENCE = "enablePersistence";
    public static final String FILE_FORMAT = "fileFormat";
//    public static final String EPISODE = "episode";

    /* ===============================
       PARAMETERS
       =============================== */

    protected final String targetPrefix;
    protected final double stepPenalty;
    protected final double foundReward;
    protected final double speed;
    protected final double targetCooldown;

    private final BehaviorPolicy policy;
    private final RLModel rlModel;
    private final Random random;

    /* persistence */

    private final boolean enablePersistence;
    private final String fileFormat;
    private final int episode;

    private boolean loaded = false;

    /* ===============================
       CONSTRUCTOR
       =============================== */

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

        /* -------- PERSISTENCE -------- */

        this.enablePersistence = rlSettings.getBoolean(ENABLE_PERSISTENCE, false);
        this.fileFormat = rlSettings.getSetting(FILE_FORMAT, "csv");
//        this.episode = rlSettings.getInt(EPISODE, 1);
        this.episode = 1;

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
       LOAD QTABLE
       =============================== */

    public void tryLoad() {

        if (!enablePersistence || loaded) {
            return;
        }

        loaded = true;

        try {

            if (fileFormat.equalsIgnoreCase("csv")) {

                rlModel.getQTable().loadFromCSV("data/qtable/qtable_latest.csv");

            } else {

                rlModel.getQTable().loadFromJSON("data/qtable/qtable_latest.json");

            }

            System.out.println("RLAgent: QTable loaded for episode " + episode);

        } catch (Exception e) {

            System.out.println("RLAgent: No previous QTable found. Starting fresh.");
        }
    }

    /* ===============================
       SAVE QTABLE
       =============================== */

    public void trySave() {

        if (!enablePersistence) {
            return;
        }

        double epsilon = getEpsilon();
        double reward = rlModel.getTotalTrainingReward();

        try {

            if (fileFormat.equalsIgnoreCase("csv")) {

                rlModel.getQTable().saveToCSV(
                        "data/qtable/qtable_latest.csv",
                        epsilon,
                        reward,
                        episode
                );

            } else {

                rlModel.getQTable().saveToJSON(
                        "data/qtable/qtable_latest.json",
                        epsilon,
                        reward,
                        episode
                );

            }

            System.out.println("RLAgent: QTable saved for episode " + episode);

        } catch (Exception e) {

            System.out.println("RLAgent: Failed to save QTable.");
            e.printStackTrace();
        }
    }

    /* ===============================
       TRAINING INFO
       =============================== */

    public double getEpsilon() {
        if (policy instanceof EpsilonPolicy) {
            return ((EpsilonPolicy) policy).getEpsilon();
        }
        return 0;
    }

    public double getTotalTrainingReward() {
        return rlModel.getTotalTrainingReward();
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

    public QTable getQTable() {
        return rlModel.getQTable();
    }
}