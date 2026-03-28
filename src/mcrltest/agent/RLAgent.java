package mcrltest.agent;

import core.Settings;
import mcrltest.policy.BehaviorPolicy;
import mcrltest.policy.EpsilonGreedyPolicy;
import mcrltest.policy.EpsilonPolicy;
import mcrltest.qModel.RLModel;
import mcrltest.utils.EpisodeStep;
import mcrltest.utils.QTable;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
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
    public static final String DESTRUCTIVE_TARGET_S = "destructiveTarget";

    /* persistence */
    public static final String ENABLE_PERSISTENCE = "enablePersistence";
    public static final String FILE_FORMAT = "fileFormat";

    public static final String SAVE_FILE_NAME = "saveFileName";
    public static final String LOAD_FILE_NAME = "loadFileName";
    public static final String EPISODE_FILE_NAME = "episodeFileName";

    /* ===============================
       PARAMETERS
       =============================== */

    protected final String targetPrefix;
    protected final double stepPenalty;
    protected final double foundReward;
    protected final double speed;
    protected final double targetCooldown;
    private final boolean destructiveTarget;

    private final BehaviorPolicy policy;
    private final RLModel rlModel;
    private final Random random;

    /* persistence */
    private final boolean enablePersistence;
    private final String fileFormat;
    private int episode;

    private final String saveFileName;
    private final String loadFileName;
    private final String episodeFileName;

    private static boolean globalLoaded = false;

    /* ===============================
       EPISODE DEBUGGING
       =============================== */

    private final List<EpisodeStep> episodeSteps;

    /* ===============================
       CONSTRUCTOR
       =============================== */

    public RLAgent(Settings s) {

        Settings rlSettings = new Settings(RLAGENT_NS);

        /* -------- POLICY -------- */

        String policyClass = rlSettings.getSetting(BEHAVIOR_POLICY_S, "mcrltest.policy.EpsilonGreedyPolicy");

        this.policy = (BehaviorPolicy) s.createIntializedObject(policyClass);

        /* -------- RL MODEL -------- */

        String modelClass = rlSettings.getSetting(RL_MODEL_S, "mcrltest.qModel.QLearningModel");

        this.rlModel = (RLModel) s.createIntializedObject(modelClass);

        /* -------- PARAMETERS -------- */

        this.targetPrefix = rlSettings.getSetting(TARGET_PREFIX_S);
        this.stepPenalty = rlSettings.getDouble(STEP_PENALTY_S, -0.01);
        this.foundReward = rlSettings.getDouble(FOUND_REWARD_S, 10.0);
        this.speed = rlSettings.getDouble(SPEED_S, 1.0);
        this.targetCooldown = rlSettings.getDouble(TARGET_COOLDOWN_S, 0);
        this.destructiveTarget = rlSettings.getBoolean(DESTRUCTIVE_TARGET_S, true);

        /* -------- PERSISTENCE -------- */

        this.enablePersistence = rlSettings.getBoolean(ENABLE_PERSISTENCE, false);
        this.fileFormat = rlSettings.getSetting(FILE_FORMAT, "csv");
        this.episode = 1;

        this.saveFileName = rlSettings.getSetting(SAVE_FILE_NAME, "save_qtable_latest");
        this.loadFileName = rlSettings.getSetting(LOAD_FILE_NAME, null);
        this.episodeFileName = rlSettings.getSetting(EPISODE_FILE_NAME, "episode");

        this.random = new Random();

        /* -------- EPISODE STORAGE -------- */

        this.episodeSteps = new ArrayList<>();
    }

    /* ===============================
       ACTION SELECTION
       =============================== */

    public int selectAction(int state) {

        QTable qTable = rlModel.getQTable();

        return policy.selectAction(state, qTable, random);
    }

    /* ===============================
       LEARNING + LOGGING
       =============================== */

    public void learn(int state, int action, double reward, int nextState) {

        /* 🔥 record step for debugging */
        episodeSteps.add(new EpisodeStep(state, action, reward));

        rlModel.update(state, action, reward, nextState);

        policy.update(state, action, reward, random);
    }

    /* ===============================
       LOAD QTABLE
       =============================== */

    public void tryLoad() {

        if (!enablePersistence || globalLoaded || loadFileName == null || loadFileName.isEmpty()) {
            return;
        }

        globalLoaded = true;

        try {

            QTable qTable = rlModel.getQTable();

            String path = "data/qtable/" + loadFileName;

            if (fileFormat.equalsIgnoreCase("csv")) {

                qTable.loadFromCSV(path + ".csv");

            } else {

                qTable.loadFromJSON(path + ".json");
            }

            syncFromQTable(qTable);
            System.out.println("RLAgent: QTable loaded from " + path);

        } catch (Exception e) {

            System.out.println("RLAgent: No previous QTable found. Starting fresh.");
        }
    }

    /* ===============================
       SYNC FROM QTABLE
       =============================== */

    private void syncFromQTable(QTable qTable) {

        double epsilon = qTable.getLoadedEpsilon();
        double reward = qTable.getLoadedTotalReward();
        this.episode = qTable.getLoadedEpisode() + 1;

        if (policy instanceof EpsilonGreedyPolicy) {
            ((EpsilonGreedyPolicy) policy).setEpsilon(epsilon);
        }

        rlModel.setTotalTrainingReward(reward);

        System.out.println("Synced → epsilon=" + epsilon + ", reward=" + reward + ", episode=" + this.episode);
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

            String path = "data/qtable/" + saveFileName + "_" + episode;

            if (fileFormat.equalsIgnoreCase("csv")) {

                rlModel.getQTable().saveToCSV(
                        path + ".csv",
                        epsilon,
                        reward,
                        episode
                );

            } else {

                rlModel.getQTable().saveToJSON(
                        path + ".json",
                        epsilon,
                        reward,
                        episode
                );
            }

            System.out.println("RLAgent: QTable saved → " + path);

        } catch (Exception e) {

            System.out.println("RLAgent: Failed to save QTable.");
            e.printStackTrace();
        }
    }

    /* ===============================
       EPISODE DEBUG EXPORT
       =============================== */

    public void saveEpisodeSteps(double simTime) {

        try {

            File dir = new File("data/episodes");
            if (!dir.exists()) dir.mkdirs();

            String filename = "data/episodes/" +
                    episodeFileName + "_" + episode + "_" + (int) simTime + ".csv";

            PrintWriter pw = new PrintWriter(new FileWriter(filename));

            pw.println("state,action,reward");

            for (EpisodeStep step : episodeSteps) {
                pw.println(step.toCSV());
            }

            pw.close();

            System.out.println("Episode steps saved → " + filename);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void resetEpisodeSteps() {
        episodeSteps.clear();
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

    public List<EpisodeStep> getEpisodeSteps() {
        return episodeSteps;
    }

    public RLModel getRlModel() {
        return rlModel;
    }

    public boolean isDestructiveTarget() {
        return destructiveTarget;
    }
}