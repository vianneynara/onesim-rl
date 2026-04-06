package report;

import movement.rl.StateActionPair;

import java.util.Map;

/**
 * Helps to report the learned Q-values from the Q-table of a learning period.
 * */
public interface QTableReporting {
	/**
	 * Retrieves the specific Q-table of the implementing class.
	 * @return map of {@link StateActionPair} and its Q-values.
	 * */
	Map<StateActionPair, Double> getQTable();
}
