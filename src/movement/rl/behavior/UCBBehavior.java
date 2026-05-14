package movement.rl.behavior;

import core.Settings;
import lombok.NonNull;
import movement.MovementModel;
import movement.rl.StateActionPair;
import movement.rl.persistence.EpisodicPersistenceData;

import java.util.*;

/**
 * Upper Confidence Bound (UCB) exploration strategy for reinforcement learning.
 * Uses the UCB formula: Q(s,a) + c * sqrt(ln(N(s)) / N(s,a))
 * where:
 * - Q(s,a) is the action-value estimate
 * - c is the exploration constant
 * - N(s) is the total number of times state s has been visited
 * - N(s,a) is the number of times action a has been selected in state s
 * <p>
 * Unvisited actions (N(s,a) = 0) receive infinite UCB bonus and are prioritized.
 *
 * @author narwa
 */
public class UCBBehavior implements BehaviorPolicy {

    private double explorationConstant;
    private boolean resetEpisodically;
    private final Map<StateActionPair, Integer> stateActionFrequencies;
    private final Map<Integer, Integer> stateFrequencies;
    private Random random;

    public static final String BEHAVIOR_NS = "BehaviorPolicy.UCB";
    public static final String EXPLORATION_CONSTANT_S = "explorationConstant";
    public static final String RESET_EPISODICALLY_S = "resetEpisodically";

    /**
     * Constructor called reflectively by Settings. The {@code _settings} param is unused
     * because this policy reads its own sub-namespace ({@value #BEHAVIOR_NS}).
     */
    public UCBBehavior(Settings _settings) {
        Settings behaviorSettings = new Settings(BEHAVIOR_NS);
        this.explorationConstant = behaviorSettings.getDouble(EXPLORATION_CONSTANT_S, 1.0);
        this.resetEpisodically = behaviorSettings.getBoolean(RESET_EPISODICALLY_S, false);

        this.stateActionFrequencies = new HashMap<>();
        this.stateFrequencies = new HashMap<>();

        // use seed from MovementModel for reproducibility
        this.random = MovementModel.getRandom();
        // failsafe in case MovementModel's random is not properly initialized
        if (this.random == null) {
            System.out.println("Warning: MovementModel random not initialized, using new Random() for UCBBehavior");
            this.random = new Random();
        }
    }

    public UCBBehavior(UCBBehavior proto) {
        this.explorationConstant = proto.explorationConstant;
        this.random = proto.random;
        this.stateActionFrequencies = new HashMap<>(proto.stateActionFrequencies);
        this.stateFrequencies = new HashMap<>(proto.stateFrequencies);
    }

    /**
     * Selects an action using the UCB formula.
     * Unvisited actions (N(s,a) = 0) are always selected first if exists (prioritized on exploring).
     * Otherwise, selects the action with the highest UCB value.
     *
     * @param stateId          Current state identifier
     * @param qValues          Q-values for each action at current state
     * @param availableActions Set of valid actions to choose from
     * @return Selected action
     */
    @Override
    public Integer selectAction(int stateId, Map<Integer, Double> qValues, @NonNull Set<Integer> availableActions) {
        /* Handle empty action set */
        Integer[] actionArray;

        if (availableActions.isEmpty()) {
            System.out.println("[UCBBehavior] No actions available, using default actions of 0 and 1");
            actionArray = new Integer[]{0, 1}; // default actions
        } else {
            actionArray = availableActions.toArray(new Integer[0]);
        }

        /* Get or initialize state frequency */
        int totalStateVisits = stateFrequencies.getOrDefault(stateId, 0);

        /* Check for unvisited actions first (N(s,a) = 0) - these has UCB bonus (is more prioritized) */
        // Though we only have 2 RN.
        List<Integer> unvisitedActions = new ArrayList<>();
        for (Integer action : actionArray) {
            StateActionPair pair = StateActionPair.of(stateId, action);
            if (!stateActionFrequencies.containsKey(pair)) {
                unvisitedActions.add(action);
            }
        }

        /* Select one randomly if there are unvisited actions. */
        if (!unvisitedActions.isEmpty()) {
            return unvisitedActions.get(random.nextInt(unvisitedActions.size()));
        }

        // Proceeding where actions have all been visited, now we do he real counting.
        // Defining the variables

        double lnStateVisits = Math.log(totalStateVisits);
        double maxUcbValue = Double.NEGATIVE_INFINITY;
        List<Integer> bestActions = new ArrayList<>();

        for (Integer action : actionArray) {
            StateActionPair pair = StateActionPair.of(stateId, action);
            double qValue = qValues.getOrDefault(action, 0.0);
            int actionVisits = stateActionFrequencies.getOrDefault(pair, 1); // avoid division by zero

            /* UCB Formula: argmax_a( Q(s,a) + c • sqrt(ln(N(s)/N(s,a) ) */
            double ucbValue = qValue + explorationConstant * Math.sqrt(lnStateVisits / actionVisits);

            if (ucbValue > maxUcbValue) {
                /* Clear all previous similar UCB-value and use the better one */
                bestActions.clear();
                bestActions.add(action);
                maxUcbValue = ucbValue;
            } else if (ucbValue == maxUcbValue) {
                /* Add equally high UCB-value */
                bestActions.add(action);
            }
        }

        // Randomly select from actions with the highest UCB value
        return bestActions.get(random.nextInt(bestActions.size()));
    }

