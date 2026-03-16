package movement.rl.persistence;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.serializer.SerializerFeature;
import core.Settings;
import core.SimClock;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

/**
 * This class is used to help manage the simulation persistence sequences.
 * The implementation supports and is used for {@link movement.rl.QLearningMovement}.
 *
 * @author narwa
 * */
public class EpisodicPersistenceManager {
	// [ Configuration - Namespace and keys ]
	public static final String EPISODIC_NS = "EPM";
	public static final String PERSISTENCE_PATH_S = "persistencePath";
	public static final String EPISODE_NUMBER_S = "episodeNumber";

	// [ Persistence Metadata ]
	private static String persistencePath = null;
	private static int episodeNumber = 1;
	private static boolean initialized = false;

	/* Register this to ONE SIM to be initialized. */
	static {
		core.DTNSim.registerForReset(EpisodicPersistenceManager.class.getCanonicalName());
	}

	private EpisodicPersistenceManager() {
	}

	public static synchronized void init() {
		if (initialized) return;

		Settings s = new Settings(EPISODIC_NS);

		/* Try reading the persistence path. */
		if (s.contains(PERSISTENCE_PATH_S)) {
			persistencePath = s.getSetting(PERSISTENCE_PATH_S);
			System.out.println("[EpisodicPersistenceManager] Initialized with path: " + persistencePath);
		} else {
			System.out.println("[Warning] [EpisodicPersistenceManager] Persistence path not set. No data will be saved.");
		}

		/* Episode number, injected from -d command (in multi batch runner) */
        episodeNumber = s.getInt(EPISODE_NUMBER_S, 1);

		initialized = true;
	}

	public static int getEpisodeNumber() {
		init(); // Read the current configuration's episode number
		return episodeNumber;
	}

	public static boolean isEnabled() {
		init();
		return persistencePath != null;
	}

	/**
	 * Deserializing JSON file into {@link EpisodicPersistenceData} object.
     *
     * @throws EpisodicPersistenceException on I/O or JSON parse errors
	 * */
	public static EpisodicPersistenceData loadIfExists() {
		init();
		if (persistencePath == null) return null;

		Path path = Paths.get(persistencePath);
		if (!Files.exists(path)) {
            System.out.println("[EpisodicPersistenceManager] No persistence file found at '" + persistencePath + "', starting fresh (episode 1).");
            return null;
        }

		try {
			String json = Files.readString(path);
			EpisodicPersistenceData data = JSON.parseObject(json, EpisodicPersistenceData.class);
			System.out.println("[EpisodicPersistenceManager] Loaded episode " + episodeNumber + " data. At: " + persistencePath);
			return data;
		} catch (IOException e) {
			throw new EpisodicPersistenceException("Failed to read persistence file: " + persistencePath, e);
		}
	}

	/**
	 * Serializing {@link EpisodicPersistenceData} into a JSON file in {@link EpisodicPersistenceManager#persistencePath}.
     *
     * @throws EpisodicPersistenceException on I/O
	 * */
	public static void save(EpisodicPersistenceData data) {
		init();
		if (persistencePath == null) return;

		/* Fills the bookkeeping data. */
		data.lastPersistedSimTime = SimClock.getTime();
		data.episodeNumber = episodeNumber;

		try {
			Path path = Paths.get(persistencePath);
			// Ensure parent directories exist
			if (path.getParent() != null) {
				Files.createDirectories(path.getParent());
			}
			String json = JSON.toJSONString(data, SerializerFeature.PrettyFormat, SerializerFeature.SortField);
			Files.writeString(path, json, StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING);
			System.out.println("[EpisodicPersistenceManager] Saved episode " + episodeNumber + "data . At " + persistencePath);
		} catch (IOException e) {
			throw new EpisodicPersistenceException(
				"[EpisodicPersistenceException] Failed to write persistence file at: " + persistencePath, e
			);
		}
	}

	/**
	 * This is called by DTNSim.
	 * */
    public static void reset() {
        persistencePath = null;
        episodeNumber = 1;
        initialized = false;
    }
}
