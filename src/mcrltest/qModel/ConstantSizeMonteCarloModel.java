package mcrltest.qModel;

import core.Settings;
import mcrltest.utils.EpisodeStep;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ConstantSizeMonteCarloModel extends MonteCarloModel {

    private final boolean firstVisit;

    public ConstantSizeMonteCarloModel(Settings s) {
        super(s);

        this.firstVisit = super.firstVisit;
    }

    /**
     * TRUE Monte Carlo (First-Visit / Every-Visit)
     */
    @Override
    public void updateEpisode(List<EpisodeStep> episodeSteps) {

        Set<String> visited = new HashSet<>();

        double G = 0;

        /* iterate backward (needed for return G) */
        for (int t = episodeSteps.size() - 1; t >= 0; t--) {

            EpisodeStep step = episodeSteps.get(t);

            int state = step.getState();
            int action = step.getAction();
            double reward = step.getReward();

            /* ===== RETURN CALCULATION ===== */
            G = gamma * G + reward;

            String key = state + "_" + action;

        /* =========================================
           🔴 FIRST-VISIT MONTE CARLO
           ========================================= */
            if (firstVisit) {

                // Skip if (s,a) already updated before in this episode
                if (visited.contains(key)) {
                    continue;
                }

                visited.add(key); // mark as visited
            }

        /* =========================================
           🔵 EVERY-VISIT MONTE CARLO
           ========================================= */
            // If firstVisit == false → this block always runs
            // meaning ALL occurrences are updated

            /* ===== Q UPDATE (SAME FORMULA FOR BOTH) ===== */
            double oldQ = getQ(state, action);

            double newQ = oldQ + alpha * (G - oldQ);

            setQ(state, action, newQ);
            updateVisitCount(state, action);
        }

        /* ===== accumulate episode return ===== */
        totalTrainingReward += G;
    }
}