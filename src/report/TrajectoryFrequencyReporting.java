package report;

import java.util.Map;

/**
 * Helps to report trajectory lengths for analyzing the distribution of step length
 * that Lévy Flight generates and compare it with other movement's generated paths.
 * */
public interface TrajectoryFrequencyReporting {
	/**
	 * Retrieves the frequencies of each recorded trajectory length and its frequencies.
	 * {@link Double} being the length of the trajectory and {@link Integer} being the frequency of that length.
	 * @return map of trajectory length and frequencies.
	 * */
	Map<Integer, Integer> getTrajectoryFrequencies();
}
