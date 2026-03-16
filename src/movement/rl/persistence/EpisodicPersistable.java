package movement.rl.persistence;

/**
 * Implemented by classes requiring episodic data persistence.
 *
 * @author narwa
 * */
public interface EpisodicPersistable {

	/**
	 * Saves by passing an empty persistence class.
	 *
	 * @param data
	 * */
	void saveTo(EpisodicPersistenceData data);

	/**
	 * Loads the implementor's components from the passed data.
	 *
	 * @param data
	 * */
	void loadFrom(EpisodicPersistenceData data);
}
