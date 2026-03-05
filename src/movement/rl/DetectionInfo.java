package movement.rl;

import lombok.Getter;

/**
 * This helper class represents detection information of a target, specifically the last found time and
 * the number of occurrences.
 *
 */
public class DetectionInfo {
	/**
	 * The last time a searching agent detected to this specific entry
	 */
	private double lastFoundTime;
	/**
	 * A helper flag to determine whether this entry has an update and reward to consume
	 */
	private boolean rewardAvailable;

	@Getter
	private int occurrences;

	protected static DetectionInfo of(double lastFoundTime, int occurences) {
		return new DetectionInfo(lastFoundTime, occurences);
	}

	public DetectionInfo(double lastFoundTime, int occurences) {
		this.lastFoundTime = lastFoundTime;
		this.occurrences = occurences;
		this.rewardAvailable = false;
	}

	/**
	 * Updates the detection info (last found time and occurrences) only if over the cooldown time.
	 */
	protected boolean update(double foundTime, double cooldown) {
		if (foundTime - lastFoundTime >= cooldown) {
			lastFoundTime = foundTime;
			occurrences++;
			rewardAvailable = true;
			return true;
		}
		return false;
	}

	protected boolean hasAvailableReward() {
		if (rewardAvailable) {
			rewardAvailable = false;
			return true;
		} else {
			return false;
		}
	}
}