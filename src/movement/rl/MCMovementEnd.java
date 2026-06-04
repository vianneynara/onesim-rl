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
 * Movement implementing Monte Carlo (MC) On-Policy reinforcement learning.
 * Uses Q-Value to estimate the reward of actions given a state.
 * <p>
 * Unlike TD methods, this implementation collects the FULL episode trajectory
 * first, then computes returns G backwards from the terminal step, and only
 * then updates the Q-table. This is the defining characteristic of Monte Carlo.
 * <p>
 * Problem mapping:
 * <ul>
 *     <li>Action: direction change (a), represented as 0,1 where 0 means no change and 1 means change direction</li>
 *     <li>State: step count (d), represented as n=0,1,2,... where 0 means the agent just recently changed direction</li>
 * </ul>
 * <p>
 * The Q-table is a simple Map<StateActionPair, Double> — no two-column Tuple
 * needed because Q-values are only written at episode end via updateEpisode(),
 * so selectAction() always reads a clean, fully-committed value.
 *
 * @author narwa, ZeroFairy
 */
public class MCMovementEnd extends MovementModel implements TrajectoryFrequencyReporting, QTableReporting, RewardReporting, SearchingAgentReporting, SearchingOccurrencesReporting, EpisodicPersistable {

	// [ REPORTING VARIABLES ]
	private final Map<Integer, Integer> trajectoryFrequencies;
	private double currentCumulativeReward;
	private double currentEpisodeReward;
	private int currentCumulativeTrueDetections;

	// [RL parameters]
	private double alpha;        // retained for potential future use
	private double lambda;       // discount factor γ
	private double initialQValue;

	// [Configuration - Settings Keys]
	public static final String MONTECALRO_NS     = "MCMovementEnd";
	public static final String ALPHA_S           = "learningRate";
	public static final String LAMBDA_S          = "discountFactor";
	public static final String INITIAL_Q_S       = "initialQValue";
	public static final String BEHAVIOR_POLICY_S = "behaviorPolicy";
	public static final String TARGET_PREFIX_S   = "targetPrefix";
	public static final String STEP_PENALTY_S    = "stepPenalty";
	public static final String FOUND_REWARD_S    = "foundReward";
	public static final String SPEED_S           = "agentSpeed";
	public static final String TARGET_COOLDOWN_S = "targetCooldown";
	public static final String LEARNING_SEED_S   = "learningSeed";
	public static final String FIRST_VISIT_S     = "firstVisit";

	public static final String PAUSE_TRANING_S = "pauseTraining";
	public static final String RESET_TRAJECTORY_HISTORY_S = "resetTrajectoryHistory";

	// [Configuration - Fixed parameters]
	private final double agentSpeed;
	private final double targetCooldown;
	private final Set<Integer> availableActions = Set.of(0, 1);

	// [Other variables]
	private BehaviorPolicy behaviorPolicy;
	private String targetPrefix;

	// [RL specific variables]
	private double stepPenalty;
	private double foundReward;

	private Map<DTNHost, DetectionInfo> objectiveFound;
	private int prevAction;
	private int prevState;
	private int currentAction;
	private int currentState;
	private int currentTrajectorySteps;

	/**
	 * The Q-table. Simple single-value map — no Tuple needed because Q-values
	 * are only written at episode end via updateEpisode(), so selectAction()
	 * always reads a clean, fully-committed value.
	 */
	private final Map<StateActionPair, Double> qTable;

	private Coord currentPosition;
	private double direction;

	/**
	 * Whether to use first-visit MC or every-visit MC.
	 */
	protected boolean firstVisit;

	/**
	 * Cumulative visit counter N(s,a) across all episodes.
	 * Used as the denominator in the incremental mean: alpha = 1/N(s,a).
	 * Never reset between episodes so the learning rate naturally decays
	 * as the agent accumulates experience.
	 */
	private final Map<StateActionPair, Integer> stateActionCount;

