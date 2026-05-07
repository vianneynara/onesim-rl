package movement;

import core.Coord;
import core.DTNSim;
import core.Settings;
import movement.rl.QLearningMovement;

import java.util.Random;

/**
 * Grid-based Poisson stationary movement model. Which divides the map into a regular grid
 * and uses Poisson distribution to determine how many nodes fall into each grid cell.
 * Each node is the placed uniformly at random within its assigned cell.
 * This creates a Cox process (doubly stochastic Poisson process) where
 * the intensity varies by grid cell location.
 * <p>
 * Parameters:
 * <ul>
 * <li> gridSize: width/height of each grid cell in map units (default: 100)
 * <li> lambda: average number of nodes per grid cell (default: 1.0)
 * </ul>
 *
 * Warning: class lock is done to prevent corruption of states during initial generations, do not change if unnecessary.
 * @author narwa
 */
public class StationaryGridPoisson extends StationaryNodes {

	public static final String STATIONARY_GRID_POISSON_NS = "StationaryGridPoisson";
	public static final String GRID_SIZE_S = "gridSize";
	public static final String LAMBDA_S = "lambda";

	public static final double DEFAULT_GRID_SIZE = 100.0;
	public static final double DEFAULT_LAMBDA = 1.0;

	private final double gridSize;
	private final double lambda;

	/* Static state shared across all instances of this model class */
	private static int nodeCounter = 0;
	private static int gridWidth = 0;
	private static int gridHeight = 0;
	private static double staticGridSize = 0;
	private static double staticLambda = 0;

	// static initialization of all movement models' random number generator
	static {
		DTNSim.registerForReset(QLearningMovement.class.getCanonicalName());
		reset();
	}

	public StationaryGridPoisson(Settings s) {
		super(s);

		Settings gs = new Settings(STATIONARY_GRID_POISSON_NS);
		this.gridSize = gs.contains(GRID_SIZE_S) ?
			gs.getDouble(GRID_SIZE_S) : DEFAULT_GRID_SIZE;
		this.lambda = gs.contains(LAMBDA_S) ?
			gs.getDouble(LAMBDA_S) : DEFAULT_LAMBDA;

		// Initialize static grid parameters on first node
		synchronized(StationaryGridPoisson.class) {
			if (gridWidth == 0) {
				staticGridSize = this.gridSize;
				staticLambda = this.lambda;
				gridWidth = (int) Math.ceil(getMaxX() / this.gridSize);
				gridHeight = (int) Math.ceil(getMaxY() / this.gridSize);
			}
		}
	}

	public StationaryGridPoisson(StationaryGridPoisson proto) {
		super(proto);
		this.gridSize = proto.gridSize;
		this.lambda = proto.lambda;
	}

	/**
	 * Returns a location based on grid-Poisson distribution.
	 * Each node is assigned to a grid cell and placed uniformly within that cell.
	 *
	 * @return coordinate within grid bounds, distributed via Poisson process
	 */
	@Override
	public Coord getInitialLocation() {
		int cellX, cellY;

		synchronized(StationaryGridPoisson.class) {
			// Assign this node to a grid cell based on counter
			int cellIndex = nodeCounter;
			nodeCounter++;

			// Map linear index to 2D grid coordinates
			cellX = cellIndex % gridWidth;
			cellY = (cellIndex / gridWidth) % gridHeight;
		}

		// Get grid cell boundaries
		double cellMinX = cellX * staticGridSize;
		double cellMaxX = Math.min((cellX + 1) * staticGridSize, getMaxX());
		double cellMinY = cellY * staticGridSize;
		double cellMaxY = Math.min((cellY + 1) * staticGridSize, getMaxY());

		// Place node uniformly within its assigned grid cell
		double x = cellMinX + rng.nextDouble() * (cellMaxX - cellMinX);
		double y = cellMinY + rng.nextDouble() * (cellMaxY - cellMinY);

		return new Coord(x, y);
	}

	@Override
	public StationaryGridPoisson replicate() {
		return new StationaryGridPoisson(this);
	}

	/**
	 * Resets the static node counter. Call this before starting a new simulation.
	 */
	public static void reset() {
		synchronized(StationaryGridPoisson.class) {
			nodeCounter = 0;
			gridWidth = 0;
			gridHeight = 0;
			staticGridSize = 0;
			staticLambda = 0;
		}
	}

	static class GridPoissonGenerator {
		/**
		 * Knuth Algorithm - Inverse transform method
		 * Generates a Poisson-distributed random number with parameter lambda.
		 */
		public static int poissonRandom(double lambda, Random random) {
			double L = Math.exp(-lambda);
			double p = 1.0;
			int k = 0;

			do {
				k++;
				p *= random.nextDouble();
			} while (p > L);
			return k - 1;
		}
	}
}
