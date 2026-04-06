package mcrltest.policy;

import core.Settings;
import mcrltest.utils.QTable;

import java.util.Random;

public class ThompsonSamplingPolicy implements BehaviorPolicy {

    public static final String TS_NS = "BehaviorPolicy.Thompson";

    public ThompsonSamplingPolicy(Settings s) {
        // no parameters needed
    }

    private ThompsonSamplingPolicy() {}

    @Override
    public Integer selectAction(int state, QTable qTable, Random random) {

        int nActions = qTable.getNrofAction();

        double bestSample = Double.NEGATIVE_INFINITY;
        int bestAction = 0;

        for (int a = 0; a < nActions; a++) {

            double mean = qTable.getQValue(state, a);
            int count = qTable.getVisitCount(state, a);

            // variance decreases as visits increase
            double variance = 1.0 / (count + 1);
            double std = Math.sqrt(variance);

            // sample from Normal(mean, std)
            double sample = mean + std * random.nextGaussian();

            if (sample > bestSample) {
                bestSample = sample;
                bestAction = a;
            }
        }

        return bestAction;
    }

    @Override
    public void update(int state, int action, double reward, Random random) {
        // Thompson Sampling uses QTable updates only
    }

    @Override
    public BehaviorPolicy replicate() {
        return new ThompsonSamplingPolicy();
    }

    @Override
    public String getName() {
        return "ThompsonSampling";
    }
}