	/**
	 * Episode trajectory buffer — ordered list of (state, action) pairs.
	 * Must be a List to preserve duplicates and temporal ordering needed
	 * for the backward return computation.
	 */
	private final List<int[]> episodeStates;   // each int[2] = {state, action}

	/**
	 * Parallel reward list. episodeRewards.get(t) is the reward received
	 * after taking the action in episodeStates.get(t).
	 */
	private final List<Double> episodeRewards;

	public static Random learningRNG;
	public final boolean pauseTraining;
	public final boolean resetTrajectoryHistory;

	static {
		DTNSim.registerForReset(MCMovementEnd.class.getCanonicalName());
		reset();
	}

	public MCMovementEnd(Settings settings) {
		super(settings);
		Settings s = new Settings(MONTECALRO_NS);

		this.trajectoryFrequencies          = new HashMap<>();
		this.currentCumulativeReward        = 0.0;
		this.currentEpisodeReward           = 0.0;
		this.currentCumulativeTrueDetections = 0;

		this.alpha         = s.getDouble(ALPHA_S, 0.1);
		this.lambda        = s.getDouble(LAMBDA_S, 0.9);
		this.initialQValue = s.getDouble(INITIAL_Q_S, 0.0);

		this.stepPenalty = s.getDouble(STEP_PENALTY_S, 0.01);
		this.foundReward = s.getDouble(FOUND_REWARD_S, 10.0);

		String behaviorClassName = s.getSetting(BEHAVIOR_POLICY_S, "movement.rl.behavior.EpsilonGreedyBehavior");
		this.behaviorPolicy = (BehaviorPolicy) s.createIntializedObject(behaviorClassName);
		this.behaviorPolicy.setRandom(learningRNG);

		this.targetPrefix   = s.getSetting(TARGET_PREFIX_S, "T");
		this.agentSpeed     = s.getDouble(SPEED_S, 1.0);
		this.targetCooldown = s.getDouble(TARGET_COOLDOWN_S, 0.0);

		this.objectiveFound         = new HashMap<>();
		this.qTable                 = new HashMap<>();
		this.prevAction             = -1;
		this.prevState              = 0;
		this.currentAction          = -1;
		this.currentState           = 0;
		this.currentTrajectorySteps = 0;

		this.direction       = rng.nextDouble() * 2 * Math.PI;
		this.currentPosition = null;

		this.pauseTraining = s.getBoolean(PAUSE_TRANING_S, false);
		this.resetTrajectoryHistory = s.getBoolean(RESET_TRAJECTORY_HISTORY_S, false);

		this.firstVisit       = s.getBoolean(FIRST_VISIT_S, true);
		this.stateActionCount = new HashMap<>();
		this.episodeStates    = new ArrayList<>();
		this.episodeRewards   = new ArrayList<>();

		EpisodicPersistenceData epd = EpisodicPersistenceManager.loadIfExists();
		if (epd != null) {
			loadFrom(epd);
		}
	}

