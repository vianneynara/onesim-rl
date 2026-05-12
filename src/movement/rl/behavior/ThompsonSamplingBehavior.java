package movement.rl.behavior;

import core.Settings;
import lombok.Getter;
import lombok.NonNull;
import lombok.Setter;
import movement.MovementModel;
import movement.rl.StateActionPair;
import movement.rl.persistence.EpisodicPersistenceData;
import movement.util.AdaptedJavaRandom;
import org.apache.commons.math3.distribution.BetaDistribution;
import org.apache.commons.math3.random.RandomGenerator;

import java.util.*;

/**
 * Thompson Sampling (TS) algorithm in the work.
 * I honestly don't understand much of it.
 *
 * @author narwa
 */
public class ThompsonSamplingBehavior implements BehaviorPolicy {

	private Random random;
	/**
	 * Commons-Math RNG adapter backed by {@link #random} to keep sampling reproducible.
	 */
	private RandomGenerator apacheRNG;
	private final double learningRate;
	private final double initialVariance;
	private final boolean usingBayesian;
	private final Map<StateActionPair, TSProperty> tsProperties;

	public static final String BEHAVIOR_NS = "BehaviorPolicy.TS";
	/**
	 * The "learning rate" for updating posterior mean toward the new reward (new Q).
	 * Controlling how quick the mean tracks the Q-value from the Q-Table.
	 * This is an adaptation for the RL environment, where Q value changes continuously during learning.
	 * <p>
	 * Note: Match the learning rate of Q-Learning or Monte Carlo being implemented.
	 * </p>
	 *
	 */
	public static final String LEARNING_RATE_S = "learningRate";
	/**
	 * The initial uncertainty of the posterior distribution for each state-action.
	 * Higher value means agent is more uncertain about all actions (more exploration).
	 * As visit count increases, variance decays monotonically via Bayesian decay: σ²(n) = σ²₀ / (1 + n).
	 *
	 */
	public static final String INITIAL_VARIANCE_S = "initialVariance";

	public static final String USING_BAYESIAN_S = "usingBayesian";

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
		initApacheRng();

