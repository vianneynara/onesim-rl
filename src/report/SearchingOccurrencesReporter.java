package report;

import core.SimScenario;
import movement.rl.persistence.EpisodicPersistenceData;
import movement.rl.persistence.EpisodicPersistenceManager;

import java.util.List;

public class SearchingOccurrencesReporter extends Report {

	public SearchingOccurrencesReporter() {
		init();
	}

	@Override
	protected void init() {
		super.init();
	}

	@Override
	public void done() {
		/* Header with scenario name */
		write("REPORT_TYPE: " + this.getClass().getSimpleName()
			+ ", SCEN: " + getScenarioName()
			+ ", SIM_TIME: " + format(getSimTime())
		);

		/* Retrieves all implementing nodes' movement */
		final List<SearchingAgentReporting> searchingAgents = SimScenario.getInstance()
			.getHosts()
			.stream()
			.filter(host -> host.getMovement() instanceof SearchingAgentReporting)
			.map(host -> (SearchingAgentReporting) host.getMovement())
			.toList();
		/* Helper representative node */
		SearchingAgentReporting representative = searchingAgents.getFirst();

		assert representative != null : "No searching agents found in the scenario.";

		int currentTrueDetections = representative.retrieveTrueDetections();

		/* Load the EPD from the JSON file using the manager */
		EpisodicPersistenceData epd = EpisodicPersistenceManager.loadIfExists();
		int previousCumulativeTrueDetections = 0;
		int currentCumulativeTrueDetections = 0;
		if (epd != null) {
			previousCumulativeTrueDetections = epd.previousCumulativeTrueDetections;
			currentCumulativeTrueDetections = epd.currentCumulativeTrueDetections;
		} else {
			System.out.println("[SearchingOccurrencesReporter] No previous episode data found, starting fresh.");
		}

		write(String.format("previousCumulativeTrueDetections: %d", previousCumulativeTrueDetections));
		write(String.format("currentCumulativeTrueDetections: %d", currentCumulativeTrueDetections));
		write(String.format("currentTrueDetections: %d", currentTrueDetections));

		super.done();
	}
}
