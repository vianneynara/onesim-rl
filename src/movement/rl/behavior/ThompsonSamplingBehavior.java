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
 * Thompson Sampling (TS) behavior policy implementing two distinct exploration strategies:
 * <ul>
 *     <li><b>Bayesian Beta-Binomial Thompson Sampling</b> ({@code usingBayesian = true}):
 *         A true Bayesian approach using Beta-Binomial conjugate priors. Maintains success/failure counts
 *         for each state-action pair and samples from the posterior Beta distribution. Theoretically grounded
 *         with proper uncertainty quantification that decreases as evidence accumulates.
 *     </li>
 *     <li><b>Q-Tracking Posterior Sampling</b> ({@code usingBayesian = false}):
 *         An ad-hoc approach designed to track continuously-updating Q-values from the learning algorithm.
 *         Uses exponential moving average (EMA) with a learning rate to update the posterior mean,
 *         making it adaptive to non-stationary Q-estimates. Variance decays artificially to control exploration.
 *     </li>
 * </ul>
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
	private final boolean resetEpisodically;
	private final Map<StateActionPair, TSProperty> tsProperties;

	public static final String BEHAVIOR_NS = "BehaviorPolicy.TS";
	/**
	 * The "learning rate" for updating posterior mean toward the new reward (new Q).
	 * <p>
	 * <b>Used only in Q-Tracking mode ({@code usingBayesian = false})</b>:
	 * Controls how quickly the posterior mean adapts to Q-value changes from the Q-Table.
	 * This is an adaptation for the RL environment where Q-values change continuously during learning.
	 * Higher values make the mean track Q more aggressively; lower values smooth changes.
	 * </p>
	 * <p>
	 * <b>Note:</b> Should match the learning rate of the Q-Learning or Monte Carlo algorithm being implemented.
	 * </p>
	 */
	public static final String LEARNING_RATE_S = "learningRate";
	/**
	 * The initial uncertainty of the posterior distribution for each state-action.
	 * <p>
	 * <b>In Q-Tracking mode ({@code usingBayesian = false}):</b>
	 * Controls initial variance for Gaussian sampling. Higher value = more uncertain (more exploration).
	 * Variance monotonically decays via artificial decay: σ²(n) = σ²₀ / (1 + n) as visit count increases.
	 * </p>
	 * <p>
	 * <b>In Bayesian mode ({@code usingBayesian = true}):</b>
	 * Not directly used in parameter updates, as posterior variance derives from Beta distribution.
	 * Primarily serves as a reference or unused legacy parameter in this mode.
	 * </p>
	 */
	public static final String INITIAL_VARIANCE_S = "initialVariance";

	/**
	 * Flag to select between two Thompson Sampling variants:
	 * <ul>
	 *   <li>{@code true}: Use true Bayesian Beta-Binomial Thompson Sampling. Posterior is updated via conjugate prior
	 *       rules by counting successes/failures. Variance is theoretically grounded in Beta distribution.</li>
	 *   <li>{@code false}: Use Q-Tracking Posterior Sampling. Posterior mean is updated via exponential moving average
	 *       toward Q-table values. Variance decays artificially. Not a true Bayesian approach but adaptive to non-stationary
	 *       Q-estimates.</li>
	 * </ul>
	 */
	public static final String USING_BAYESIAN_S = "usingBayesian";

	public static final String RESET_EPISODICALLY_S = "resetEpisodically";

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
		this.resetEpisodically = behaviorSettings.getBoolean(RESET_EPISODICALLY_S, false);
		this.tsProperties = new HashMap<>();
	}

	public ThompsonSamplingBehavior(ThompsonSamplingBehavior proto) {
		this.random = proto.random;
		initApacheRng();
		this.learningRate = proto.learningRate;
		this.initialVariance = proto.initialVariance;
		this.usingBayesian = proto.usingBayesian;
		this.resetEpisodically = proto.resetEpisodically;
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

			/* Q-Tracking Posterior Sampling: sample from Gaussian posterior */
			if (!usingBayesian) {
				double mean = prop.getMu();
				double variance = prop.getSigma2();
				sampledValue = retrieveNormalSample(mean, variance);
			}

			/* Bayesian Beta-Binomial Thompson Sampling: sample from Beta posterior */
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
	 * <p>
	 * <b>In Q-Tracking mode ({@code usingBayesian = false}):</b>
	 * Updates mean via exponential moving average toward the new Q-value, and decays variance artificially.
	 * Designed to track continuously-updating Q-table estimates.
	 * </p>
	 * <p>
	 * <b>In Bayesian mode ({@code usingBayesian = true}):</b>
	 * Updates success/failure counts based on reward sign, then derives posterior mean and variance
	 * from the Beta-Binomial conjugate prior. Theoretically sound Bayesian update.
	 * </p>
	 *
	 * @param stateId      State where the action was taken
	 * @param actionIndex  Action that was taken
	 * @param reward       Observed reward from the action
	 * @param prevQ        Previous Q-value (unused in current implementation)
	 * @param prevMaxNextQ Previous max next Q (unused in current implementation)
	 * @param updatedQ     Updated Q-value from the learning algorithm
	 */
	@Override
	public void update(int stateId, int actionIndex, double reward, double prevQ, double prevMaxNextQ, double updatedQ) {
		StateActionPair pair = StateActionPair.of(stateId, actionIndex);
		TSProperty prop = tsProperties.getOrDefault(pair, new TSProperty(0, initialVariance, 0, 0, 0));

		/* Q-Tracking Posterior Sampling (exponential moving average of Q-values) */
		if (!usingBayesian) {
			/* Q-Tracking Posterior Sampling: Update mean using exponential moving average */
			double currMean = prop.getMu();
//			double currVariance = prop.getSigma2();
			int currVisitCount = prop.getVisitCount();

			// Increment visit count
			int newVisitCount = currVisitCount + 1;
			prop.incrementVisitCount();

			/* Update mean via EMA toward updatedQ: μ_new = μ_old + learningRate * (Q_new - μ_old) */
			double updatedMean = currMean + learningRate * (updatedQ - currMean);

			/* Update variance: Artificial decay to control exploration without theoretical grounding */
			double updatedVariance;
			if (newVisitCount == 1) {
				// First observation: initialize variance to initial value
				updatedVariance = initialVariance;
			} else {
				/* Variance: Artificial decay (not derived from Bayesian principles) */
//				updatedVariance = currVariance + (reward - currMean) * (reward - updatedMean) / newVisitCount;

				/* Variance decay: σ²(n) = σ²₀ / (1 + n) */
				updatedVariance = initialVariance / (1.0 + newVisitCount);
			}

			// Ensure variance does not become too small, avoiding numerical issues
			updatedVariance = Math.max(updatedVariance, 1e-6);

			prop.setMu(updatedMean);
			prop.setSigma2(updatedVariance);

			// Update or insert back into the map
			tsProperties.put(pair, prop);
		}

		/* Bayesian Beta-Binomial Thompson Sampling (conjugate prior update) */
		else {
			int alpha = 1 + prop.getSuccessCount();
			int beta = 1 + prop.getFailureCount();

			/* If reward is positive, count as success and increment alpha. Otherwise increment beta. */
			if (reward > 0) {
				alpha++;
			} else {
				beta++;
			}

			/* Derive posterior mean and variance from Beta distribution: mean = α/(α+β) */
			double updatedMean = (double) alpha / (alpha + beta);
			double updatedVariance = (double) (alpha * beta) / (Math.pow((alpha + beta), 2) * (alpha + beta + 1));

			/* Ensure variance does not become too small, avoiding numerical issues */
			updatedVariance = Math.max(updatedVariance, 1e-6);

			/* Update state-action pair with new posterior parameters */
			prop.setSuccessCount(alpha - 1);    // store count (subtract 1 for consistency with initialization)
			prop.setFailureCount(beta - 1);     // store count (subtract 1 for consistency with initialization)
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
		if (!resetEpisodically) {
			// Load Thompson Sampling state variables from persistence data
			tsProperties.clear();

			if (epd.tsProperties != null) {
				for (var entry : epd.tsProperties.entrySet()) {
					StateActionPair pair = StateActionPair.fromJsonKey(entry.getKey());
					TSProperty prop = TSProperty.fromJsonValue(entry.getValue());

					tsProperties.put(pair, prop);
				}
			}
		} else {
			tsProperties.clear();

			System.out.println("[ThompsonSamplingBehavior] Episodic data is not loaded. Reset episodically is TRUE.");
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
	 * Encapsulated class that contains Thompson Sampling state, consisting of:
	 * <ul>
	 *     <li><b>mu (μ):</b> Posterior mean. In Q-Tracking mode: tracks Q-values via EMA.
	 *                        In Bayesian mode: α/(α+β) from Beta distribution.</li>
	 *     <li><b>sigma^2 (σ²):</b> Posterior variance. In Q-Tracking mode: artificial decay σ²₀/(1+n).
	 *                        In Bayesian mode: derived from Beta distribution.</li>
	 *     <li><b>visitCount:</b> Used in Q-Tracking mode to track state-action visits for variance decay.
	 *                        Unused in Bayesian mode.</li>
	 *     <li><b>successCount:</b> Used in Bayesian mode to track positive rewards. Unused in Q-Tracking mode.</li>
	 *     <li><b>failureCount:</b> Used in Bayesian mode to track non-positive rewards. Unused in Q-Tracking mode.</li>
	 * </ul>
	 * This will be keyed using {@link StateActionPair}.
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

//			assert valueParts.length == 3 : "Asserting TRUE (older value): jsonValue:" + jsonValue;

			double mu = Double.parseDouble(valueParts[0]);
			double sigma2 = Double.parseDouble(valueParts[1]);
			int visitCount = Integer.parseInt(valueParts[2]);

			int successCount;
			int failureCount;
			if (valueParts.length != 3) {
				successCount = Integer.parseInt(valueParts[3]);
				failureCount = Integer.parseInt(valueParts[4]);
			} else {
				// Backward compatibility with 3 values (no successCount and failureCount)
				successCount = 0;
				failureCount = 0;
			}

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
