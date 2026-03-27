package report;

import core.SimScenario;
import movement.rl.persistence.EpisodicPersistenceData;
import movement.rl.persistence.EpisodicPersistenceManager;

import java.util.List;

public class RewardReporter extends Report {

	public RewardReporter() {
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
		final List<RewardReporting> learningModule = SimScenario.getInstance()
			.getHosts()
			.stream()
			.filter(host -> host.getMovement() instanceof RewardReporting)
			.map(host -> (RewardReporting) host.getMovement())
			.toList();
		/* Helper representative node */
		RewardReporting representative = learningModule.getFirst();

		assert representative != null;

		/* Retrieves the episode's total reward and the cumulative rewards (from previous episodes) */
		double currentEpisodeRewards = representative.retrieveCurrentReward();
		System.out.println("Retrieved reward of " + currentEpisodeRewards);

		EpisodicPersistenceData epd = EpisodicPersistenceManager.loadIfExists();
		double currentCumulativeReward = 0;
		if (epd != null) {
			currentCumulativeReward = epd.currentCumulativeReward;
		} else {
			System.out.println("[RewardReporter] No previous episode data found, starting fresh.");
		}

		write("currentCumulativeReward: " + currentCumulativeReward);
		write("currentTotalReward: " + currentEpisodeRewards);

		super.done();
	}
}
