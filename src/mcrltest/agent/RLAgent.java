package mcrltest.agent;

import core.Settings;
import mcrltest.policy.BehaviorPolicy;
import mcrltest.policy.PolicyPersistence;
import mcrltest.qModel.RLModel;
import mcrltest.utils.EpisodeStep;
import mcrltest.utils.QTable;
import mcrltest.utils.QTableSerializer;
import mcrltest.utils.QTableSerializer.LoadResult;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.*;

public class RLAgent {

    public static final String RLAGENT_NS = "RLAgent";

    /* =============================== SETTINGS =============================== */

    public static final String BEHAVIOR_POLICY_S    = "behaviorPolicy";
    public static final String RL_MODEL_S           = "rlModel";
    public static final String TARGET_PREFIX_S      = "targetPrefix";
    public static final String STEP_PENALTY_S       = "stepPenalty";
    public static final String FOUND_REWARD_S       = "foundReward";
    public static final String SPEED_S              = "agentSpeed";
    public static final String TARGET_COOLDOWN_S    = "targetCooldown";
    public static final String DESTRUCTIVE_TARGET_S = "destructiveTarget";
    public static final String BASE_FOLDER_S        = "baseFolder";
    public static final String CURRENT_EPISODE_S    = "currentEpisode";
    public static final String ENABLE_PERSISTENCE   = "enablePersistence";
    public static final String FILE_FORMAT          = "fileFormat";
    public static final String SAVE_FILE_NAME       = "saveFileName";
    public static final String LOAD_FILE_NAME       = "loadFileName";
    public static final String EPISODE_FILE_NAME    = "episodeFileName";
    public static final String AGENT_SEED           = "agentSeed";

    /* =============================== PARAMETERS =============================== */

    protected final String targetPrefix;
    protected final double stepPenalty;
    protected final double foundReward;
    protected final double speed;
    protected final double targetCooldown;
    private final boolean destructiveTarget;

    private final BehaviorPolicy policy;
    private final RLModel rlModel;
    private final Random random;
    private final int agentSeed;

    private final boolean enablePersistence;
    private final String fileFormat;
    private int episode;

    private final String saveFileName;
    private final String loadFileName;
    private final String episodeFileName;
    private final String baseFolder;

    private static boolean globalLoaded = false;

    private final List<EpisodeStep> episodeSteps;
    private double currentEpisodeReward = 0;

    /* =============================== AGENT STATE =============================== */

    private final Map<String, Object> agentState = new HashMap<>();

    public RLAgent(Settings s) {

        Settings rlSettings = new Settings(RLAGENT_NS);

        this.baseFolder = rlSettings.getSetting(BASE_FOLDER_S, "default");
        this.episode    = rlSettings.getInt(CURRENT_EPISODE_S, 1);

        this.policy = (BehaviorPolicy) s.createIntializedObject(
                rlSettings.getSetting(BEHAVIOR_POLICY_S,
                        "mcrltest.policy.EpsilonGreedyPolicy"));

        this.rlModel = (RLModel) s.createIntializedObject(
                rlSettings.getSetting(RL_MODEL_S,
                        "mcrltest.qModel.QLearningModel"));

        this.targetPrefix      = rlSettings.getSetting(TARGET_PREFIX_S);
        this.stepPenalty       = rlSettings.getDouble(STEP_PENALTY_S, -0.01);
        this.foundReward       = rlSettings.getDouble(FOUND_REWARD_S, 10.0);
        this.speed             = rlSettings.getDouble(SPEED_S, 1.0);
        this.targetCooldown    = rlSettings.getDouble(TARGET_COOLDOWN_S, 0);
        this.destructiveTarget = rlSettings.getBoolean(DESTRUCTIVE_TARGET_S, true);

        this.enablePersistence = rlSettings.getBoolean(ENABLE_PERSISTENCE, false);
        this.fileFormat        = rlSettings.getSetting(FILE_FORMAT, "csv");
        this.saveFileName      = rlSettings.getSetting(SAVE_FILE_NAME, "save_qtable_latest");
        this.loadFileName      = rlSettings.getSetting(LOAD_FILE_NAME, null);
        this.episodeFileName   = rlSettings.getSetting(EPISODE_FILE_NAME, "episode");
        this.agentSeed         = rlSettings.getInt(AGENT_SEED, 0);

        this.random = (agentSeed == 0)
                ? new Random()
                : new Random(agentSeed);

        this.episodeSteps = new ArrayList<>();
    }

    /* =============================== ACTION =============================== */

