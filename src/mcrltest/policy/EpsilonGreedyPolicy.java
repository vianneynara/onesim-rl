package mcrltest.policy;

import core.Settings;
import mcrltest.utils.QTable;
import movement.MovementModel;

import java.util.Random;

public class EpsilonGreedyPolicy implements BehaviorPolicy {

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
        this.decayRate = behaviorSettings.getDouble(DECAY_S, 0.995);
        this.minEpsilon = behaviorSettings.getDouble(MIN_EPSILON_S, 0.01);

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

        epsilon = Math.max(minEpsilon, epsilon * decayRate);

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
}