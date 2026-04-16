package mcrltest.policy;

import core.Settings;
import mcrltest.utils.QTable;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class UCBPolicy implements BehaviorPolicy, PolicyPersistence {

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
        this.c = set.getDouble(EXPLORATION_C, 2.0);
    }

    private UCBPolicy(double c) {
        this.c = c;
    }

    /* ===============================
       ACTION SELECTION (FIXED)
       =============================== */

    @Override
    public Integer selectAction(int state, QTable qTable, Random random) {

        int nActions = qTable.getNrofAction();

        double totalVisits = 0;

        for (int a = 0; a < nActions; a++) {
            totalVisits += qTable.getVisitCount(state, a);
        }

        double logTerm = Math.log(totalVisits + 1);

        double bestValue = Double.NEGATIVE_INFINITY;

        int bestAction = random.nextInt(nActions);

        for (int a = 0; a < nActions; a++) {

            double q = qTable.getQValue(state, a);
            double n_sa = qTable.getVisitCount(state, a);

            double ucb;

            if (n_sa == 0) {
                ucb = Double.POSITIVE_INFINITY;
            } else {
                double exploration = c * Math.sqrt(logTerm / n_sa);
                ucb = q + exploration;
            }

            if (ucb > bestValue ||
                    (ucb == bestValue && random.nextBoolean())) {

                bestValue = ucb;
                bestAction = a;
            }
        }

        return bestAction;
    }

    /* ===============================
       UPDATE
       =============================== */

    @Override
    public void update(int state, int action, double reward, Random random) {

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
        return "UCB(c=" + c + ")";
    }

    /* ===============================
       POLICY PERSISTENCE
       =============================== */

    @Override
    public String getPolicyType() {
        return "UCB";
    }

    @Override
    public Map<String, Object> exportState() {
        Map<String, Object> map = new HashMap<>();
        map.put("c", c);
        return map;
    }

    @Override
    public void importState(Map<String, Object> data) {
        if (data.containsKey("c")) {
            this.c = ((Number) data.get("c")).doubleValue();
        }
    }
}