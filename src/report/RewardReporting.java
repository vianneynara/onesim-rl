package report;

/**
 * Helps to report the reward achieved during a learning period.
 * */
public interface RewardReporting {
	/**
	 * Retrieves the total reward achieved during the call.
	 * */
	double retrieveCurrentReward();
}
