package movement;

import core.Coord;
import core.DTNSim;
import core.Settings;
import movement.rl.QLearningMovement;

/**
 * Generated Immobile Gaussian movement with non-stationary distribution drift.
 *
 * Nodes are immobile (do not call getPath() repeatedly), but their spatial
 * distribution parameters vary over wall-clock time via a normalized drift multiplier.
 * This creates time-dependent distribution shapes while maintaining node immobility.
 *
 * @author narwa
 */
public class ImmobileCustomizableGaussian extends StationaryNodes {

	private Coord location;

	public static final String NSG_NS = "ImmobileCustomizableGaussian";
	public static final String MEAN_X_RATIO_S = "meanXRatio";           // e.g. 0.5
	public static final String MEAN_Y_RATIO_S = "meanYRatio";           // e.g. 0.5
	public static final String STD_X_RATIO_S  = "stdXRatio";            // e.g. 3.0
	public static final String STD_Y_RATIO_S  = "stdYRatio";            // e.g. 3.0
	public static final String DRIFT_SPEED_S = "driftSpeed";            // e.g. 0.1
	public static final String NORMALIZATION_FACTOR_S = "normalizationFactor"; // e.g. 100.0
	public static final String DRIFT_MIN_S = "driftMin";                // e.g. 0.1
	public static final String DRIFT_MAX_S = "driftMax";                // e.g. 3.0

	private static Double driftMultiplier = null;
	private static Long driftStartTime = null;
	private static final Object LOCK = new Object();

	private double meanXRatio;
	private double meanYRatio;
	private double stdXRatio;
	private double stdYRatio;
	private double driftSpeed;
	private double normalizationFactor;
	private double driftMin;
	private double driftMax;

	// static initialization of all movement models' random number generator
	static {
		DTNSim.registerForReset(QLearningMovement.class.getCanonicalName());
		reset();
	}

	public ImmobileCustomizableGaussian(Settings _settings) {
		super(_settings);

		Settings s = new Settings(NSG_NS);
		this.meanXRatio = s.getDouble(MEAN_X_RATIO_S, 0.5);
		this.meanYRatio = s.getDouble(MEAN_Y_RATIO_S, 0.5);
		this.stdXRatio = s.getDouble(STD_X_RATIO_S, 3.0);
		this.stdYRatio = s.getDouble(STD_Y_RATIO_S, 3.0);
		this.driftSpeed = s.getDouble(DRIFT_SPEED_S, 0.1);
		this.normalizationFactor = s.getDouble(NORMALIZATION_FACTOR_S, 100.0);
		this.driftMin = s.getDouble(DRIFT_MIN_S, 0.1);
		this.driftMax = s.getDouble(DRIFT_MAX_S, 3.0);

		initializeDriftMultiplier();
	}

	public ImmobileCustomizableGaussian(ImmobileCustomizableGaussian proto) {
		super(proto);
		this.location = proto.location;

		this.meanXRatio = proto.meanXRatio;
		this.meanYRatio = proto.meanYRatio;
		this.stdXRatio = proto.stdXRatio;
		this.stdYRatio = proto.stdYRatio;
		this.driftSpeed = proto.driftSpeed;
		this.normalizationFactor = proto.normalizationFactor;
		this.driftMin = proto.driftMin;
		this.driftMax = proto.driftMax;

		initializeDriftMultiplier();
	}

	/**
	 * Resets all static fields to default values
	 */
	public static void reset() {
		ImmobileCustomizableGaussian.driftMultiplier = null;
		ImmobileCustomizableGaussian.driftStartTime = null;
	}

	/**
	 * Initializes the static drift multiplier on first instantiation.
	 * Subsequent calls reuse the initialized value without modification.
	 * Thread-safe via synchronized locking.
	 */
	private static void initializeDriftMultiplier() {
		synchronized(LOCK) {
			if (driftMultiplier == null) {
				driftStartTime = System.currentTimeMillis();
				driftMultiplier = 1.0;
			}
		}
	}

	/**
	 * Computes the current drift multiplier based on elapsed wall-clock time.
	 * Applies clamping to keep drift within [driftMin, driftMax] bounds.
	 *
	 * Formula: drift = 1.0 + driftSpeed * (elapsedSeconds / normalizationFactor)
	 * Clamped to: [driftMin, driftMax]
	 *
	 * @return normalized and clamped drift multiplier for current time
	 */
	private double computeCurrentDrift() {
		synchronized(LOCK) {
			if (driftMultiplier == null || driftStartTime == null) {
				return 1.0;
			}

			long elapsedMs = System.currentTimeMillis() - driftStartTime;
			double elapsedSeconds = elapsedMs / 1000.0;

			double drift = 1.0 + driftSpeed * (elapsedSeconds / normalizationFactor);

			// Apply clamping bounds
			drift = Math.max(driftMin, Math.min(driftMax, drift));

			return drift;
		}
	}

	/**
	 * Returns the only location of this movement model.
	 * Distribution shape is modulated by time-dependent drift multiplier.
	 *
	 * @return the only location of this movement model
	 */
	@Override
	public Coord getInitialLocation() {
		double x;
		double y;

		// Get current drift multiplier normalized by elapsed time
		double drift = computeCurrentDrift();

		do {
			// Apply drift to standard deviations - distribution spreads/compresses over time
			x = rng.nextGaussian() * (getMaxX() / stdXRatio) * drift + getMaxX() * meanXRatio;
			y = rng.nextGaussian() * (getMaxY() / stdYRatio) * drift + getMaxY() * meanYRatio;

		} while (x > getMaxX() || y > getMaxY() || x < 0 || y < 0);
		return new Coord(x, y);
	}

	@Override
	public ImmobileCustomizableGaussian replicate() {
		return new ImmobileCustomizableGaussian(this);
	}
}