	/** Copy constructor for replicate(). */
	public MCMovementEnd(MCMovementEnd proto) {
		super(proto);
		this.trajectoryFrequencies          = new HashMap<>(proto.trajectoryFrequencies);
		this.currentCumulativeReward        = proto.currentCumulativeReward;
		this.currentEpisodeReward           = proto.currentEpisodeReward;
		this.currentCumulativeTrueDetections = proto.currentCumulativeTrueDetections;
		this.alpha                          = proto.alpha;
		this.lambda                         = proto.lambda;
		this.initialQValue                  = proto.initialQValue;
		this.behaviorPolicy                 = proto.behaviorPolicy.replicate();
		this.agentSpeed                     = proto.agentSpeed;
		this.targetCooldown                 = proto.targetCooldown;
		this.stepPenalty                    = proto.stepPenalty;
		this.foundReward                    = proto.foundReward;
		this.targetPrefix                   = proto.targetPrefix;
		this.objectiveFound                 = new HashMap<>(proto.objectiveFound);
		this.qTable                         = new HashMap<>(proto.qTable);
		this.prevAction                     = proto.prevAction;
		this.prevState                      = proto.prevState;
		this.currentAction                  = proto.currentAction;
		this.currentState                   = proto.currentState;
		this.currentTrajectorySteps         = proto.currentTrajectorySteps;
		this.direction                      = proto.direction;
		this.firstVisit                     = proto.firstVisit;
		this.pauseTraining					= proto.pauseTraining;
		this.resetTrajectoryHistory			= proto.resetTrajectoryHistory;
		this.stateActionCount               = new HashMap<>(proto.stateActionCount);

		// Deep-copy episode buffers
		this.episodeStates = new ArrayList<>();
		for (int[] sa : proto.episodeStates) {
			this.episodeStates.add(new int[]{sa[0], sa[1]});
		}
		this.episodeRewards = new ArrayList<>(proto.episodeRewards);

		this.currentPosition = (proto.currentPosition != null)
				? new Coord(proto.currentPosition.getX(), proto.currentPosition.getY())
				: null;
	}

	public static void reset() {
		Settings s = new Settings(MONTECALRO_NS);

		if (s.contains(LEARNING_SEED_S) && s.getInt(LEARNING_SEED_S) != 0) {
			System.out.printf("[%s] Using %s.%s of: %s%n",
					MCMovementEnd.class.getCanonicalName(), MONTECALRO_NS, LEARNING_SEED_S, s.getInt(LEARNING_SEED_S));
			learningRNG = new Random(s.getInt(LEARNING_SEED_S));
		} else if (s.contains(LEARNING_SEED_S) && s.getInt(LEARNING_SEED_S) == 0) {
			System.out.printf("[%s] Using a random learning RNG seed.%n", MCMovementEnd.class.getCanonicalName());
			learningRNG = new Random();
		} else {
			System.out.printf("[%s] Inheriting RNG seed from MovementModel.%n", MCMovementEnd.class.getCanonicalName());
			Settings movementSettings = new Settings(MOVEMENT_MODEL_NS);
			if (movementSettings.contains(RNG_SEED) && movementSettings.getInt(RNG_SEED) != 0) {
				learningRNG = new Random(movementSettings.getInt(RNG_SEED));
			} else {
				learningRNG = new Random();
			}
		}
	}

	// =========================================================================
	// CORE RL METHODS
	// =========================================================================

	protected int selectAction(int state, Set<Integer> availableActions) {
		Map<Integer, Double> qValues = new HashMap<>();
		for (Integer action : availableActions) {
			qValues.put(action, getQ(state, action));
		}
		return behaviorPolicy.selectAction(state, qValues, availableActions);
	}

	/**
	 * Collects one step of experience into the episode buffer.
	 * No Q-value computation happens here — deferred to {@link #updateEpisode()}.
	 */
	protected void update(int state, int action, double reward,
						  int nextState, Set<Integer> availableNextActions) {
		episodeStates.add(new int[]{state, action});
		episodeRewards.add(reward);
	}

