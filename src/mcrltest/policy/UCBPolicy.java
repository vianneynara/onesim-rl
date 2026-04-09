package mcrltest.policy;

import core.Settings;
import mcrltest.utils.QTable;

import java.util.Random;

public class UCBPolicy implements BehaviorPolicy {

    public static final String UCB_NS = "BehaviorPolicy.UCB";
    public static final String EXPLORATION_C = "c";

    /* ===============================
       PARAMETERS
       =============================== */

    private double c;

    /* ===============================
       CONSTRUCTOR
       =============================== */

    public UCBPolicy(Settings s) {
        Settings set = new Settings(UCB_NS);

        // base exploration strength
        this.c = set.getDouble(EXPLORATION_C, 2.0);
    }

    private UCBPolicy(double c) {
        this.c = c;
    }

    /* ===============================
       ACTION SELECTION
       =============================== */

    @Override
    public Integer selectAction(int state, QTable qTable, Random random) {

        int nActions = qTable.getNrofAction();

        double totalVisits = 0;

        // 🔥 total visits for this state
        for (int a = 0; a < nActions; a++) {
            totalVisits += qTable.getVisitCount(state, a);
        }

        // 🔥 FORCE exploration if any action never tried
        for (int a = 0; a < nActions; a++) {
            if (qTable.getVisitCount(state, a) == 0) {
                return a;
            }
        }

        // 🔥 dynamic exploration coefficient (KEY IMPROVEMENT)
        double dynamicC = c / Math.sqrt(totalVisits + 1);

        double bestValue = Double.NEGATIVE_INFINITY;
        int bestAction = 0;

        for (int a = 0; a < nActions; a++) {

            double q = qTable.getQValue(state, a);
            double n_sa = qTable.getVisitCount(state, a);

            double exploration = dynamicC * Math.sqrt(Math.log(totalVisits + 1) / n_sa);

            double ucb = q + exploration;

            if (ucb > bestValue) {
                bestValue = ucb;
                bestAction = a;
            }
        }

        return bestAction;
    }

    /* ===============================
       UPDATE (NOT USED IN UCB)
       =============================== */

    @Override
    public void update(int state, int action, double reward, Random random) {
        // UCB is stateless → no update needed
    }

    /* ===============================
       REPLICATE
       =============================== */

    @Override
    public BehaviorPolicy replicate() {
        return new UCBPolicy(this.c);
    }

    /* ===============================
       NAME
       =============================== */

    @Override
    public String getName() {
        return "DynamicUCB(c=" + c + ")";
    }
}