
package movement.rl.behavior;

import movement.rl.Action;

import java.io.Serializable;
import java.util.Map;
import java.util.Set;

/**
 * Interface for behavioral policies that decide which action to take
 * during exploration/exploitation.
 *
 * @author narwa
 */
public interface BehaviorPolicy extends Serializable, Cloneable {
    
    /**
     * Selects an action given current state, Q-values, and available actions. Q-value stored as Q(s,a) in the map, uses Action
	 * as key. It only considers actions in `availableActions`, otherwise only uses the actions in `qValues`.
     * @param stateId Current state identifier
     * @param qValues Q-values for each action at current state `stateId`
     * @param availableActions Set of valid actions (or null for all)
     * @return Selected action
	 *
	 * @author narwa
     */
    Integer selectAction(int stateId, Map<Integer, Double> qValues, Set<Integer> availableActions);
    
    /**
     * To update the internal parameters of behavioral policy (e.g., decay epsilon, update UCB counts,
	 * Thompson Sampling).
     * @param stateId State where the action was taken
     * @param actionIndex Action that was taken
     * @param reward Reward received
     */
    void update(int stateId, Integer actionIndex, double reward);
    
    /**
     * Create a copy of this policy
     */
    BehaviorPolicy replicate();
    
    /**
     * Get policy name for logging/debugging
     */
    String getName();
}