	/**
	 * Performs the true Monte Carlo Q-value update at the END of an episode.
	 * <p>
	 * Algorithm (Sutton & Barto, Chapter 5):
	 * <ol>
	 *   <li>G ← 0</li>
	 *   <li>Loop t = T-1 down to 0:</li>
	 *   <li>  G ← γ·G + R_{t+1}</li>
	 *   <li>  If first-visit: skip if (S_t, A_t) seen at a later t in this episode</li>
	 *   <li>  N(s,a) ← N(s,a) + 1</li>
	 *   <li>  Q(s,a) ← Q(s,a) + (1/N(s,a)) · (G − Q(s,a))</li>
	 * </ol>
	 */
	private void updateEpisode() {
		double G = 0.0;
		Set<StateActionPair> visitedThisEpisode = new HashSet<>();

		int T = episodeStates.size();
		for (int t = T - 1; t >= 0; t--) {
			int state     = episodeStates.get(t)[0];
			int action    = episodeStates.get(t)[1];
			double reward = episodeRewards.get(t);

			G = lambda * G + reward;

			StateActionPair key = new StateActionPair(state, action);

			if (firstVisit && visitedThisEpisode.contains(key)) {
				continue;
			}
			visitedThisEpisode.add(key);

			stateActionCount.merge(key, 1, Integer::sum);
			int N = stateActionCount.get(key);

			double oldQ = getQ(state, action);
			double newQ = oldQ + (1.0 / N) * (G - oldQ);
			setQ(state, action, newQ);
			behaviorPolicy.update(state, action, reward, oldQ, 0.0, newQ);
		}

		episodeStates.clear();
		episodeRewards.clear();
	}

	// =========================================================================
	// Q-TABLE ACCESSORS — simple single-column Map
	// =========================================================================

	private double getQ(int state, int action) {
		return qTable.getOrDefault(StateActionPair.of(state, action), initialQValue);
	}

	private void setQ(int state, int action, double value) {
		qTable.put(StateActionPair.of(state, action), value);
	}

	private double getMaxQ(int state, Set<Integer> actions) {
		return actions.stream()
				.mapToDouble(a -> getQ(state, a))
				.max().orElse(initialQValue);
	}

	// =========================================================================
	// MOVEMENT
	// =========================================================================

	@Override
	public void changedConnection(Connection con) {
		if (con.isUp()) {
			DTNHost otherNode = con.getOtherNode(getHost());
			if (otherNode != null
					&& !otherNode.getGroupId().equals(getHost().getGroupId())
					&& otherNode.getGroupId().startsWith(targetPrefix)) {

				double now = SimClock.getTime();
				objectiveFound.compute(otherNode, (node, existsInfo) -> {
					if (existsInfo == null) {
						DetectionInfo info = DetectionInfo.of(Double.NEGATIVE_INFINITY, 0);
						info.update(now, targetCooldown);
						return info;
					} else {
						existsInfo.update(now, targetCooldown);
						return existsInfo;
					}
				});
			}
		}
	}

	@Override
	public Path getPath() {
		if (prevAction != -1) {
			int s_t   = prevState;
			int a_t   = prevAction;
			int s_tp1 = currentState;

			double reward = -stepPenalty;

			int availableRewards = 0;
			for (DetectionInfo info : new ArrayList<>(objectiveFound.values())) {
				if (info.hasAvailableReward()) availableRewards++;
			}
			if (availableRewards > 0) {
				reward = foundReward * availableRewards;
			}

			currentEpisodeReward += reward;

			if (!this.pauseTraining) {
				update(s_t, a_t, reward, s_tp1, availableActions);
			}
		}

		if (currentAction == -1) {
			currentTrajectorySteps = 0;
		} else if (currentAction == 0) {
			currentTrajectorySteps++;
		} else if (currentAction == 1) {
			recordFinishedTrajectory(currentTrajectorySteps);
			currentTrajectorySteps = 0;
		}
		currentState = currentTrajectorySteps;

		int nextAction = selectAction(currentState, availableActions);

		prevState     = currentState;
		prevAction    = nextAction;
		currentAction = nextAction;

		switch (currentAction) {
			case 0: break;
			case 1: direction = rng.nextDouble() * 2 * Math.PI; break;
			default: throw new IllegalStateException("Unexpected action: " + currentAction);
		}

		Path p = new Path(agentSpeed);
		p.addWaypoint(currentPosition);

		double nextX = currentPosition.getX() + agentSpeed * Math.cos(direction);
		double nextY = currentPosition.getY() + agentSpeed * Math.sin(direction);

		if (nextX >= getMaxX() || nextY >= getMaxY() || nextX <= 0 || nextY <= 0) {
			double[] bounced = bounce(currentPosition.getX(), currentPosition.getY(), nextX, nextY);
			direction = bounced[2];
			p.addWaypoint(new Coord(bounced[0], bounced[1]));
			nextX = Math.max(0, Math.min(getMaxX(), bounced[0] + bounced[3]));
			nextY = Math.max(0, Math.min(getMaxY(), bounced[1] + bounced[4]));
		}

		Coord nextWaypoint = new Coord(nextX, nextY);
		p.addWaypoint(nextWaypoint);
		currentPosition = nextWaypoint;

		return p;
	}

