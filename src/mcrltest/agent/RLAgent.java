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

    public static final String BASE_FOLDER_S = "baseFolder";
    public static final String CURRENT_EPISODE_S = "currentEpisode";

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

    private final boolean enablePersistence;
    private final String fileFormat;
    private int episode;

    private final String saveFileName;
    private final String loadFileName;
    private final String episodeFileName;

    private final String baseFolder;

    private static boolean globalLoaded = false;

    private final List<EpisodeStep> episodeSteps;

    /* 🔥 NEW: per-episode reward */
    private double currentEpisodeReward = 0;

    public RLAgent(Settings s) {

        Settings rlSettings = new Settings(RLAGENT_NS);

        this.baseFolder = rlSettings.getSetting(BASE_FOLDER_S, "default");
        this.episode = rlSettings.getInt(CURRENT_EPISODE_S, 1);

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
        this.destructiveTarget = rlSettings.getBoolean(DESTRUCTIVE_TARGET_S, true);

        /* -------- PERSISTENCE -------- */

        this.enablePersistence = rlSettings.getBoolean(ENABLE_PERSISTENCE, false);
        this.fileFormat = rlSettings.getSetting(FILE_FORMAT, "csv");

        this.saveFileName = rlSettings.getSetting(SAVE_FILE_NAME, "save_qtable_latest");
        this.loadFileName = rlSettings.getSetting(LOAD_FILE_NAME, null);
        this.episodeFileName = rlSettings.getSetting(EPISODE_FILE_NAME, "episode");

        this.random = new Random();
        this.episodeSteps = new ArrayList<>();
    }

    /* ===============================
       ACTION SELECTION
       =============================== */

    public int selectAction(int state) {
        return policy.selectAction(state, rlModel.getQTable(), random);
    }

    /* ===============================
       LEARNING
       =============================== */

    public void learn(int state, int action, double reward, int nextState) {

        episodeSteps.add(new EpisodeStep(state, action, reward));

        /* 🔥 NEW: accumulate per-episode reward */
        currentEpisodeReward += reward;

        rlModel.update(state, action, reward, nextState);
        policy.update(state, action, reward, random);
    }

    /* ===============================
       LOAD QTABLE
       =============================== */

    public void tryLoad() {

        if (!enablePersistence || globalLoaded ||
                loadFileName == null || loadFileName.isEmpty()) {
            return;
        }

        globalLoaded = true;

        try {

            QTable qTable = rlModel.getQTable();

            String path = "data/qtable/" + baseFolder + "/" + loadFileName;

            if (fileFormat.equalsIgnoreCase("csv")) {
                qTable.loadFromCSV(path + ".csv");
            } else {
                qTable.loadFromJSON(path + ".json");
            }

            syncFromQTable(qTable);

            System.out.println("RLAgent: QTable loaded from " + path);

        } catch (Exception e) {
            System.out.println("RLAgent: No previous QTable found.");
        }
    }

    private void syncFromQTable(QTable qTable) {

        double epsilon = qTable.getLoadedEpsilon();
        double reward = qTable.getLoadedTotalReward();

        if (policy instanceof EpsilonGreedyPolicy) {
            ((EpsilonGreedyPolicy) policy).setEpsilon(epsilon);
        }

        rlModel.setTotalTrainingReward(reward);

        System.out.println("Synced → epsilon=" + epsilon +
                ", reward=" + reward +
                ", episode=" + this.episode);
    }

    /* ===============================
       SAVE QTABLE
       =============================== */

    public void trySave() {

        if (!enablePersistence) return;

        try {

            String dirPath = "data/qtable/" + baseFolder;
            new File(dirPath).mkdirs();

            String path = dirPath + "/" + saveFileName + "_" + episode;

            if (fileFormat.equalsIgnoreCase("csv")) {

                rlModel.getQTable().saveToCSV(
                        path + ".csv",
                        getEpsilon(),
                        rlModel.getTotalTrainingReward(),
                        currentEpisodeReward,   // 🔥 NEW
                        episode
                );

            } else {

                rlModel.getQTable().saveToJSON(
                        path + ".json",
                        getEpsilon(),
                        rlModel.getTotalTrainingReward(),
                        currentEpisodeReward,   // 🔥 NEW
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
       EPISODE SAVE
       =============================== */

    public void saveEpisodeSteps(double simTime) {

        try {

            String dirPath = "data/episodes/" + baseFolder;
            File dir = new File(dirPath);
            if (!dir.exists()) dir.mkdirs();

            String filename = dirPath + "/" +
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

    /* ===============================
       RESET EPISODE
       =============================== */

    public void resetEpisode() {
        episodeSteps.clear();

        /* 🔥 IMPORTANT */
        currentEpisodeReward = 0;

        episode++;
    }

    /* ===============================
       GETTERS
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

    public double getCurrentEpisodeReward() {
        return currentEpisodeReward;
    }

    public int getEpisode() {
        return episode;
    }

    public double getStepPenalty() { return stepPenalty; }
    public double getFoundReward() { return foundReward; }
    public double getSpeed() { return speed; }
    public double getTargetCooldown() { return targetCooldown; }
    public String getTargetPrefix() { return targetPrefix; }
    public Random getRandom() { return random; }
    public QTable getQTable() { return rlModel.getQTable(); }
    public List<EpisodeStep> getEpisodeSteps() { return episodeSteps; }
    public RLModel getRlModel() { return rlModel; }
    public boolean isDestructiveTarget() { return destructiveTarget; }
}