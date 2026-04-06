package mcrltest.policy;

import core.Settings;
import mcrltest.utils.QTable;

import java.util.Random;

public class UCBPolicy implements BehaviorPolicy {

    public static final String UCB_NS = "BehaviorPolicy.UCB";
    public static final String EXPLORATION_C = "c";

    private double c;

    public UCBPolicy(Settings s) {
        Settings set = new Settings(UCB_NS);
        this.c = set.getDouble(EXPLORATION_C, 2.0);
    }

    private UCBPolicy(double c) {
        this.c = c;
    }

    @Override
    public Integer selectAction(int state, QTable qTable, Random random) {

        int nActions = qTable.getNrofAction();

        double totalVisits = 0;

        // total visits of state
        for (int a = 0; a < nActions; a++) {
            totalVisits += qTable.getVisitCount(state, a);
        }

        // 🔥 force exploration if never visited
        for (int a = 0; a < nActions; a++) {
            if (qTable.getVisitCount(state, a) == 0) {
                return a;
            }
        }

        double bestValue = Double.NEGATIVE_INFINITY;
        int bestAction = 0;

        for (int a = 0; a < nActions; a++) {

            double q = qTable.getQValue(state, a);
            double n_sa = qTable.getVisitCount(state, a);

            double ucb = q + c * Math.sqrt(Math.log(totalVisits) / n_sa);

            if (ucb > bestValue) {
                bestValue = ucb;
                bestAction = a;
            }
        }

        return bestAction;
    }

    @Override
    public void update(int state, int action, double reward, Random random) {
        // UCB does not update internal parameters
    }

    @Override
    public BehaviorPolicy replicate() {
        return new UCBPolicy(this.c);
    }

    @Override
    public String getName() {
        return "UCB(c=" + c + ")";
    }
}