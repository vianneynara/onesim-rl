package movement.rl;

import core.*;
import movement.MovementModel;
import movement.Path;
import movement.rl.behavior.BehaviorPolicy;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

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
public class QLearningMovement extends MovementModel {
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
	public static final String ALPHA_S = "alpha";
	public static final String LAMBDA_S = "lambda";
	public static final String INITIAL_Q_S = "initialQValue";
	public static final String BEHAVIOR_POLICY_S = "behaviorPolicy";
	public static final String TARGET_PREFIX_S = "targetPrefix";
	public static final String STEP_PENALTY_S = "stepPenalty";
	public static final String FOUND_REWARD_S = "foundReward";

	// [Explicitly defined constants for the problem]
	private final int SPEED = 1;
	/**
	 * Explicitly define the available actions.
	 * */
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
	/** Penalty per step when no target found */
	private double stepPenalty;
	/** Reward for finding a new target node */
	private double foundReward;
	private Map<DTNHost, Double> targetFound;	// O_{f},
	private int prevAction; 					// a_{t},
	private long prevState; 					// s_{t},
	private int currentAction; 					// a_{t+1},
	private long currentState; 					// s_{t+1},
	/**
	 * The Q-table, mapping every state's to the Q-value of each action.
	 * {@link StateActionPair} is a pair of state and action, Double is Q-value's datatype of that state-action pair.
	 */
	private Map<StateActionPair, Double> qTable;

	/** Stores the previous Coordinate of the agent */
	private Coord lastWaypoint;
	/**
	 * A radian value representing the direction of movement, used for reward calculation. Range: [0, 2*PI].
	 */
	private double direction;

	public QLearningMovement(Settings settings) {
		super(settings);
		Settings s = new Settings(QLEARNING_NS);

		// Bellman specific parameters
		this.alpha = s.getDouble(ALPHA_S, 0.1);
		this.lambda = s.getDouble(LAMBDA_S, 0.9);
		this.initialQValue = s.getDouble(INITIAL_Q_S, 0.0);

		// Reward parameters
		this.stepPenalty = s.getDouble(STEP_PENALTY_S, 0.01);
		this.foundReward = s.getDouble(FOUND_REWARD_S, 10.0);

		// Load the behavior policy & target prefix
		String behaviorClassName = s.getSetting(BEHAVIOR_POLICY_S, "movement.rl.behavior.EpsilonGreedyBehavior");
		this.behaviorPolicy = (BehaviorPolicy) s.createIntializedObject(behaviorClassName);
		this.targetPrefix = s.getSetting(TARGET_PREFIX_S, "T");

		// Reinforcement learning specific variables
		this.targetFound = new HashMap<>();
		this.qTable = new java.util.HashMap<>();
		this.prevAction = -1;
		this.prevState = 0L;
		this.currentAction = -1;
		this.currentState = 0L;

		// Initialize direction randomly
		this.direction = rng.nextDouble() * 2 * Math.PI;
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
					targetFound.put(otherNode, SimClock.getTime());
				}
			}
		}
	}

	/**
	 * Copy constructor for replicate.
	 */
	public QLearningMovement(QLearningMovement proto) {
		super(proto);
		this.alpha = proto.alpha;
		this.lambda = proto.lambda;
		this.initialQValue = proto.initialQValue;
		this.behaviorPolicy = proto.behaviorPolicy;
		this.targetFound = null;
		this.prevAction = 0;
		this.prevState = 0L;
		this.currentAction = 0;
		this.currentState = 0L;
		this.direction = 0.0;
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
	 * */
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
	 * */
	private double getQ(int state, int action) {
		return qTable.getOrDefault(StateActionPair.of(state, action), initialQValue);
	}

	/**
	 * Setting Q-value of state-action pair (Q(s,a)).
	 * */
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

	@Override
	public Path getPath() {
		if (currentAction != -1) {

			return null;
		} else {
			// Initialize with a random action on first step
			currentAction = rng.nextInt(availableActions.size());

			// Create path
			Path p = new Path(SPEED);
			p.addWaypoint(lastWaypoint);

			double nextX;
			double nextY;

			do {
				nextX = lastWaypoint.getX() + SPEED * Math.cos(direction);
				nextY = lastWaypoint.getY() + SPEED * Math.sin(direction);
			} while (nextX >= getMaxX() || nextY >= getMaxY() || nextX <= 0 || nextY <= 0);
			Coord nextWaypoint = new Coord(nextX, nextY);
			p.addWaypoint(nextWaypoint);

			prevAction = currentAction;

			switch (currentAction) {
				case 0: // No change in direction, go to the same direction
					break;
				case 1: // Change direction
					direction = rng.nextDouble() * 2 * Math.PI;
					break;
				default:
					throw new IllegalStateException("Unexpected action: " + currentAction);
			}

			this.lastWaypoint = nextWaypoint;
			return p;
		}
	}

	/** Initialize in a random position */
	@Override
	public Coord getInitialLocation() {
		return new Coord(rng.nextDouble() * getMaxX(), rng.nextDouble() * getMaxY());
	}

	@Override
	public MovementModel replicate() {
		return new QLearningMovement(this);
	}

	/**
	 * This helper class represents a pair of state and action, used as the key for the Q-table.
	 * It hashes and compares based on both state and action to retrieve Q-Values with more ease.
	 * */
	private static class StateActionPair {
		private final long stateId;
		private final int action;

		/** The author loves this approach. */
		public static StateActionPair of(long stateId, int action) {
			return new StateActionPair(stateId, action);
		}

		public StateActionPair(long stateId, int action) {
			this.stateId = stateId;
			this.action = action;
		}

		/**
		 * A specific implementation o avoid the same pair's key-value values being considered as the same.
		 * For example, if we have two pairs (stateId=1, action=0) and (stateId=1, action=1),
		 * they should be considered different keys in the Q-table.
		 * */
		@Override
		public boolean equals(Object o) {
			if (this == o) return true;
			if (o == null || getClass() != o.getClass()) return false;
			StateActionPair that = (StateActionPair) o;
			return stateId == that.stateId && action == that.action;
		}

		@Override
		public int hashCode() {
			return 31 * Long.hashCode(stateId) + Integer.hashCode(action);
		}
	}
}