    /**
     * Updates the visit frequency counters after an action is taken.
     * Increments both N(s,a) and N(s).
     *
     * @param stateId     State where the action was taken
     * @param actionIndex Action that was taken
     */
    @Override
    public void update(int stateId, int actionIndex, double reward, double prevQ, double prevMaxNextQ, double updatedQ) {
        StateActionPair pair = StateActionPair.of(stateId, actionIndex);

        /* Increment N(s,a) - state-action frequency by 1 */
        stateActionFrequencies.merge(pair, 1, Integer::sum);

        /* Increment N(s) - state frequency by 1 */
        stateFrequencies.merge(stateId, 1, Integer::sum);
    }

    @Override
    public BehaviorPolicy replicate() {
        return new UCBBehavior(this);
    }

    @Override
    public String getName() {
        return "UCBBehavior(c=" + String.format("%.3f", explorationConstant) + ")";
    }

    @Override
    public void setRandom(Random random) {
        this.random = random;
    }

    @Override
    public void saveTo(EpisodicPersistenceData epd) {
        /* Save exploration constant */
        epd.ucbExplorationConstant = this.explorationConstant;

        /* Save state-action pair frequencies, combined with : */
        epd.ucbStateActionFrequencies = new HashMap<>();
        for (var entry : stateActionFrequencies.entrySet()) {
            String key = entry.getKey().getStateId() + ":" + entry.getKey().getAction();
            epd.ucbStateActionFrequencies.put(key, entry.getValue());
        }

        /* Save state-action frequencies with string keys */
        epd.ucbStateFrequencies = new HashMap<>();
        for (var entry : stateFrequencies.entrySet()) {
            epd.ucbStateFrequencies.put(String.valueOf(entry.getKey()), entry.getValue());
        }

        System.out.println("[UCBBehavior] Saved exploration constant: " + epd.ucbExplorationConstant);
    }

    @Override
    public void loadFrom(EpisodicPersistenceData epd) {
        if (!resetEpisodically) {
            this.explorationConstant = epd.ucbExplorationConstant;

            /* Load state-action frequencies */
            this.stateActionFrequencies.clear();
            if (epd.ucbStateActionFrequencies != null) {
                for (var entry : epd.ucbStateActionFrequencies.entrySet()) {
                    String[] values = entry.getKey().split(":");
                    if (values.length == 2) { // meaning a valid state-action pair from : split
                        StateActionPair pair = StateActionPair.of(Integer.parseInt(values[0]), Integer.parseInt(values[1]));
                        this.stateActionFrequencies.put(pair, entry.getValue());
                    }
                }
            }

            /* Load state frequencies */
            this.stateFrequencies.clear();
            if (epd.ucbStateFrequencies != null) {
                for (var entry : epd.ucbStateFrequencies.entrySet()) {
                    this.stateFrequencies.put(Integer.parseInt(entry.getKey()), entry.getValue());
                }
            }

            System.out.println("[UCBBehavior] Loaded exploration constant: " + this.explorationConstant);
        } else {
            this.stateActionFrequencies.clear();
            this.stateFrequencies.clear();
            System.out.println("[UCBBehavior] Episodic data is not loaded. Reset episodically is TRUE");
        }
    }
}
