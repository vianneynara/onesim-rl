package movement.rl.persistence;

import report.Report;

/**
 * Implemented by classes requiring episodic data persistence.
 *
 * @author narwa
 * */
public interface EpisodicPersistable {

	/**
	 * Saves by passing an empty persistence class.
	 * Used to make sure the implementor separates the logic of saving the persistable dataa.
	 *
	 * @param epd
	 * */
	void saveTo(EpisodicPersistenceData epd);

	/**
	 * Loads the implementor's components from the passed data.
	 * Used to make sure the implementor separates the logic of loading the persistable dataa.
	 *
	 * @param epd
	 * */
	void loadFrom(EpisodicPersistenceData epd);

	// These methods are called from the reporter.
	// Only works if the implementors overrides them with saving/loading inner logic.

	/**
	 * Called by the reporters to load.
	 * I think it would work though, since the reporter are only added and instantiated after the hosts are
	 * created in {@link core.SimScenario} during the scenario's hosts creation (which instantiates the
	 * movements, routers, etc.).
	 * Not currently implemented.
	 * */
	default void loadPreviousEpisode() {
		System.out.println("[EpisodicPersistable] Loading previous episode data not implemented");
	}

	/**
	 * Used by {@link report.EpisodicManagerReport} to save the current episode data during {@link Report#done()}.
	 * */
	default void saveCurrentEpisode() {
		System.out.println("[EpisodicPersistable] Saving current episode data not implemented");
	}
}
