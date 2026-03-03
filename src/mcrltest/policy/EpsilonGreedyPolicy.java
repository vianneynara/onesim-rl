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

        // use seed from MovementModel for reproducibility
        this.random = MovementModel.getRandom();
        // failsafe in case MovementModel's random is not properly initialized
        if (this.random == null) {
            System.out.println("Warning: MovementModel random not initialized, using new Random() for EpsilonGreedyBehavior");
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

    @Override
    public Integer selectAction(int state, QTable qTable) {

        if (random.nextDouble() < epsilon) {
            // Explore
            return random.nextBoolean() ? 1 : 0;
        } else {
            // Exploit
            return qTable.getBestAction(state, random);
        }
    }

    @Override
    public void update(int state, int action, double reward) {
        // Decay epsilon after each step
        epsilon = Math.max(minEpsilon, epsilon * decayRate);
    }

    @Override
    public BehaviorPolicy replicate() {
        return new EpsilonGreedyPolicy(epsilon, minEpsilon, decayRate, random);
    }

    @Override
    public String getName() {
        return "EpsilonGreedyDecay";
    }
}