		this.learningRate = behaviorSettings.getDouble(LEARNING_RATE_S, 0.01);
		this.initialVariance = behaviorSettings.getDouble(INITIAL_VARIANCE_S, 1.0);
		this.usingBayesian = behaviorSettings.getBoolean(USING_BAYESIAN_S, false);
		this.tsProperties = new HashMap<>();
	}

	public ThompsonSamplingBehavior(ThompsonSamplingBehavior proto) {
		this.random = proto.random;
		initApacheRng();
		this.learningRate = proto.learningRate;
		this.initialVariance = proto.initialVariance;
		this.usingBayesian = proto.usingBayesian;
		this.tsProperties = new HashMap<>(proto.tsProperties);
	}

	private void initApacheRng() {
		// Delegate to the simulator RNG so Commons-Math sampling is reproducible.
		this.apacheRNG = new AdaptedJavaRandom(this.random);
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

			final TSProperty prop = tsProperties.getOrDefault(pair, new TSProperty(0, initialVariance, 0, 0, 0));


			double sampledValue;

			/* Gaussian Thompson Sampling */
			if (!usingBayesian) {
				double mean = prop.getMu();
				double variance = prop.getSigma2();
				sampledValue = retrieveNormalSample(mean, variance);
			}

			/* Bayesian Thompson Sampling */
			else {
				// (Defensive) ensure RNG is initialized even if setRandom() wasn't called through ctor.
				if (apacheRNG == null) {
					initApacheRng();
				}
				BetaDistribution betaDist = new BetaDistribution(
					apacheRNG,
					prop.getSuccessCount() + 1,
					prop.getFailureCount() + 1
				);

				sampledValue = betaDist.sample();
			}

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
		TSProperty prop = tsProperties.getOrDefault(pair, new TSProperty(0, initialVariance, 0, 0, 0));

		/* Gaussian Thompson Sampling (with learning rate) */
		if (!usingBayesian) {
			/* Gaussian Thompson Sampling (with learning rate) */
			double currMean = prop.getMu();
//			double currVariance = prop.getSigma2();
			int currVisitCount = prop.getVisitCount();

			// Increment visit count
			int newVisitCount = currVisitCount + 1;
			prop.incrementVisitCount();

			/* Gaussian Thompson Sampling (with learning rate) */
			// Update mean using incremental average: μ_new = μ_old + (r - μ_old) / n
			double updatedMean = currMean + learningRate * (updatedQ - currMean);

			// Update variance using incremental formula for running variance
			// σ²_new = σ²_old + (r - μ_old)(r - μ_new) / n
			double updatedVariance;
			if (newVisitCount == 1) {
				// First observation: initialize variance to a small value or based on reward
				updatedVariance = initialVariance;
			} else {
				/* Variance: Welford's Algorithm */
//				updatedVariance = currVariance + (reward - currMean) * (reward - updatedMean) / newVisitCount;

				/* Variance: Monotone Bayesian decay */
				updatedVariance = initialVariance / (1.0 + newVisitCount);
			}

			// This ensures variance to not exceed 0.000001, avoiding zero
			updatedVariance = Math.max(updatedVariance, 1e-6);

			prop.setMu(updatedMean);
			prop.setSigma2(updatedVariance);

			// Update or insert back into the map
			tsProperties.put(pair, prop);
		}

		/* Bayesian? Thompson Sampling */
		else {
			int alpha = 1 + prop.getSuccessCount();
			int beta = 1 + prop.getFailureCount();

			/* If the reward is plus, count as success and increase alpha. Beta otherwise. */
			if (reward > 0) {
				alpha++;
			} else {
				beta++;
			}

			/* Calculate mean from Alpha and Beta */
			double updatedMean = (double) alpha / (alpha + beta);
			double updatedVariance = (double) (alpha * beta) / (Math.pow((alpha + beta), 2) * (alpha + beta + 1));

			/* Ensures variance to not exceed 0.000001, avoiding zero */
			updatedVariance = Math.max(updatedVariance, 1e-6);

			/* Update the state-action pair wise TS properties */
			prop.setSuccessCount(alpha - 1);    // decrement by one for consistency
			prop.setFailureCount(beta - 1);        // decrement by one for consistency
			prop.setMu(updatedMean);
			prop.setSigma2(updatedVariance);

			// Update or insert back into the map
			tsProperties.put(pair, prop);
		}
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
		initApacheRng();
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
		@Getter
		@Setter
		private int successCount;
		@Getter
		@Setter
		private int failureCount;

		public TSProperty() {
			this.mu = 0.0;
			this.sigma2 = 0.0;
			this.visitCount = 0;
			this.successCount = 0;
			this.failureCount = 0;
		}

		public TSProperty(double mu, double sigma2, int visitCount, int successCount, int failureCount) {
			this.mu = mu;
			this.sigma2 = sigma2;
			this.visitCount = visitCount;
			this.successCount = successCount;
			this.failureCount = failureCount;
		}

		public static TSProperty of(double mu, double sigma2, int visitCount, int successCount, int failureCount) {
			return new TSProperty(mu, sigma2, visitCount, successCount, failureCount);
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
			int successCount = Integer.parseInt(valueParts[3]);
			int failureCount = Integer.parseInt(valueParts[4]);

			return new TSProperty(mu, sigma2, visitCount, successCount, failureCount);
		}

		/**
		 * Encodes {@link TSProperty} as "mu,sigma2,visitCount" string to be represented in JSON value.
		 *
		 */
		public String toJsonValue() {
			return mu + ","
				+ sigma2 + ","
				+ visitCount + ","
				+ successCount + ","
				+ failureCount;
		}

		public int incrementVisitCount() {
			return ++this.visitCount;
		}
	}
}
