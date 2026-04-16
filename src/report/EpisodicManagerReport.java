package report;

import core.Settings;
import core.SimScenario;
import movement.rl.persistence.EpisodicPersistable;
import movement.rl.persistence.EpisodicPersistenceManager;

/**
 * This specific reporter does one thing, saves {@link EpisodicPersistable} implementors of a host's movement.
 *
 * @author narwa
 * */
public class EpisodicManagerReport extends Report {

	public EpisodicManagerReport() {
		init();
	}

	@Override
	protected void init() {
		super.init();
	}

	@Override
	public void done() {

		/* This just prints an announcement */
		int currentEpisode = (new Settings(EpisodicPersistenceManager.EPISODIC_NS)).getInt(EpisodicPersistenceManager.EPISODE_NUMBER_S, 1);
		System.out.printf("[EpisodicManagerReport] ### SAVING EPISODE %d PERSISTENCE DATA ###%n", currentEpisode);

		/* Grabbing the movement of the host that implements EpisodicPersistable and executes episode saving. */
		SimScenario.getInstance()
			.getHosts()
			.stream()
			.filter(host -> host.getMovement() instanceof EpisodicPersistable)
			.map(host -> (EpisodicPersistable) host.getMovement())
			.findFirst()
			.ifPresent(EpisodicPersistable::saveCurrentEpisode);

		super.done();
	}
}
