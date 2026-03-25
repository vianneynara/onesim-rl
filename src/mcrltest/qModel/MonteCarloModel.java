package mcrltest.qModel;

import core.Settings;
import mcrltest.utils.EpisodeStep;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class MonteCarloModel extends RLModel {

    public static final String MC_NS = "MonteCarlo";

    public static final String FIRST_VISIT_S = "firstVisit";

    private final boolean firstVisit;

    public MonteCarloModel(Settings s) {
        super(s);

        Settings mcSettings = new Settings(MC_NS);

        this.firstVisit = mcSettings.getBoolean(FIRST_VISIT_S, true);
    }

    /**
     * NOT USED in Monte Carlo (step-based learning)
     */
    @Override
    public void update(int state, int action, double reward, int nextState) {
        // do nothing
    }

    /**
     * MAIN Monte Carlo update
     */
    public void updateEpisode(List<EpisodeStep> episodeSteps) {

        Set<String> visited = new HashSet<>();

        double G = 0;

        /* iterate backward */
        for (int t = episodeSteps.size() - 1; t >= 0; t--) {

            EpisodeStep step = episodeSteps.get(t);

            int state = step.getState();
            int action = step.getAction();
            double reward = step.getReward();

            G = gamma * G + reward;

            String key = state + "_" + action;

            /* FIRST-VISIT check */
            if (firstVisit && visited.contains(key)) {
                continue;
            }

            visited.add(key);

            double oldQ = getQ(state, action);

            double newQ = oldQ + alpha * (G - oldQ);

            setQ(state, action, newQ);
        }

        totalTrainingReward += G;
    }
}