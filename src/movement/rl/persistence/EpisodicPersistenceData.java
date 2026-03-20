package movement.rl.persistence;

import java.util.HashMap;
import java.util.Map;

public class EpisodicPersistenceData {
	// [ BehaviorPolicy.EpsilonGreedyBehavior ]
	public double epsilon;

	// [ QLearningMovement core ]
	/**
	 * Stores the value, but uses String keys because fastjson cannot use complex objects as keys.
	 * The key's format will be `stateId:actionId`.
	 * */
	public Map<String, Double> qTable;
	public int prevAction;
	public int prevState;
	public int currentAction;
	public int currentState;
	public int currentTrajectorySteps;
	public double direction;

	// [ TrajectoryFrequencyReporting ]
	public Map<String, Integer> trajectoryFrequencies = new HashMap<>();

	// [ SearchingAgentReporting ]
	public int totalDiscovered;
	public int totalUndiscovered;

	// [ Episodic bookkeeping ]
	public int episodeNumber;
	public double lastPersistedSimTime;
}
