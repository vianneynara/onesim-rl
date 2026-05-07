package movement;

import core.*;
import movement.rl.persistence.EpisodicPersistable;
import movement.rl.persistence.EpisodicPersistenceData;
import movement.rl.persistence.EpisodicPersistenceManager;
import movement.util.MovUtil;
import report.RewardReporting;
import report.SearchingOccurrencesReporting;
import report.TrajectoryFrequencyReporting;

import java.util.*;

/**
 * Generates movement paths according to human-like behavior,
 * where short steps are more frequent than long ones (Lévy Flight pattern).
 *
 * @see <a href="https://en.wikipedia.org/wiki/L%C3%A9vy_flight">Lévy flight</a>
 * @see <a href="https://ieeexplore.ieee.org/document/5750071">On the Levy-Walk Nature of Human Mobility</a>
 */
public class LevyFlightEpisodic extends MovementModel implements EpisodicPersistable, TrajectoryFrequencyReporting, SearchingOccurrencesReporting, RewardReporting {
	// [ REPORTING VARIABLES ]
	private final Map<Integer, Integer> trajectoryFrequencies;

	private double currentCumulativeReward;
	private double currentEpisodeReward;

	private int currentCumulativeTrueDetections;
	private int currentTrueDetections;
	private final Map<DTNHost, Double> objectiveFound;

	/**
	 * Number of waypoints per path
	 */
	private final double flightSpeed;
	private Coord lastWaypoint;

	/**
	 * Controls how heavy the distribution tail is
	 */
	public static final String LFE_NS = "LevyFlightEpisodic";
	public static final String ALPHA_S = "levyAlpha";
	public static final String XM_S = "xm";
	public static final String TARGET_PREFIX_S = "targetPrefix";
	public static final String STEP_PENALTY_S = "stepPenalty";
	public static final String FOUND_REWARD_S = "foundReward";
	public static final String FLIGHT_SPEED_S = "flightSpeed";
	public static final String TARGET_COOLDOWN_S = "targetCooldown";
	public static final String LEARNING_SEED_S = "learningSeed";

	public static final double DEFAULT_ALPHA = 1.5;
	public static final double DEFAULT_XM = 1;
	public static final String DEFAULT_TARGET_PREFIX = "T";

	private final double xm;
	private final double alpha;

	private final double targetCooldown;

	private final double stepPenalty;
	private final double foundReward;

	/**
	 * The target's prefix
	 */
	private final String targetPrefix;

	/**
	 * An addition to separate learning RNG (used in direction choosing), to create differentiation between
	 * RNG used to initialize locations of the target nodes and the learning behavior. Especially when
	 * we need the same locations of the targets per episode instead of position re-initialization per episode.
	 *
	 */
	public static Random learningRNG;

	// static initialization of all movement models' random number generator
	static {
		DTNSim.registerForReset(LevyFlightEpisodic.class.getCanonicalName());
		reset();
	}

	public LevyFlightEpisodic(Settings _settings) {
		super(_settings);
		Settings s = new Settings(LFE_NS);

		this.trajectoryFrequencies = new HashMap<>();
		this.currentCumulativeReward = 0.0;
		this.currentEpisodeReward = 0.0;
		this.currentCumulativeTrueDetections = 0;
		this.currentTrueDetections = 0;
		this.objectiveFound = new HashMap<>();

		this.targetPrefix = s.getSetting(TARGET_PREFIX_S, DEFAULT_TARGET_PREFIX);
		this.alpha = s.getDouble(ALPHA_S, DEFAULT_ALPHA);
		this.xm = s.getDouble(XM_S, DEFAULT_XM);
		this.flightSpeed = s.getDouble(FLIGHT_SPEED_S, 1.0);
		this.targetCooldown = s.getDouble(TARGET_COOLDOWN_S, 0.0);
		this.stepPenalty = s.getDouble(STEP_PENALTY_S, 0.01);
		this.foundReward = s.getDouble(FOUND_REWARD_S, 10);

		this.lastWaypoint = null;

		// Re/Initializes episodic persistence
		EpisodicPersistenceData epd = EpisodicPersistenceManager.loadIfExists();
		if (epd != null) {
			loadFrom(epd);
		}
	}

	public LevyFlightEpisodic(LevyFlightEpisodic proto) {
		super(proto);

		this.trajectoryFrequencies = new HashMap<>(proto.trajectoryFrequencies);
		this.currentCumulativeReward = proto.currentCumulativeReward;
		this.currentEpisodeReward = proto.currentEpisodeReward;
		this.currentCumulativeTrueDetections = proto.currentCumulativeTrueDetections;
		this.currentTrueDetections = proto.currentTrueDetections;
		this.objectiveFound = new HashMap<>(proto.objectiveFound);

		this.xm = proto.xm;
		this.alpha = proto.alpha;
		this.targetPrefix = proto.targetPrefix;
		this.flightSpeed = proto.flightSpeed;
		this.targetCooldown = proto.targetCooldown;
		this.stepPenalty = proto.stepPenalty;
		this.foundReward = proto.foundReward;

		if (proto.lastWaypoint != null) {
			this.lastWaypoint = new Coord(proto.lastWaypoint.getX(), proto.lastWaypoint.getY());
		} else {
			this.lastWaypoint = null;
		}
	}

