package movement.rl.persistence;

import core.Coord;

import java.util.HashMap;
import java.util.Map;

public class EpisodicPersistenceData {
	// [ BehaviorPolicy.EpsilonGreedyBehavior ]
	public double epsilon;

	// [ BehaviorPolicy.UCBBehavior ]
	public double ucbExplorationConstant;
	public Map<String, Integer> ucbStateActionFrequencies = new HashMap<>();
	public Map<String, Integer> ucbStateFrequencies = new HashMap<>();

	// [ BehaviorPolicy.ThompsonSamplingBehavior ]
	public Map<String, String> tsProperties = new HashMap<>();

	// [ QLearningMovement core ]
	/**
	 * Stores the value, but uses String keys because fastjson cannot use complex objects as keys.
	 * The key's format will be `stateId:actionId`.
	 *
	 */
	public Map<String, Double> qTable;
	public int prevAction;
	public int prevState;
	public int currentAction;
	public int currentState;
	public int currentTrajectorySteps;
	public double direction;
	public Coord currentPosition;

	// [ TrajectoryFrequencyReporting ]
	public Map<String, Integer> trajectoryFrequencies = new HashMap<>();

	// [ RewardReporting addon ]
	public double previousCumulativeReward;
	public double currentCumulativeReward;
	public double currentEpisodeReward;

	// [ SearchingAgentReporting ]
	public int previousCumulativeTrueDetections;
	public int currentCumulativeTrueDetections;
	public int currentTrueDetections;

	// [ Episodic bookkeeping ]
	public int episodeNumber;
	public double lastPersistedSimTime;
}
