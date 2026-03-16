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
	 * @param epd
	 * */
	void saveTo(EpisodicPersistenceData epd);

	/**
	 * Loads the implementor's components from the passed data.
	 *
	 * @param epd
	 * */
	void loadFrom(EpisodicPersistenceData epd);
}
