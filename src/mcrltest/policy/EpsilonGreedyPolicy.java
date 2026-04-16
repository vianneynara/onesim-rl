package mcrltest.policy;

import core.Settings;
import mcrltest.utils.QTable;
import movement.MovementModel;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class EpsilonGreedyPolicy implements BehaviorPolicy, EpsilonPolicy, PolicyPersistence {

    private double epsilon;
    private final double minEpsilon;
    private final double decayRate;
    private Random random;

    public static final String BEHAVIOR_NS = "BehaviorPolicy.EpsilonGreedy";
    public static final String EPSILON_S = "epsilon";
    public static final String DECAY_S = "epsilonDecay";
    public static final String MIN_EPSILON_S = "minEpsilon";

    public EpsilonGreedyPolicy(Settings s) {
        Settings behaviorSettings = new Settings(BEHAVIOR_NS);

        this.epsilon = behaviorSettings.getDouble(EPSILON_S, 0.9);
        this.decayRate = behaviorSettings.getDouble(DECAY_S, 0.99999);
        this.minEpsilon = behaviorSettings.getDouble(MIN_EPSILON_S, 0.01);

        System.out.println("==============================================================" + epsilon);

        // Use MovementModel RNG for reproducibility
        this.random = MovementModel.getRandom();

        if (this.random == null) {
            System.out.println("Warning: MovementModel random not initialized, using new Random()");
            this.random = new Random();
        }
    }

    public EpsilonGreedyPolicy(double epsilon,
                               double minEpsilon,
                               double decayRate,
                               Random random) {
        this.epsilon = epsilon;
        this.minEpsilon = minEpsilon;
        this.decayRate = decayRate;
        this.random = random;
    }

    /**
     * Select action using epsilon-greedy strategy
     */
    @Override
    public Integer selectAction(int state, QTable qTable, Random random) {

        Random rng = (random != null) ? random : this.random;

        if (rng.nextDouble() < epsilon) {
            // Explore
            return rng.nextBoolean() ? 1 : 0;
        } else {
            // Exploit
            return qTable.getBestAction(state, rng);
        }
    }

    /**
     * Decay epsilon after learning step
     */
    @Override
    public void update(int state, int action, double reward, Random random) {

//        System.out.println("Min epsilon= " + minEpsilon);
//
//        System.out.println("epsilon= " +epsilon);
//        System.out.println("decay= " + decayRate);

        double d = epsilon * decayRate;
        epsilon = Math.max(minEpsilon, d);

//        System.out.println("after decay= " + d);
//        System.out.println("========= NEW EPSILON ===============");
//        System.out.println(epsilon);
//        System.out.println("=====================================");

    }

    /**
     * Clone policy for another agent
     */
    @Override
    public BehaviorPolicy replicate() {

        return new EpsilonGreedyPolicy(
                epsilon,
                minEpsilon,
                decayRate,
                random
        );
    }

    @Override
    public String getName() {
        return "EpsilonGreedyDecay";
    }

    @Override
    public double getEpsilon() {
        return epsilon;
    }

    @Override
    public void setEpsilon(double epsilon) {
        this.epsilon = epsilon;
    }

    /* ===============================
       POLICY PERSISTENCE
       =============================== */

    @Override
    public String getPolicyType() {
        return "EpsilonGreedy";
    }

    @Override
    public Map<String, Object> exportState() {
        Map<String, Object> map = new HashMap<>();
        map.put("epsilon", epsilon);
        map.put("minEpsilon", minEpsilon);
        map.put("decayRate", decayRate);
        return map;
    }

    @Override
    public void importState(Map<String, Object> data) {
        if (data.containsKey("epsilon")) {
            this.epsilon = ((Number) data.get("epsilon")).doubleValue();
        }
    }
}