    public int selectAction(int state) {
        return policy.selectAction(state, rlModel.getQTable(), random);
    }

    /* =============================== LEARNING =============================== */

    public void learn(int state, int action, double reward, int nextState) {
        episodeSteps.add(new EpisodeStep(state, action, reward));
        currentEpisodeReward += reward;

        rlModel.update(state, action, reward, nextState);
        policy.update(state, action, reward, random);
    }

    /* =============================== AGENT STATE =============================== */

    public void setAgentState(Map<String, Object> state) {
        if (state == null) return;

        agentState.clear();
        agentState.putAll(state);
    }

    public Map<String, Object> getAgentState() {
        return agentState;
    }

    /* =============================== LOAD =============================== */

    public void tryLoad() {

        if (!enablePersistence || globalLoaded ||
                loadFileName == null || loadFileName.isEmpty()) return;

        globalLoaded = true;

        try {

            String path = "data/qtable/" + baseFolder + "/" + loadFileName;

            QTable qTable = rlModel.getQTable();

            LoadResult result = fileFormat.equalsIgnoreCase("csv")
                    ? QTableSerializer.loadFromCSV(path + ".csv", qTable)
                    : QTableSerializer.loadFromJSON(path + ".json", qTable);

            if (result == null) {
                System.out.println("⚠️ No save file found.");
                return;
            }

            /* ================= POLICY ================= */

            if (policy instanceof PolicyPersistence) {
                PolicyPersistence p = (PolicyPersistence) policy;

                if (p.getPolicyType().equals(result.policyType)) {
                    p.importState(result.policyData);
                } else {
                    System.out.println("⚠️ Policy type mismatch. Skipping policy load.");
                }
            }

            /* ================= RL MODEL ================= */

            rlModel.setTotalTrainingReward(result.totalReward);
            this.episode = result.episode + 1;

            /* ================= AGENT STATE ================= */

            if (result.agentState != null) {
                agentState.clear();
                agentState.putAll(result.agentState);
            }

            System.out.println("🔥 Loaded episode " + result.episode);

        } catch (Exception e) {
            System.out.println("❌ Failed to load state");
            e.printStackTrace();
        }
    }

    /* =============================== SAVE =============================== */

    public void trySave() {

        if (!enablePersistence) return;

        try {

            String dirPath = "data/qtable/" + baseFolder;
            new File(dirPath).mkdirs();

            String path = dirPath + "/" + saveFileName + "_" + episode;

            if (fileFormat.equalsIgnoreCase("csv")) {

                QTableSerializer.saveToCSV(
                        path + ".csv",
                        rlModel.getQTable(),
                        policy,
                        rlModel.getTotalTrainingReward(),
                        currentEpisodeReward,
                        episode,
                        agentState
                );

            } else {

                QTableSerializer.saveToJSON(
                        path + ".json",
                        rlModel.getQTable(),
                        policy,
                        rlModel.getTotalTrainingReward(),
                        currentEpisodeReward,
                        episode,
                        agentState
                );
            }

            System.out.println("💾 Saved → " + path);

        } catch (Exception e) {
            System.out.println("❌ Failed to save state");
            e.printStackTrace();
        }
    }

    /* =============================== EPISODE SAVE =============================== */

    public void saveEpisodeSteps(double simTime) {
        try {

            String dirPath = "data/episodes/" + baseFolder;
            new File(dirPath).mkdirs();

            String filename = dirPath + "/" +
                    episodeFileName + "_" + episode + "_" + (int) simTime + ".csv";

            PrintWriter pw = new PrintWriter(new FileWriter(filename));
            pw.println("state,action,reward");

            for (EpisodeStep step : episodeSteps) {
                pw.println(step.toCSV());
            }

            pw.close();

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /* =============================== GETTERS =============================== */

    public double getTotalTrainingReward()   { return rlModel.getTotalTrainingReward(); }
    public double getCurrentEpisodeReward()  { return currentEpisodeReward; }
    public int    getEpisode()               { return episode; }
    public double getStepPenalty()           { return stepPenalty; }
    public double getFoundReward()           { return foundReward; }
    public double getSpeed()                 { return speed; }
    public double getTargetCooldown()        { return targetCooldown; }
    public String getTargetPrefix()          { return targetPrefix; }
    public Random getRandom()                { return random; }
    public QTable getQTable()                { return rlModel.getQTable(); }
    public List<EpisodeStep> getEpisodeSteps() { return episodeSteps; }
    public RLModel getRlModel()              { return rlModel; }
    public boolean isDestructiveTarget()     { return destructiveTarget; }
}