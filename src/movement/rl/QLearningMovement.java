package movement.rl;

import core.*;
import movement.MovementModel;
import movement.Path;
import movement.rl.behavior.BehaviorPolicy;
import movement.rl.persistence.EpisodicPersistable;
import movement.rl.persistence.EpisodicPersistenceData;
import movement.rl.persistence.EpisodicPersistenceManager;
import report.*;

import java.util.*;

/**
 * Movement implementing Temporal Difference (TD) Off-Policy reinforcement learning, namely Q-Learning.
 * Uses Q-Value to estimate the reward of actions given a state.
 * <p>
 * Problem mapping:
 * <ul>
 *     <li>Action: direction change (a), represented as 0,1 where 0 means no change and 1 means change direction</li>
 *     <li>State: step count (d), represented as n=0,1,2,... where 0 means the agent just recently changes direction</li>
 * </ul>
 * <p>
 * This class is implemented for Informatics final project and thesis work.
 *
 * @author narwa
 *
 */
public class QLearningMovement extends MovementModel implements TrajectoryFrequencyReporting, QTableReporting, RewardReporting, SearchingAgentReporting, SearchingOccurrencesReporting, EpisodicPersistable {
	// [ REPORTING VARIABLES ]
	private final Map<Integer, Integer> trajectoryFrequencies;

	private double currentCumulativeReward;
	private double currentEpisodeReward;

	private int currentCumulativeTrueDetections;

//	// [ EPISODIC VARIABLES]
//	private final int episodeNumber;

	// [Bellman equation specific parameters]
	/**
	 * Alpha value, controls the amount of reward to update the Q-value. Values range: [0,1].
	 * Lower value means less learning (more stable), while higher value means more learning (volatile).
	 *
	 */
	private double alpha;
	/**
	 * Lambda value, controls how important reward (delayed~immediate). Values range: [0,1].
	 * Lower value means focusing on immediate reward, while higher value means focusing on delayed reward.
	 *
	 */
	private double lambda;
	/**
	 * Stores the initial Q-value, usually at 0.
	 */
	private double initialQValue;

	// [Configuration - Settings Keys]
	public static final String QLEARNING_NS = "QLearningMovement";
	public static final String ALPHA_S = "learningRate";
	public static final String LAMBDA_S = "discountFactor";
	public static final String INITIAL_Q_S = "initialQValue";
	public static final String BEHAVIOR_POLICY_S = "behaviorPolicy";
	public static final String TARGET_PREFIX_S = "targetPrefix";
	public static final String STEP_PENALTY_S = "stepPenalty";
	public static final String FOUND_REWARD_S = "foundReward";
	public static final String SPEED_S = "agentSpeed";
	public static final String TARGET_COOLDOWN_S = "targetCooldown";
	public static final String LEARNING_SEED_S = "learningSeed";

	// [Configuration - Fixed parameters]
	private final double agentSpeed;
	/**
	 * The target's regeneration time before it could be detected as new target. 0 for destructive search.
	 */
	private final double targetCooldown;
	/**
	 * Explicitly define the available actions.
	 */
	private final Set<Integer> availableActions = Set.of(0, 1);

	// [Other variables]
	/**
	 * Policy to be used to either explore a choice, or exploit the current best approach
	 */
	private BehaviorPolicy behaviorPolicy;
	/**
	 * The target's prefix
	 */
	private String targetPrefix;

	// [Reinforcement learning specific variables]
	/**
	 * Penalty per step when no target found
	 */
	private double stepPenalty;
	/**
	 * Reward for finding a new target node
	 */
	private double foundReward;
	private Map<DTNHost, DetectionInfo> objectiveFound;    // O_{f},
	private int prevAction;                                // a_{t},
	private int prevState;                                // s_{t},
	private int currentAction;                            // a_{t+1},
	private int currentState;                            // s_{t+1},
	/**
	 * Step counter n along current trajectory l. This is the RL state.
	 */
	private int currentTrajectorySteps;
	/**
	 * The Q-table, mapping every state's to the Q-value of each action.
	 * {@link StateActionPair} is a pair of state and action, Double is Q-value's datatype of that state-action pair.
	 */
	private final Map<StateActionPair, Double> qTable;

