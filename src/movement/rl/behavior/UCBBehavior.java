package movement.rl.behavior;

import core.Settings;
import movement.MovementModel;
import movement.rl.StateActionPair;
import movement.rl.persistence.EpisodicPersistenceData;

import java.util.Map;
import java.util.Random;
import java.util.Set;

public class UCBBehavior implements BehaviorPolicy {

	private double explorationFrequency;
	private Map<StateActionPair, Integer> stateActionsFrequencies;
	private Map<Integer, Integer> statesFrequencies;
	private Random random;

	public static final String BEHAVIOR_NS = "BehaviorPolicy.UCB";
	public static final String EXPLORATION_FREQUENCY_S = "explorationFrequency";

	public UCBBehavior(Settings _settings) {
		// use seed from MovementModel for reproducibility
		this.random = MovementModel.getRandom();

		Settings behaviorSettings = new Settings(BEHAVIOR_NS);
		explorationFrequency = behaviorSettings.getInt(EXPLORATION_FREQUENCY_S);
	}

	@Override
	public Integer selectAction(int stateId, Map<Integer, Double> qValues, Set<Integer> availableActions) {
		return 0;
	}

	@Override
	public void update(int stateId, Integer actionIndex, double reward) {

	}

	@Override
	public BehaviorPolicy replicate() {
		return null;
	}

	@Override
	public String getName() {
		return "";
	}

	@Override
	public void saveTo(EpisodicPersistenceData epd) {

	}

	@Override
	public void loadFrom(EpisodicPersistenceData epd) {

	}
}