	private double[] bounce(double fromX, double fromY, double toX, double toY) {
		double dx = toX - fromX;
		double dy = toY - fromY;
		double tMin = 1.0;
		boolean hitVertical = false, hitHorizontal = false;

		if (dx > 0 && toX >= getMaxX()) { double t = (getMaxX() - fromX) / dx; if (t < tMin) { tMin = t; hitVertical = true; } }
		if (dx < 0 && toX <= 0)         { double t = -fromX / dx;               if (t < tMin) { tMin = t; hitVertical = true; } }
		if (dy > 0 && toY >= getMaxY()) { double t = (getMaxY() - fromY) / dy;  if (t < tMin) { tMin = t; hitHorizontal = true; hitVertical = false; } }
		if (dy < 0 && toY <= 0)         { double t = -fromY / dy;               if (t < tMin) { tMin = t; hitHorizontal = true; hitVertical = false; } }

		double bounceX = Math.max(0, Math.min(getMaxX(), fromX + tMin * dx));
		double bounceY = Math.max(0, Math.min(getMaxY(), fromY + tMin * dy));
		double remDX   = (1.0 - tMin) * dx;
		double remDY   = (1.0 - tMin) * dy;
		if (hitVertical)   remDX = -remDX;
		if (hitHorizontal) remDY = -remDY;
		double reflectedDir = Math.atan2(hitHorizontal ? -dy : dy, hitVertical ? -dx : dx);

		return new double[]{bounceX, bounceY, reflectedDir, remDX, remDY};
	}

	@Override
	public Coord getInitialLocation() {
		if (currentPosition != null) return currentPosition;
		assert rng != null : "MovementModel not initialized!";
		Coord c = new Coord(rng.nextDouble() * getMaxX(), rng.nextDouble() * getMaxY());
		this.currentPosition = c;
		return c;
	}

	@Override
	public MovementModel replicate() {
		return new MCMovementEnd(this);
	}

	// =========================================================================
	// REPORTING METHODS
	// =========================================================================

	private void recordFinishedTrajectory(int length) {
		if (length <= 0) return;
		trajectoryFrequencies.merge(length, 1, Integer::sum);
	}

	@Override public Map<Integer, Integer> getTrajectoryFrequencies() { return trajectoryFrequencies; }

	@Override
	public Map<StateActionPair, Double> getQTable() {
		return Collections.unmodifiableMap(qTable);
	}

	@Override public double retrieveCurrentReward()  { return currentEpisodeReward; }
	@Override public double getInitialDiscovery()    { return 0; }

	@Override
	public Collection<DTNHost> getDiscoveredNodes() {
		return List.of(objectiveFound.keySet().toArray(new DTNHost[0]));
	}

	@Override public String getTargetPrefix() { return targetPrefix; }
	@Override public int retrieveTrueDetections()   { return retrieveCurrentNewTrueDetections(); }
	@Override public int retrieveUniqueDetections() { return objectiveFound.size(); }

	public int retrieveCurrentNewTrueDetections() {
		return objectiveFound.entrySet().stream()
				.reduce(0, (sum, e) -> sum + e.getValue().getOccurrences(), Integer::sum);
	}

	// =========================================================================
	// EPISODIC PERSISTENCE
	// =========================================================================

