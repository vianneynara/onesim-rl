package report;

import core.SimScenario;

import java.util.List;
import java.util.Map;

public class TrajectoryFrequencyReporter extends Report {

	public TrajectoryFrequencyReporter() {
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
		final List<TrajectoryLengthReporting> trajectoryMovements = SimScenario.getInstance()
			.getHosts()
			.stream()
			.filter(host -> host.getMovement() instanceof TrajectoryLengthReporting)
			.map(host -> (TrajectoryLengthReporting) host.getMovement())
			.toList();
		/* Helper representative node */
		TrajectoryLengthReporting representative = trajectoryMovements.getFirst();

		assert representative != null;

		Map<Integer, Integer> trajectoryFrequencies = representative.getTrajectoryFrequencies();

		write("length,frequency");
		for (var entry : trajectoryFrequencies.entrySet()) {
			int trajLength = entry.getKey();
			int trajFreq = entry.getValue();
			System.out.println(trajLength + ":" + trajFreq);
			write(entry.getKey() + "," + entry.getValue());
		}

		super.done();
	}
}
