package report;

import core.DTNHost;

import java.util.Collection;

public interface SearchingAgentReporting {
	/**
	 * Retrieves the time of the first searchable node discovery.
	 * */
	double getInitialDiscovery();

	/**
	 * Retrieves all the discovered searchable nodes.
	 * */
	Collection<DTNHost> getDiscoveredNodes();

	String getTargetPrefix();

	/**
	 * Retrieves the number of true detections, defined by numbers of detections qualifying a specific requirement.
	 * Example: detecting a target outside of cooldown time.
	 *
	 * @return amount of all true detections.
	 * */
	default int retrieveTrueDetections() {
		return 0;
	}

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
