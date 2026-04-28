package movement;

import core.Coord;
import core.Settings;

/**
 * Generated random stationary movement. (Maybe semi-Poisson, Poisson enough?)
 *
 * @author narwa
 */
public class StationaryRandom extends StationaryNodes {

	public StationaryRandom(Settings s) {
		super(s);
	}

	public StationaryRandom(StationaryRandom sr) {
		super(sr);
	}

	@Override
	public StationaryRandom replicate() {
		return new StationaryRandom(this);
	}

	/**
	 * Returns a uniformly random location for this node.
	 * When multiple nodes independently call this method, they collectively form
	 * a homogeneous Poisson point process with intensity λ = nodeCount / area.
	 *
	 * @return uniformly random coordinate within map bounds
	 */
	@Override
	public Coord getInitialLocation() {
		double x = rng.nextDouble() * getMaxX();
		double y = rng.nextDouble() * getMaxY();
		return new Coord(x, y);
	}
}