	/**
	 * Resets all static fields to default values
	 */
	public static void reset() {
		Settings s = new Settings(LFE_NS);

		/* Initialize seed if not 0, initialize random seed if 0, inherit if not specified. */
		if (s.contains(LEARNING_SEED_S) && s.getInt(LEARNING_SEED_S) != 0) {
			System.out.printf("[%s] Using %s.%s of: %s %n", LevyFlightEpisodic.class.getCanonicalName(), LFE_NS, LEARNING_SEED_S, s.getInt(LEARNING_SEED_S));
			learningRNG = new Random(s.getInt(LEARNING_SEED_S));
		} else if (s.contains(LEARNING_SEED_S) && s.getInt(LEARNING_SEED_S) == 0) {
			System.out.printf("[%s] Using a random learning RNG seed.", LevyFlightEpisodic.class.getCanonicalName());
			learningRNG = new Random();
		} else {
			// Inherit the seed from MovementModel
			System.out.printf("[%s] Using a random learning RNG seed inherited from MovementModel.", LevyFlightEpisodic.class.getCanonicalName());
			Settings movementSettings = new Settings(MOVEMENT_MODEL_NS);
			if (movementSettings.contains(RNG_SEED) && movementSettings.getInt(RNG_SEED) != 0) {
				learningRNG = new Random(movementSettings.getInt(RNG_SEED));
			} else {
				learningRNG = new Random();  // truly random if not set
			}
		}
	}


	@Override
	public void changedConnection(Connection con) {
		if (con.isUp()) {
			// The host
			DTNHost otherNode = con.getOtherNode(getHost());
			if (otherNode != null && !otherNode.getGroupId().equals(getHost().getGroupId())) {
				// Check if the other node matches target prefix
				if (otherNode.getGroupId().startsWith(targetPrefix)) {
					// Increment the cumulative detection count if this is the first time and above cooldown we detect this target
					if (isTrueDetection(otherNode)) {
						this.currentTrueDetections++;
						this.currentEpisodeReward += this.foundReward;
					}
				}
			}
		}
	}

	/**
	 * Computes whether the detected host is found over the cooldown since the last time it was found.
	 *
	 */
	private boolean isTrueDetection(DTNHost targetHost) {
		double currTime = SimClock.getTime();
		double lastTimeFound = this.objectiveFound.getOrDefault(targetHost, 0.0);

		if (lastTimeFound == 0.0 || currTime - lastTimeFound >= targetCooldown) {
			this.objectiveFound.merge(targetHost, currTime, Double::sum);
			return true;
		}
		return false;
	}

	/**
	 * Returns a random initial location for a host on the map.
	 *
	 * @return Random position on the map
	 */
	@Override
	public Coord getInitialLocation() {
		assert rng != null : "MovementModel not initialized!";
		Coord c = randomCoord();
		this.lastWaypoint = c;
		return c;
	}

	@Override
	public Path getPath() {
		Path p = new Path(this.flightSpeed);
		p.addWaypoint(lastWaypoint.clone());

		Coord c = computeNextLevyPoint();
		double distance = lastWaypoint.distance(c);
		int trajLength = (int) distance;
		recordFinishedTrajectory(trajLength);

		double nextX = c.getX();
		double nextY = c.getY();

		// If the straight step would exit the world bounds, bounce off the wall instead.
		if (nextX >= getMaxX() || nextY >= getMaxY() || nextX <= 0 || nextY <= 0) {
			double[] bounced = MovUtil.bounce(lastWaypoint.getX(), lastWaypoint.getY(), nextX, nextY, getMaxX(), getMaxY());
			double bounceX = bounced[0];
			double bounceY = bounced[1];
//			direction = bounced[2]; // reflected direction: unused, because LF is random
			double remainX = bounced[3]; // remaining step X-component after bounce
			double remainY = bounced[4]; // remaining step Y-component after bounce

			// Add the wall-contact point as an intermediate waypoint.
			p.addWaypoint(new Coord(bounceX, bounceY));

			// Continue from the bounce point with the remaining distance.
			nextX = bounceX + remainX;
			nextY = bounceY + remainY;

			// Clamp to bounds in case a corner or very short remaining step still exits.
			nextX = Math.max(0, Math.min(getMaxX(), nextX));
			nextY = Math.max(0, Math.min(getMaxY(), nextY));
		}

		/* Record estimated penalty before simulation ends */

//		double estimatedPenalty = distance * -this.stepPenalty;
//		double currTime = SimClock.getTime();
//		double endTime = SimScenario.getInstance().getEndTime();
//		if (currTime + distance >= endTime) {
//			estimatedPenalty += (endTime - currTime) * this.flightSpeed * this.stepPenalty;
//		}
//		this.currentEpisodeReward += estimatedPenalty;

		double currTime = SimClock.getTime();
		double endTime = SimScenario.getInstance().getEndTime();
		double remainingTime = Math.max(0, endTime - currTime);

		double reachableDistance = remainingTime * this.flightSpeed;
		double executedDistance = Math.min(distance, reachableDistance);

		double estimatedPenalty = -this.stepPenalty * executedDistance;
		this.currentEpisodeReward += estimatedPenalty;

		Coord nextWaypoint = new Coord(nextX, nextY);
		p.addWaypoint(nextWaypoint);

		this.lastWaypoint = c;
		return p;
	}

