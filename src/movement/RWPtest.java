/* 
 * Copyright 2010 Aalto University, ComNet
 * Released under GPLv3. See LICENSE.txt for details. 
 */
package movement;

import core.*;
import mcrltest.QModel.mcrltest;

import java.util.List;

/**
 * Random waypoint movement model. Creates zig-zag paths within the
 * simulation area.
 */
public class RWPtest extends MovementModel implements ConnectionListener, UpdateListener
{
	/** how many waypoints should there be per path */
	private static final int PATH_LENGTH = 1;
	private Coord lastWaypoint;

	public mcrltest test;
	private Coord next;

	public RWPtest(Settings settings) {
		super(settings);
	}

	protected RWPtest(RWPtest rwp) {
		super(rwp);
	}
	
	/**
	 * Returns a possible (random) placement for a host
	 * @return Random position on the map
	 */
	@Override
	public Coord getInitialLocation() {
		assert rng != null : "MovementModel not initialized!";
		Coord c = randomCoord();

		this.lastWaypoint = c;
		return c;
	}

	@Override
	public Path getPath() {
		Path p;
		p = new Path(generateSpeed());
		p.addWaypoint(lastWaypoint.clone());
		Coord c = lastWaypoint;

		for (int i=0; i<PATH_LENGTH; i++) {
			c = randomCoord();
			p.addWaypoint(c);
		}

		this.lastWaypoint = c;
		return p;
	}
	
	@Override
	public RWPtest replicate() {
		return new RWPtest(this);
	}
	
	protected Coord randomCoord() {
		return new Coord(rng.nextDouble() * getMaxX(),
				rng.nextDouble() * getMaxY());
	}

	@Override
	public void hostsConnected(DTNHost host1, DTNHost host2) {
		System.out.println("Host connectedyyy");
		next = test.givenCoord();

	}

	@Override
	public void hostsDisconnected(DTNHost host1, DTNHost host2) {

	}

	@Override
	public void updated(List<DTNHost> hosts) {
		System.out.println("print");
	}
}