	/**
	 * Stores the previous Coordinate of the agent
	 */
	private Coord currentPosition;
	/**
	 * A radian value representing the direction of movement, used for reward calculation. Range: [0, 2*PI].
	 */
	private double direction;

	/**
	 * An addition to separate learning RNG (used in behavior policy), to create differentiation between
	 * RNG used to initialize locations of the target nodes and the learning behavior. Especially when
	 * we need the same locations of the targets per episode instead of position re-initialization per episode.
	 *
	 */
	public static Random learningRNG;

	// static initialization of all movement models' random number generator
	static {
		DTNSim.registerForReset(QLearningMovement.class.getCanonicalName());
		reset();
	}

	public QLearningMovement(Settings settings) {
		super(settings);
		Settings s = new Settings(QLEARNING_NS);

		this.trajectoryFrequencies = new HashMap<>();
		this.currentCumulativeReward = 0.0;
		this.currentEpisodeReward = 0.0;
		this.currentCumulativeTrueDetections = 0;

		// Bellman specific parameters
		this.alpha = s.getDouble(ALPHA_S, 0.1);
		this.lambda = s.getDouble(LAMBDA_S, 0.9);
		this.initialQValue = s.getDouble(INITIAL_Q_S, 0.0);

		// Reward parameters
		this.stepPenalty = s.getDouble(STEP_PENALTY_S, 0.01);
		this.foundReward = s.getDouble(FOUND_REWARD_S, 10.0);

		// Load the behavior policy & target prefix
//		System.out.println("before loading BP");
		String behaviorClassName = s.getSetting(BEHAVIOR_POLICY_S, "movement.rl.behavior.EpsilonGreedyBehavior");
//		System.out.println("is it loading this");
		this.behaviorPolicy = (BehaviorPolicy) s.createIntializedObject(behaviorClassName);
		this.behaviorPolicy.setRandom(learningRNG);

		this.targetPrefix = s.getSetting(TARGET_PREFIX_S, "T");
		this.agentSpeed = s.getDouble(SPEED_S, 1.0);
		this.targetCooldown = s.getDouble(TARGET_COOLDOWN_S, 0.0);

		// Reinforcement learning specific variables
		this.objectiveFound = new HashMap<>();
		this.qTable = new HashMap<>();
		this.prevAction = -1;
		this.prevState = 0;
		this.currentAction = -1;
		this.currentState = 0;
		this.currentTrajectorySteps = 0;

		// Initialize direction randomly
		this.direction = rng.nextDouble() * 2 * Math.PI;
		this.currentPosition = null; // will be initialized on first getPath()

		// Re/Initializes episodic persistence
		EpisodicPersistenceData epd = EpisodicPersistenceManager.loadIfExists();
		if (epd != null) {
			loadFrom(epd);
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
					// Update the last found time for this target
					double now = SimClock.getTime();
					objectiveFound.compute(otherNode, (node, existsInfo) -> {
						if (existsInfo == null) {
							/* First detection, negative infinity to ensure update */
							DetectionInfo info = DetectionInfo.of(Double.NEGATIVE_INFINITY, 0);
							info.update(now, targetCooldown);
							return info;
						} else {
							/* Redetection */
							existsInfo.update(now, targetCooldown);
							return existsInfo;
						}
					});
				}
			}
		}
	}

	/**
	 * Copy constructor for replicate.
	 */
	public QLearningMovement(QLearningMovement proto) {
		super(proto);
		this.trajectoryFrequencies = new HashMap<>(proto.trajectoryFrequencies);
		this.currentCumulativeReward = proto.currentCumulativeReward;
		this.currentEpisodeReward = proto.currentEpisodeReward;
		this.currentCumulativeTrueDetections = proto.currentCumulativeTrueDetections;
		this.alpha = proto.alpha;
		this.lambda = proto.lambda;
		this.initialQValue = proto.initialQValue;
		this.behaviorPolicy = proto.behaviorPolicy.replicate();
		this.agentSpeed = proto.agentSpeed;
		this.targetCooldown = proto.targetCooldown;
		this.stepPenalty = proto.stepPenalty;
		this.foundReward = proto.foundReward;
		this.targetPrefix = proto.targetPrefix;
		this.objectiveFound = new HashMap<>(proto.objectiveFound);
		this.qTable = new HashMap<>(proto.qTable);
		this.prevAction = proto.prevAction;
		this.prevState = proto.prevState;
		this.currentAction = proto.currentAction;
		this.currentState = proto.currentState;
		this.currentTrajectorySteps = proto.currentTrajectorySteps;
		this.direction = proto.direction;

		if (proto.currentPosition != null) {
			this.currentPosition = new Coord(proto.currentPosition.getX(), proto.currentPosition.getY());
		} else {
			this.currentPosition = null;
		}

	}

	/**
	 * Resets all static fields to default values
	 */
	public static void reset() {
		Settings s = new Settings(QLEARNING_NS);

		/* Initialize seed if not 0, initialize random seed if 0, inherit if not specified. */
		if (s.contains(LEARNING_SEED_S) && s.getInt(LEARNING_SEED_S) != 0) {
			System.out.printf("[%s] Using %s.%s of: %s %n", QLearningMovement.class.getName(), QLEARNING_NS, LEARNING_SEED_S, s.getInt(LEARNING_SEED_S));
			learningRNG = new Random(s.getInt(LEARNING_SEED_S));
		} else if (s.contains(LEARNING_SEED_S) && s.getInt(LEARNING_SEED_S) == 0) {
			System.out.printf("[%s] Using a random learning RNG seed.", QLearningMovement.class.getName());
			learningRNG = new Random();
		} else {
			// Inherit the seed from MovementModel
			System.out.printf("[%s] Using a random learning RNG seed inherited from MovementModel.", QLearningMovement.class.getName());
			Settings movementSettings = new Settings(MOVEMENT_MODEL_NS);
			if (movementSettings.contains(RNG_SEED) && movementSettings.getInt(RNG_SEED) != 0) {
				learningRNG = new Random(movementSettings.getInt(RNG_SEED));
			} else {
				learningRNG = new Random();  // truly random if not set
			}
		}
	}

	protected int selectAction(int state, Set<Integer> availableActions) {
		Map<Integer, Double> qValues = new HashMap<>();
		for (Integer action : availableActions) {
			qValues.put(action, getQ(state, action));
		}
		return behaviorPolicy.selectAction(state, qValues, availableActions);
	}

	/**
	 * Updates the Q-table based on the observed reward and the next state.
	 * Also updates the behavior policy with the new experience.
	 *
	 */
	protected void update(int state, int action, double reward, int nextState, Set<Integer> availableNextActions) {
		double currentQ = getQ(state, action);
		double maxNextQ = getMaxQ(nextState, availableNextActions);

		// Q-Learning update: Q(s,a) = Q(s,a) + α[r + λ max Q(s',a') - Q(s,a)]
		double newQ = currentQ + alpha * (reward + lambda * maxNextQ - currentQ);
		setQ(state, action, newQ);

		// Update the behavior policy
		behaviorPolicy.update(state, action, reward);
	}

	/**
	 * Getting Q-value of state-action pair (Q(s,a)). Defaults to {@link QLearningMovement#initialQValue}.
	 *
	 */
	private double getQ(int state, int action) {
		return qTable.getOrDefault(StateActionPair.of(state, action), initialQValue);
	}

	/**
	 * Setting Q-value of state-action pair (Q(s,a)).
	 *
	 */
	private void setQ(int state, int action, double value) {
		qTable.put(StateActionPair.of(state, action), value);
	}

	private double getMaxQ(int state, Set<Integer> availableActions) {
		double maxQ = Double.NEGATIVE_INFINITY;

		// Getting the maximum Q-Value by comparing each action's q-value for the state
		for (Integer action : availableActions) {
			maxQ = Math.max(maxQ, getQ(state, action));
		}

		// If not initialized, return initial Q-value
		return (maxQ == Double.NEGATIVE_INFINITY) ? initialQValue : maxQ;
	}

	/**
	 * Not only generates the path, it will also do and process all the Markovian Decision Process.
	 * Including:
	 * <ol>
	 *     <li>Updating the Q-table</li>
	 *     <li>Determining next state (n) based on the previous action</li>
	 *     <li>Selection action for the current state</li>
	 *     <li>Doing variable changes regarding the selected action</li>
	 *     <li>Generates path with agent's speed and direction</li>
	 * </ol>
	 *
	 * @author narwa
	 *
	 */
	@Override
	public Path getPath() {
		/* Perform Q-Learning update only if we have previous action */
		if (prevAction != -1) {
			// to make it easier to understand
			int s_t = prevState;
			int a_t = prevAction;
			int s_tp1 = currentState;

			// base movement reward, defaulting to penalty
			double reward = -stepPenalty;

			/* Determining reward using lastRewardedTime based on the recency of targets found */
			double now = SimClock.getTime();
			int availableRewards = 0;
			for (DetectionInfo info : new ArrayList<>(objectiveFound.values())) {
				// check if there's an available reward for the current detection information
				if (info.hasAvailableReward()) {
					availableRewards++;
//					System.out.println("GOT A REWARD");
				}
			}

			if (availableRewards > 0) {
				// if there's an available reward, multiply it with the foundReward
				reward = foundReward * availableRewards;
			}

			// increment the reward tracker variable
			currentEpisodeReward += reward;

//			if (now % 1000 == 1 || reward > 1) System.out.printf("Current Cumulative Reward: %s%n", currentEpisodeReward);
//				s_t, a_t, reward, s_tp1, availableActions);
			update(s_t, a_t, reward, s_tp1, availableActions);
		}

		/* Determining the next state s = (n = n + d), based on the previous action */
		if (currentAction == -1) {
			/* Start counting from 0 */
			currentTrajectorySteps = 0;
		} else if (currentAction == 0) {
			/* Continuing straight, increment the step counter */
			currentTrajectorySteps++;
		} else if (currentAction == 1) {
			/* Agent turned, reset n to 0 */
			recordFinishedTrajectory(currentTrajectorySteps);
			currentTrajectorySteps = 0;
		}

		currentState = currentTrajectorySteps;

		/* Selecting action of this state */
		int stateForAction = currentState; // to make sure consistency of data
		int nextAction = selectAction(stateForAction, availableActions);

		//============================================================================================ TRANSITION PHASE
		/* Transition of the action and state from the previous time ({t} -> {t+1}) */
		prevState = currentState;
		prevAction = nextAction;
		currentAction = nextAction;

		/* Variable changes during action */
		switch (currentAction) {
			case 0:
				// keep direction
				break;
			case 1:
				// change direction randomly and reset step counter for next call
				direction = rng.nextDouble() * 2 * Math.PI;
				break;
			default:
				throw new IllegalStateException("Unexpected action: " + currentAction);
		}

		/* Generate path for this action. */
		Path p = new Path(agentSpeed);
		p.addWaypoint(currentPosition);

		double nextX = currentPosition.getX() + agentSpeed * Math.cos(direction);
		double nextY = currentPosition.getY() + agentSpeed * Math.sin(direction);

		// If the straight step would exit the world bounds, bounce off the wall instead.
		if (nextX >= getMaxX() || nextY >= getMaxY() || nextX <= 0 || nextY <= 0) {
			double[] bounced = bounce(currentPosition.getX(), currentPosition.getY(), nextX, nextY);
			double bounceX = bounced[0];
			double bounceY = bounced[1];
			direction = bounced[2]; // reflected direction
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

		Coord nextWaypoint = new Coord(nextX, nextY);
		p.addWaypoint(nextWaypoint);
		currentPosition = nextWaypoint;

//		if (SimClock.getTime() % 1000 == 1) System.out.println("CURRENT POSITION: " + currentPosition);

		return p;
	}

	/**
	 * Computes a wall-bounce for a movement step that would exit the world bounds.
	 * <p>
	 * Uses parametric ray-vs-axis-aligned-box intersection to find the exact point
	 * where the step first crosses a boundary wall. The remaining distance after the
	 * wall contact is then reflected about that wall's normal, producing a physically
	 * plausible bounce trajectory without any random direction change.
	 *
	 * @param fromX starting X coordinate
	 * @param fromY starting Y coordinate
	 * @param toX   un-clipped target X (may be out of bounds)
	 * @param toY   un-clipped target Y (may be out of bounds)
	 * @return double[5] = { bounceX, bounceY, reflectedDirection, remainDX, remainDY }
	 * <p>
	 * Made by Claude
	 */
	private double[] bounce(double fromX, double fromY, double toX, double toY) {
		double dx = toX - fromX;
		double dy = toY - fromY;

		// Find the smallest t in (0,1] at which the ray (fromX+t*dx, fromY+t*dy) hits a wall.
		double tMin = 1.0;
		boolean hitVertical = false;   // true → hit left/right wall (reflect dx)
		boolean hitHorizontal = false; // true → hit top/bottom wall (reflect dy)

		if (dx > 0 && toX >= getMaxX()) {
			double t = (getMaxX() - fromX) / dx;
			if (t < tMin) {
				tMin = t;
				hitVertical = true;
			}
		}
		if (dx < 0 && toX <= 0) {
			double t = -fromX / dx;
			if (t < tMin) {
				tMin = t;
				hitVertical = true;
			}
		}
		if (dy > 0 && toY >= getMaxY()) {
			double t = (getMaxY() - fromY) / dy;
			if (t < tMin) {
				tMin = t;
				hitHorizontal = true;
				hitVertical = false;
			}
		}
		if (dy < 0 && toY <= 0) {
			double t = -fromY / dy;
			if (t < tMin) {
				tMin = t;
				hitHorizontal = true;
				hitVertical = false;
			}
		}

		// Wall contact point (clamp to avoid floating-point drift outside bounds).
		double bounceX = Math.max(0, Math.min(getMaxX(), fromX + tMin * dx));
		double bounceY = Math.max(0, Math.min(getMaxY(), fromY + tMin * dy));

		// Remaining vector after the bounce point.
		double remDX = (1.0 - tMin) * dx;
		double remDY = (1.0 - tMin) * dy;

		// Reflect the remaining vector about the wall normal.
		if (hitVertical) remDX = -remDX;
		if (hitHorizontal) remDY = -remDY;

		// Derive the new direction angle from the reflected vector.
		double reflectedDir = Math.atan2(
			hitHorizontal ? -dy : dy,
			hitVertical ? -dx : dx);

		return new double[]{bounceX, bounceY, reflectedDir, remDX, remDY};
	}

	/**
	 * Initialize in a random position in the map.
	 */
	@Override
	public Coord getInitialLocation() {
		if (currentPosition != null) {
			return currentPosition;
		} else {
			assert rng != null : "MovementModel not initialized!";
			Coord c = new Coord(rng.nextDouble() * getMaxX(), rng.nextDouble() * getMaxY());
			this.currentPosition = c;
			return c;
		}
	}

	@Override
	public MovementModel replicate() {
		return new QLearningMovement(this);
	}

	// [ REPORTING METHODS ]

	/* Trajectory Frequency Reporter */

	/**
	 * Records a length value to {@link QLearningMovement#trajectoryFrequencies}.
	 */
	private void recordFinishedTrajectory(int length) {
		if (length <= 0) return;
		trajectoryFrequencies.merge(length, 1, Integer::sum);
	}

	@Override
	public Map<Integer, Integer> getTrajectoryFrequencies() {
		return trajectoryFrequencies;
	}

	/* Q-Table Reporter */

	@Override
	public Map<StateActionPair, Double> getQTable() {
		return qTable;
	}

	/* Reward Reporter */

	@Override
	public double retrieveCurrentReward() {
		return currentEpisodeReward;
	}

	/* Searching Agent Reporter */

	/**
	 * This might be useless for our case.
	 *
	 */
	@Override
	public double getInitialDiscovery() {
		return 0;
	}

	@Override
	public Collection<DTNHost> getDiscoveredNodes() {
		return List.of(objectiveFound.keySet().toArray(new DTNHost[0]));
	}

	@Override
	public String getTargetPrefix() {
		return targetPrefix;
	}

	/**
	 * Returns the true amount of detections, derived from adding all occurrences in {@link QLearningMovement#objectiveFound}.
	 *
	 */
	@Override
	public int retrieveTrueDetections() {
		return retrieveCurrentNewTrueDetections();
	}

	public int retrieveCurrentNewTrueDetections() {
		return objectiveFound.entrySet().stream().reduce(
			0,
			(sum, entry) -> sum + entry.getValue().getOccurrences(),
			Integer::sum
		);
	}


	// [ EPISODIC PERSISTENCE METHODS ]

	/**
	 * Minimizes the process of saving an episode.
	 *
	 */
	@Override
	public void saveCurrentEpisode() {
		EpisodicPersistenceData epd = new EpisodicPersistenceData();
		saveTo(epd);
		EpisodicPersistenceManager.save(epd);
	}

	@Override
	public void saveTo(EpisodicPersistenceData epd) {
		System.out.printf("<%s> Saving persistence data...%n", QLearningMovement.class.getName());

		/* Saving RL cores */
		epd.prevAction = this.prevAction;
		epd.prevState = this.prevState;
		epd.currentAction = this.currentAction;
		epd.currentState = this.currentState;
		epd.currentTrajectorySteps = this.currentTrajectorySteps;
		epd.direction = this.direction;
		epd.currentPosition = this.currentPosition;

		/* Saving Q-Table */
		epd.qTable = new HashMap<>();
		for (var entr : qTable.entrySet()) {
			String key = entr.getKey().getStateId() + ":" + entr.getKey().getAction();
			epd.qTable.put(key, entr.getValue());
		}

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
		int newCumulativeTrueDetections = this.currentCumulativeTrueDetections + retrieveCurrentNewTrueDetections();
		epd.previousCumulativeTrueDetections = this.currentCumulativeTrueDetections;
		epd.currentCumulativeTrueDetections = newCumulativeTrueDetections;
		epd.currentTrueDetections = retrieveCurrentNewTrueDetections();
		this.currentCumulativeTrueDetections = newCumulativeTrueDetections;

		// Also save the persistence data for the BP
		behaviorPolicy.saveTo(epd);
	}

	@Override
	public void loadFrom(EpisodicPersistenceData epd) {
		System.out.printf("<%s> Loading persistence data...%n", QLearningMovement.class.getName());

		/* Loading RL cores */
		this.prevAction = epd.prevAction;
		this.prevState = epd.prevState;
		this.currentAction = epd.currentAction;
		this.currentState = epd.currentState;
		this.currentTrajectorySteps = epd.currentTrajectorySteps;
		this.direction = epd.direction;
		this.currentPosition = epd.currentPosition;
		System.out.println("Loading EPD.currentPosition: " + epd.currentPosition);

		/* Loading Q-Table */
		qTable.clear();
		if (epd.qTable != null) {
			for (var entry : epd.qTable.entrySet()) {
				String[] values = entry.getKey().split(":");
				qTable.put(
					StateActionPair.of(Integer.parseInt(values[0]), Integer.parseInt(values[1])),
					entry.getValue()
				);
			}
		}

		/* Loading trajectory recorder */
		trajectoryFrequencies.clear();
		if (epd.trajectoryFrequencies != null) {
			for (var entry : epd.trajectoryFrequencies.entrySet()) {
				this.trajectoryFrequencies.put(Integer.valueOf(entry.getKey()), entry.getValue());
			}
		}

		/* Loading reward recorder */
		System.out.println("Loading EPD.currentCumulativeReward: " + epd.currentCumulativeReward);
		this.currentCumulativeReward = epd.currentCumulativeReward;
		this.currentEpisodeReward = 0.0;

		/* Loading Total occurrences recorder */
		System.out.println("Reading EPD.currentCumulativeTrueDetections: " + epd.currentCumulativeTrueDetections);
		this.currentCumulativeTrueDetections = epd.currentCumulativeTrueDetections;

		// Now, also load persistence for the BP
		behaviorPolicy.loadFrom(epd);
	}
}
