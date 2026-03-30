package report;

public interface SearchingOccurrencesReporting {
	/**
	 * Retrieves the number of true detections, defined by numbers of detections qualifying a specific requirement.
	 * Example: detecting a target outside of cooldown time.
	 *
	 * @return amount of all true detections.
	 * */
	int retrieveTrueDetections();

	/**
	 * Retrieves the number of all detections.
	 *
	 * @return amount of all detections.
	 * */
	default int retrieveAllDetections() {
		return 0;
	}

	/**
	 * Retrieves the number of unique instances.
	 *
	 * @return amount of unique instances.
	 * */
	default int retrieveUniqueDetections() {
		return 0;
	}
}
