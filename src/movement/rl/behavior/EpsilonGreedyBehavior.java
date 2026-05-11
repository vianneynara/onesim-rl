package movement.rl.behavior;

import core.Settings;
import lombok.Getter;
import lombok.NonNull;
import movement.MovementModel;
import movement.rl.persistence.EpisodicPersistenceData;

import java.util.*;

/**
 * Epsilon-greedy behavior policy with optional decay parameter
 *
 * @author narwa
 */
public class EpsilonGreedyBehavior implements BehaviorPolicy {

	@Getter
	private double epsilon;
	private final double epsilonDecay;
	private final double minEpsilon;
	private Random random;

	public static final String BEHAVIOR_NS = "BehaviorPolicy.EpsilonGreedy";
	public static final String EPSILON_S = "epsilon";
	public static final String DECAY_S = "epsilonDecay";
	public static final String MIN_EPSILON_S = "minEpsilon";

	/**
	 * Constructor called reflectively by Settings. The {@code _settings} param is unused
	 * because this policy reads its own sub-namespace ({@value #BEHAVIOR_NS}).
	 */
	public EpsilonGreedyBehavior(Settings _settings) {
		Settings behaviorSettings = new Settings(BEHAVIOR_NS);

		this.epsilon = behaviorSettings.getDouble(EPSILON_S, 0.9);
		this.epsilonDecay = behaviorSettings.getDouble(DECAY_S, 0.995);
		this.minEpsilon = behaviorSettings.getDouble(MIN_EPSILON_S, 0.01);

		// use seed from MovementModel for reproducibility
		this.random = MovementModel.getRandom();
		// failsafe in case MovementModel's random is not properly initialized
		if (this.random == null) {
			System.out.println("Warning: MovementModel random not initialized, using new Random() for EpsilonGreedyBehavior");
			this.random = new Random();
		}
	}

	public EpsilonGreedyBehavior(EpsilonGreedyBehavior proto) {
		this.epsilon = proto.epsilon;
		this.epsilonDecay = proto.epsilonDecay;
		this.minEpsilon = proto.minEpsilon;
		this.random = proto.random;
	}

	/**
	 * Decides the use of random or best selection (`arg max Q(s,a)`) using the epsilon as threshold.
	 * Explores if RNG is under epsilon threshold {@link EpsilonGreedyBehavior#epsilon}.
	 *
	 * @param availableActions valid actions to choose from; if empty falls back to {0,1}
	 */
	@Override
	public Integer selectAction(int stateId, Map<Integer, Double> qValues, @NonNull Set<Integer> availableActions) {
		if (random.nextDouble() < epsilon) {
			/* Explore a random action */
			return selectRandomAction(availableActions);
		} else {
			/* Exploit the best action given the state */
			return selectBestAction(qValues, availableActions);
		}
	}

	/**
	 * Called after selection behavioral action within the implementing model.
	 * Decays the epsilon value by multiplying the current epsilon with the decay factor.
	 * The decay process continues until the epsilon value reaches the minimum epsilon threshold.
	 * This ensures the agent to gradually shift to exploitation while still allowing some exploration.
	 * Parameters are unused for Epsilon Greedy.
	 */
	@Override
	public void update(int stateId, int actionIndex, double reward, double prevQ, double prevMaxNextQ, double updatedQ) {
		/* ε_t+1 = max(ε, ε • decay rate) */
		epsilon = Math.max(minEpsilon, epsilon * epsilonDecay);
	}

	/**
	 * Selects a random action from the given set of available actions.
	 * If the set is empty, it will use default an undefined action space (0 and 1) for random selection.
	 *
	 * @param availableActions set of valid action indices to pick from
	 */
	private Integer selectRandomAction(@NonNull Set<Integer> availableActions) {
		Integer[] actionIndexes;

		if (!availableActions.isEmpty()) {
			actionIndexes = availableActions.toArray(new Integer[0]);
		} else {
			actionIndexes = new Integer[]{0, 1};
		}

		return actionIndexes[random.nextInt(actionIndexes.length)];
	}

	/**
	 * Selects the best action given the qValue (`arg max Q(s,a)`).
	 *
	 * @param qValues          is the Q Action-Value
	 * @param availableActions permissible actions
	 * @return Integer index of action
	 */
	private Integer selectBestAction(Map<Integer, Double> qValues, @NonNull Set<Integer> availableActions) {
		List<Integer> bestActions = new ArrayList<>(availableActions.size());
		double maxQ = Double.NEGATIVE_INFINITY;

		for (Integer action : availableActions) {
			Double qValue = qValues.getOrDefault(action, 0.0);

			if (qValue > maxQ) {
				/* Clear all previous similar qValues */
				bestActions.clear();
				bestActions.add(action);
				maxQ = qValue;
			} else if (qValue == maxQ) {
				/* Add equally high q-value action */
				bestActions.add(action);
			}
		}

		return bestActions.get(random.nextInt(bestActions.size()));
	}

	@Override
	public BehaviorPolicy replicate() {
		return new EpsilonGreedyBehavior(this);
	}

	@Override
	public String getName() {
		return "EpsilonGreedyBehavior(ε=" + String.format("%.3f", epsilon) + ")";
	}

	@Override
	public void setRandom(Random random) {
		this.random = random;
	}

	@Override
	public void saveTo(EpisodicPersistenceData epd) {
		epd.epsilon = this.epsilon;
		System.out.println("[EpsilonGreedyBehavior] Saved epsilon of: " + epd.epsilon);
	}

	@Override
	public void loadFrom(EpisodicPersistenceData epd) {
		this.epsilon = epd.epsilon;
		System.out.println("[EpsilonGreedyBehavior] Loaded epsilon of: " + this.epsilon);
	}
}