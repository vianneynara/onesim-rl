package movement.rl;

/**
 * This helper class represents a pair of state and action, used as the key for the Q-table.
 * It hashes and compares based on both state and action to retrieve Q-Values with more ease.
 *
 */
public class StateActionPair {
	private final long stateId;
	private final int action;

	/**
	 * The author loves this approach.
	 */
	protected static StateActionPair of(long stateId, int action) {
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
	 *
	 */
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