	@Override
	public void saveCurrentEpisode() {
		EpisodicPersistenceData epd = new EpisodicPersistenceData();
		saveTo(epd);
		EpisodicPersistenceManager.save(epd);
	}

	@Override
	public void saveTo(EpisodicPersistenceData epd) {
		System.out.printf("[%s] Saving persistence data...%n", MCMovementEnd.class.getCanonicalName());

		// Run the MC update first, then save the resulting Q-table
		updateEpisode();

		/* Saving RL cores */
		epd.prevAction             = this.prevAction;
		epd.prevState              = this.prevState;
		epd.currentAction          = this.currentAction;
		epd.currentState           = this.currentState;
		epd.currentTrajectorySteps = this.currentTrajectorySteps;
		epd.direction              = this.direction;
		epd.currentPosition        = this.currentPosition;

		/* Saving Q-Table — single Double value per entry */
		epd.qTable = new HashMap<>();
		for (var entry : qTable.entrySet()) {
			String key = entry.getKey().getStateId() + ":" + entry.getKey().getAction();
			epd.qTable.put(key, entry.getValue());
		}

		/* Saving trajectory recorder */
		epd.trajectoryFrequencies = new HashMap<>();
		for (var entry : trajectoryFrequencies.entrySet()) {
			epd.trajectoryFrequencies.put(String.valueOf(entry.getKey()), entry.getValue());
		}

		/* Saving reward recorder */
		double newTotalReward = this.currentCumulativeReward + this.currentEpisodeReward;
		epd.previousCumulativeReward = this.currentCumulativeReward;
		epd.currentCumulativeReward  = newTotalReward;
		epd.currentEpisodeReward     = this.currentEpisodeReward;
		this.currentCumulativeReward = newTotalReward;

		/* Saving detection recorder */
		int newCumulativeDetections = this.currentCumulativeTrueDetections + retrieveCurrentNewTrueDetections();
		epd.previousCumulativeTrueDetections = this.currentCumulativeTrueDetections;
		epd.currentCumulativeTrueDetections  = newCumulativeDetections;
		epd.currentTrueDetections            = retrieveCurrentNewTrueDetections();
		epd.currentUniqueDetections			 = retrieveUniqueDetections();
		this.currentCumulativeTrueDetections = newCumulativeDetections;

		behaviorPolicy.saveTo(epd);
	}

	@Override
	public void loadFrom(EpisodicPersistenceData epd) {
		System.out.printf("[%s] Loading persistence data...%n", MCMovementEnd.class.getCanonicalName());

		/* Loading RL cores */
		this.prevAction             = epd.prevAction;
		this.prevState              = epd.prevState;
		this.currentAction          = epd.currentAction;
		this.currentState           = epd.currentState;
		this.currentTrajectorySteps = epd.currentTrajectorySteps;
		this.direction              = epd.direction;
		this.currentPosition        = epd.currentPosition;

		/* Loading Q-Table — direct single-value load, no Tuple */
		qTable.clear();
		if (epd.qTable != null) {
			for (var entry : epd.qTable.entrySet()) {
				qTable.put(StateActionPair.fromJsonKey(entry.getKey()), entry.getValue());
			}
		}

		/* Loading trajectory recorder */
		trajectoryFrequencies.clear();
		if(!this.resetTrajectoryHistory){
			if (epd.trajectoryFrequencies != null) {
				for (var entry : epd.trajectoryFrequencies.entrySet()) {
					trajectoryFrequencies.put(Integer.valueOf(entry.getKey()), entry.getValue());
				}
			}
		}

		/* Loading reward recorder */
		this.currentCumulativeReward = epd.currentCumulativeReward;
		this.currentEpisodeReward    = 0.0;

		/* Loading detection recorder */
		this.currentCumulativeTrueDetections = epd.currentCumulativeTrueDetections;

		// Clear episode-transient state
		this.episodeStates.clear();
		this.episodeRewards.clear();

		behaviorPolicy.loadFrom(epd);
	}
}