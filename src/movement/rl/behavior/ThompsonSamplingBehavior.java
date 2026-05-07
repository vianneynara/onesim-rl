package movement.rl.behavior;

import core.Settings;
import lombok.Getter;
import lombok.NonNull;
import lombok.Setter;
import movement.MovementModel;
import movement.rl.StateActionPair;
import movement.rl.persistence.EpisodicPersistenceData;

import java.util.*;

/**
 * Thompson Sampling (TS) algorithm in the work.
 * I honestly don't understand much of it.
 *
 * @author narwa
 */
public class ThompsonSamplingBehavior implements BehaviorPolicy {

	private Random random;
	private final double initialVariance;
	private final Map<StateActionPair, TSProperty> tsProperties;

	public static final String BEHAVIOR_NS = "BehaviorPolicy.TS";

	public static final double DEFAULT_INITIAL_VARIANCE = 1.0;

	/**
	 * Constructor called reflectively by Settings. The {@code _settings} param is unused
	 * because this policy reads its own sub-namespace ({@value #BEHAVIOR_NS}).
	 */
	public ThompsonSamplingBehavior(Settings _settings) {
		Settings behaviorSettings = new Settings(BEHAVIOR_NS);

		// use seed from MovementModel for reproducibility
		this.random = MovementModel.getRandom();
		// failsafe in case MovementModel's random is not properly initialized
		if (this.random == null) {
			System.out.println("Warning: MovementModel random not initialized, using new Random() for ThompsonSamplingBehavior");
			this.random = new Random();
		}

		this.initialVariance = behaviorSettings.getDouble("initialVariance", DEFAULT_INITIAL_VARIANCE);
		this.tsProperties = new HashMap<>();
	}

	public ThompsonSamplingBehavior(ThompsonSamplingBehavior proto) {
		this.random = proto.random;
		this.initialVariance = proto.initialVariance;
		this.tsProperties = new HashMap<>(proto.tsProperties);
	}

	/**
	 * Selects an action using the Thompson Sampling formula.
	 *
	 * @param stateId          Current state identifier
	 * @param qValues          Q-values for each action at current state
	 * @param availableActions Set of valid actions to choose from
	 * @return Selected action
	 */
	@Override
	public Integer selectAction(int stateId, Map<Integer, Double> qValues, @NonNull Set<Integer> availableActions) {
		/* Handle empty action set */
		Integer[] actionArray;

		if (availableActions.isEmpty()) {
			System.out.println("[ThompsonSamplingBehavior] No actions available, using default actions of 0 and 1");
			actionArray = new Integer[]{0, 1}; // default actions
		} else {
			actionArray = availableActions.toArray(new Integer[0]);
		}

		/* Now choose the actions using a sampled value from mean and variance */
		double maxSample = Double.NEGATIVE_INFINITY;
		List<Integer> bestActions = new ArrayList<>();

		for (Integer action : actionArray) {
			StateActionPair pair = StateActionPair.of(stateId, action);

			final TSProperty prop = tsProperties.getOrDefault(pair, new TSProperty(0, initialVariance, 0));

			double mean = prop.getMu();
			double variance = prop.getSigma2();

			double sampledValue = retrieveNormalSample(mean, variance);

			if (sampledValue > maxSample) {
				/* Clear all previous similar sample-value and use the better one */
				bestActions.clear();
				bestActions.add(action);
				maxSample = sampledValue;
			} else if (sampledValue == maxSample) {
				/* Add equally high sample-value */
				bestActions.add(action);
			}
		}

		// Randomly select from actions with the highest UCB value
		return bestActions.get(random.nextInt(bestActions.size()));
	}

