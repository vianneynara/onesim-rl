package report;

import core.SimScenario;
import movement.rl.StateActionPair;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.stream.Collectors;

public class QTableReporter extends Report {

	public QTableReporter() {
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
		final List<QTableReporting> qTableModules = SimScenario.getInstance()
			.getHosts()
			.stream()
			.filter(host -> host.getMovement() instanceof QTableReporting)
			.map(host -> (QTableReporting) host.getMovement())
			.toList();
		/* Helper representative node */
		QTableReporting representative = qTableModules.getFirst();

		assert representative != null;

		Map<StateActionPair, Double> qTable = representative.getQTable();

		/* Retrieve all unique states and actions */
		Set<Long> states = new TreeSet<>();
		Set<Integer> actions = new TreeSet<>();
		for (StateActionPair sap : qTable.keySet()) {
			states.add(sap.getStateId());
			actions.add(sap.getAction());
		}

		/* Header of state and the list of actions */
		String header = "state,"
			+ actions.stream()
			.map(String::valueOf)
			.collect(Collectors.joining(","));
		write(header);

		for (Long state : states) {
			StringBuilder sb = new StringBuilder();
			sb.append(state);
			for (Integer action : actions) {
				var qValue = qTable.get(StateActionPair.of(state, action));
				sb.append(",").append(qValue != null ? qValue.toString() : "null");
			}
			write(sb.toString());
		}

		super.done();
	}
}
