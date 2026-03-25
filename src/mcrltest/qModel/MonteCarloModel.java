package mcrltest.qModel;

import core.Settings;
import mcrltest.utils.EpisodeStep;

import java.util.List;

public abstract class MonteCarloModel extends RLModel {

    public static final String MC_NS = "MonteCarlo";
    public static final String FIRST_VISIT_S = "firstVisit";

    protected final boolean firstVisit;

    public MonteCarloModel(Settings s) {
        super(s);

        Settings mcSettings = new Settings(MC_NS);
        this.firstVisit = mcSettings.getBoolean(FIRST_VISIT_S, true);
    }

    /**
     * Not used in Monte Carlo
     */
    @Override
    public void update(int state, int action, double reward, int nextState) {
        // do nothing
    }

    /**
     * TRUE Monte Carlo (First-Visit / Every-Visit)
     */
    public void updateEpisode(List<EpisodeStep> episodeSteps){}
}