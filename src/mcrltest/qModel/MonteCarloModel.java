package mcrltest.qModel;

import core.Settings;
import mcrltest.utils.EpisodeStep;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MonteCarloModel extends RLModel {

    public static final String MC_NS = "MonteCarlo";
    public static final String FIRST_VISIT_S = "firstVisit";

    protected final boolean firstVisit;

    public MonteCarloModel(Settings s) {
        super(s);

        Settings mcSettings = new Settings(MC_NS);
        this.firstVisit = mcSettings.getBoolean(FIRST_VISIT_S, true);
    }

    @Override
    public void update(int state, int action, double reward, int nextState) {}

    /**
     * TRUE Monte Carlo (First-Visit / Every-Visit)
     */
    public void updateEpisode(List<EpisodeStep> episodeSteps) {

        int T = episodeSteps.size();

        double G = 0;
        double episodeReward = 0;

        /* =========================================
           STEP 1: Record FIRST occurrence index
           ========================================= */
        Map<String, Integer> firstOccurrence = new HashMap<>();

        for (int t = 0; t < T; t++) {
            EpisodeStep step = episodeSteps.get(t);

            String key = step.getState() + "_" + step.getAction();

            if (!firstOccurrence.containsKey(key)) {
                firstOccurrence.put(key, t);
            }

            episodeReward += step.getReward();
        }

        /* =========================================
           STEP 2: Backward return computation
           ========================================= */
        for (int t = T - 1; t >= 0; t--) {

            EpisodeStep step = episodeSteps.get(t);

            int state = step.getState();
            int action = step.getAction();
            double reward = step.getReward();

            /* ===== Efficient return ===== */
            G = gamma * G + reward;

            String key = state + "_" + action;

            /* =========================================
               FIRST-VISIT CONTROL (CORRECT)
               ========================================= */
            if (firstVisit) {
                if (firstOccurrence.get(key) != t) {
                    continue; // skip if not first occurrence
                }
            }

            /* =========================================
               SAMPLE-AVERAGE UPDATE
               ========================================= */
            int count = qTable.getVisitCount(state, action) + 1;
            qTable.setVisitCount(state, action, count);

            double oldQ = getQ(state, action);
            double alpha = 1.0 / count;

            double newQ = oldQ + alpha * (G - oldQ);

            setQ(state, action, newQ);
        }

        totalTrainingReward += episodeReward;
    }
}