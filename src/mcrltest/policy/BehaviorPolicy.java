package mcrltest.policy;

import mcrltest.utils.QTable;

import java.io.Serializable;


/**
 * @author narwa
 */
public interface BehaviorPolicy extends Serializable, Cloneable {

    /**
     * Select action for given state using QTable.
     * Action: 0 = straight, 1 = turn
     *
     * change from
     * @author narwa
     *
     * @author ZeroKampus
     */
    Integer selectAction(int state, QTable qTable);

    /**
     * Update internal policy parameters (if needed).
     */
    void update(int state, int action, double reward);

    /**
     * Copy policy for another agent
     */
    BehaviorPolicy replicate();

    /**
     * Policy name (for logging/debugging)
     */
    String getName();
}

