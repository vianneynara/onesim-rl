package mcrltest.qModel;

import core.Settings;
import mcrltest.utils.EpisodeStep;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class SampleAverageMonteCarloModel extends MonteCarloModel {

    private final boolean firstVisit;

    public SampleAverageMonteCarloModel(Settings s) {
        super(s);

        this.firstVisit = super.firstVisit;
    }

    /**
     * MAIN Monte Carlo update
     */
    @Override
    public void updateEpisode(List<EpisodeStep> episodeSteps) {

        Set<String> visited = new HashSet<>();

        double G = 0;
        double episodeReward = 0;

        /* iterate backward */
        for (int t = episodeSteps.size() - 1; t >= 0; t--) {

            EpisodeStep step = episodeSteps.get(t);

            int state = step.getState();
            int action = step.getAction();
            double reward = step.getReward();

            episodeReward += reward;

            /* compute return */
            G = gamma * G + reward;

            String key = state + "_" + action;

        /* =========================
           FIRST-VISIT FILTER
        ========================= */
            if (firstVisit) {
                if (visited.contains(key)) {
                    continue;
                }
                visited.add(key);
            }

        /* =========================
           TEXTBOOK UPDATE
        ========================= */
            updateVisitCount(state, action);

            double oldQ = getQ(state, action);
            double alpha = 1.0 / qTable.getVisitCount(state, action);

            double newQ = oldQ + alpha * (G - oldQ);

            setQ(state, action, newQ);
        }

        /* correct reward accumulation */
        totalTrainingReward += episodeReward;
    }
}