	@Override
	public LevyFlightEpisodic replicate() {
		return new LevyFlightEpisodic(this);
	}

	/**
	 * Generates a random coordinate within the bounds of the map.
	 */
	protected Coord randomCoord() {
		return new Coord(
			rng.nextDouble() * getMaxX(),
			rng.nextDouble() * getMaxY()
		);
	}

	/**
	 * Performs a Lévy Flight step to determine the next coordinate.
	 */
	protected Coord computeNextLevyPoint() {
		double next_X, next_Y;

		do {
			double step_length = pareto();
			double theta = learningRNG.nextDouble(0, 2 * Math.PI);

			next_X = (int) lastWaypoint.getX() + step_length * Math.cos(theta);
			next_Y = (int) lastWaypoint.getY() + step_length * Math.sin(theta);

		} while (next_X >= getMaxX() || next_Y >= getMaxY() || next_X <= 0 || next_Y <= 0);

		return new Coord(next_X, next_Y);
	}

	/**
	 * Calculates a step length based on the Pareto distribution.
	 *
	 * @return A value representing the step length
	 */
	public double pareto() {
		double u = 1 - rng.nextDouble(); // Ensures u is in (0, 1]
		return this.xm / Math.pow(u, 1 / this.alpha);
	}

	/**
	 * Records a length value to {@link LevyFlightEpisodic#trajectoryFrequencies}.
	 */
	private void recordFinishedTrajectory(int length) {
		if (length <= 0) return;
		trajectoryFrequencies.merge(length, 1, Integer::sum);
	}

	// [ REPORTING METHODS ]

	/* Trajectory Frequency Reporter */

	@Override
	public Map<Integer, Integer> getTrajectoryFrequencies() {
		return trajectoryFrequencies;
	}

	/* Searching Occurrences Reporter */

	@Override
	public int retrieveTrueDetections() {
		return currentTrueDetections;
	}

	@Override
	public int retrieveUniqueDetections() {
		return this.objectiveFound.size();
	}

	/* Reward Reporter */

	@Override
	public double retrieveCurrentReward() {
		return 0;
	}

	/**
	 * Minimizes the process of saving an episode.
	 */
	@Override
	public void saveCurrentEpisode() {
		EpisodicPersistenceData epd = new EpisodicPersistenceData();
		saveTo(epd);
		EpisodicPersistenceManager.save(epd);
	}

	@Override
	public void saveTo(EpisodicPersistenceData epd) {
//		System.out.printf("[%s] Saving persistence data...%n", LevyFlightEpisodic.class.getName());

		/* Saving trajectory recorder */
		epd.trajectoryFrequencies = new HashMap<>();
		for (var entry : trajectoryFrequencies.entrySet()) {
			epd.trajectoryFrequencies.put(String.valueOf(entry.getKey()), entry.getValue());
		}

		/* Saving reward recorder */
		double newTotalReward = this.currentCumulativeReward + this.currentEpisodeReward;
		epd.previousCumulativeReward = this.currentCumulativeReward;
		epd.currentCumulativeReward = newTotalReward;
		epd.currentEpisodeReward = this.currentEpisodeReward;
		this.currentCumulativeReward = newTotalReward;

		/* Saving Total occurrences recorder */
		epd.previousCumulativeTrueDetections = this.currentCumulativeTrueDetections;
		epd.currentCumulativeTrueDetections = this.currentCumulativeTrueDetections + currentTrueDetections;
		epd.currentTrueDetections = currentTrueDetections;
		epd.currentUniqueDetections = retrieveUniqueDetections();
	}

	@Override
	public void loadFrom(EpisodicPersistenceData epd) {
//		System.out.printf("[%s] Loading persistence data...%n", this.getClass().getName());

		/* Loading trajectory recorder */
		trajectoryFrequencies.clear();
		if (epd.trajectoryFrequencies != null) {
			for (var entry : epd.trajectoryFrequencies.entrySet()) {
				this.trajectoryFrequencies.put(Integer.valueOf(entry.getKey()), entry.getValue());
			}
		}

		/* Loading reward recorder */
//		System.out.println("Loading EPD.currentCumulativeReward: " + epd.currentCumulativeReward);
		this.currentCumulativeReward = epd.currentCumulativeReward;
		this.currentEpisodeReward = 0.0;

		/* Loading Total occurrences recorder */
//		System.out.printf("[%s] Reading EPD.currentCumulativeTrueDetections: " + epd.currentCumulativeTrueDetections, this.getClass().getName());
		this.currentCumulativeTrueDetections = epd.currentCumulativeTrueDetections;
	}
}