	/**
	 * Updates the Thompson Sampling posterior distribution based on observed reward.
	 * Uses incremental Bayesian update for both mean (μ) and variance (σ²).
	 *
	 * @param stateId     State where the action was taken
	 * @param actionIndex Action that was taken
	 * @param reward      Observed reward from the action
	 */
	@Override
	public void update(int stateId, int actionIndex, double reward, double prevQ, double prevMaxNextQ, double updatedQ) {
		StateActionPair pair = StateActionPair.of(stateId, actionIndex);
		TSProperty prop = tsProperties.getOrDefault(pair, new TSProperty(0, initialVariance, 0));

		double currMean = prop.getMu();
		double currVariance = prop.getSigma2();
		int currVisitCount = prop.getVisitCount();

		// Increment visit count
		int newVisitCount = currVisitCount + 1;
		prop.incrementVisitCount();

		// Update mean using incremental average: μ_new = μ_old + (r - μ_old) / n
		double updatedMean = currMean + (reward - currMean) / newVisitCount;

		// Update variance using incremental formula for running variance
		// σ²_new = σ²_old + (r - μ_old)(r - μ_new) / n
		double updatedVariance;
		if (newVisitCount == 1) {
			// First observation: initialize variance to a small value or based on reward
			// I don't know which variance is proper for initializing the Thompson Sampling yet
			updatedVariance = initialVariance;
		} else {
			updatedVariance = currVariance + (reward - currMean) * (reward - updatedMean) / newVisitCount;
		}

		// This ensures variance to not exceed 0.000001, avoiding zero
		updatedVariance = Math.max(updatedVariance, 1e-6);

		prop.setMu(updatedMean);
		prop.setSigma2(updatedVariance);

		// Update or insert back into the map
		tsProperties.put(pair, prop);
	}

	@Override
	public BehaviorPolicy replicate() {
		return new ThompsonSamplingBehavior(this);
	}

	@Override
	public String getName() {
		return "ThompsonSamplingBehavior()";
	}

	@Override
	public void setRandom(Random random) {
		this.random = random;
	}

	@Override
	public void saveTo(EpisodicPersistenceData epd) {
		// Save Thompson Sampling state variables to persistence data
		if (epd.tsProperties == null) {
			epd.tsProperties = new HashMap<>();
		}

		for (var entry : tsProperties.entrySet()) {
			// Encode as "stateId:action" key
			String key = entry.getKey().toJsonKey();
			// Encode as "mu,sigma2,visitCount" value
			String value = entry.getValue().toJsonValue();

			epd.tsProperties.put(key, value);
		}
	}

	@Override
	public void loadFrom(EpisodicPersistenceData epd) {
		// Load Thompson Sampling state variables from persistence data
		tsProperties.clear();

		if (epd.tsProperties != null) {
			for (var entry : epd.tsProperties.entrySet()) {
				StateActionPair pair = StateActionPair.fromJsonKey(entry.getKey());
				TSProperty prop = TSProperty.fromJsonValue(entry.getValue());

				tsProperties.put(pair, prop);
			}
		}
	}

	/**
	 * Normal sampling using <a href="https://en.wikipedia.org/wiki/Box%E2%80%93Muller_transform">Box-Muller Transform</a>.
	 * The transformation is used to generate normally distributed random samples from the standard deviation (of variance) and mean.
	 * Used by Thompson Sampling to create random samples from posterior distributions, modeled in Gaussian distribution.
	 *
	 */
	private double retrieveNormalSample(double mean, double variance) {
		double stdDev = Math.sqrt(variance);
		double z = random.nextGaussian();
		return mean + stdDev * z;
	}

	/**
	 * Encapsulated class that contains Thompson Sampling needs, consisting of:
	 * <ul>
	 *     <li>mu, μ the mean Q-values</li>
	 *     <li>sigma^2, σ² the variance</li>
	 *     <li>the visit count</li>
	 * </ul>
	 * This will be keyed using {@link StateActionPair}.
	 *
	 */
	public static class TSProperty {
		@Getter
		@Setter
		private double mu;
		@Getter
		@Setter
		private double sigma2;
		@Getter
		@Setter
		private int visitCount;

		public TSProperty() {
			this.mu = 0.0;
			this.sigma2 = 0.0;
			this.visitCount = 0;
		}

		public TSProperty(double mu, double sigma2, int visitCount) {
			this.mu = mu;
			this.sigma2 = sigma2;
			this.visitCount = visitCount;
		}

		public static TSProperty of(double mu, double sigma2, int visitCount) {
			return new TSProperty(mu, sigma2, visitCount);
		}

		/**
		 * Decodes {@link TSProperty} from format of "mu,sigma2,visitCount".
		 *
		 */
		public static TSProperty fromJsonValue(String jsonValue) {
			String[] valueParts = jsonValue.split(",");

			double mu = Double.parseDouble(valueParts[0]);
			double sigma2 = Double.parseDouble(valueParts[1]);
			int visitCount = Integer.parseInt(valueParts[2]);

			return new TSProperty(mu, sigma2, visitCount);
		}

		/**
		 * Encodes {@link TSProperty} as "mu,sigma2,visitCount" string to be represented in JSON value.
		 *
		 */
		public String toJsonValue() {
			return mu + "," + sigma2 + "," + visitCount;
		}

		public int incrementVisitCount() {
			return ++this.visitCount;
		}
	}
}
