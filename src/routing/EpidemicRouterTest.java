/* 
 * Copyright 2010 Aalto University, ComNet
 * Released under GPLv3. See LICENSE.txt for details. 
 */
package routing;

import core.Coord;
import core.DTNHost;
import core.Message;
import core.Settings;

/**
 * Epidemic message router with drop-oldest buffer and only single transferring
 * connections at a time.
 */
public class EpidemicRouterTest extends ActiveRouter {

	private Coord nextLocation;

	/**
	 * Constructor. Creates a new message router based on the settings in
	 * the given Settings object.
	 * @param s The settings object
	 */
	public EpidemicRouterTest(Settings s) {
		super(s);
		//TODO: read&use epidemic router specific settings (if any)
	}

	/**
	 * Copy constructor.
	 * @param r The router prototype where setting values are copied from
	 */
	protected EpidemicRouterTest(EpidemicRouterTest r) {
		super(r);
		//TODO: copy epidemic settings here (if any)
	}
			
	@Override
	public void update() {
		super.update();
		if (isTransferring() || !canStartTransfer()) {
			return; // transferring, don't try other connections yet
		}
		
		// Try first the messages that can be delivered to final recipient
		if (exchangeDeliverableMessages() != null) {
			return; // started a transfer, don't try others (yet)
		}
		
		// then try any/all message to any/all connection
		this.tryAllMessagesToAllConnections();
	}

	@Override
	public Message messageTransferred(String id, DTNHost from) {
		Message m = super.messageTransferred(id, from);

		setNextLocation(0,0);

		return m;
	}

	@Override
	public EpidemicRouterTest replicate() {
		return new EpidemicRouterTest(this);
	}

	public void setNextLocation(double x, double y) {
		nextLocation.setLocation(x, y);
	}

	public Coord getNextLocation(){
		return nextLocation;
	}
}