package movement;

import core.*;
import mcrltest.agent.RLAgent;
import mcrltest.utils.DetectionInfo;

import java.util.HashMap;
import java.util.Map;

public class RLMovementModel extends MovementModel {

    private RLAgent agent;

    private int prevState;
    private int prevAction;
    private int currentState;

    /* 🔥 now starts from 1 */
    private int stepCounter;

    private Coord lastWaypoint;
    private double direction;

    private Map<DTNHost, DetectionInfo> objectiveFound;

    private boolean targetDetectedThisStep = false;

    private final int[] RED = {255, 0, 0};

    public RLMovementModel(Settings settings) {
        super(settings);

        this.agent = new RLAgent(settings);

        /* 🔥 FIXED: start from 1 */
        this.prevState = 1;
        this.prevAction = -1;
        this.currentState = 1;

        this.stepCounter = 1;

        this.direction = rng.nextDouble() * 2 * Math.PI;

        this.objectiveFound = new HashMap<>();
    }

    protected RLMovementModel(RLMovementModel proto) {
        super(proto);

        this.agent = new RLAgent(new Settings(RLAgent.RLAGENT_NS));

        /* 🔥 FIXED: start from 1 */
        this.prevState = 1;
        this.prevAction = -1;
        this.currentState = 1;

        this.stepCounter = 1;

        this.direction = rng.nextDouble() * 2 * Math.PI;

        this.objectiveFound = new HashMap<>();
    }

    @Override
    public MovementModel replicate() {
        return new RLMovementModel(this);
    }

    /* =====================================
       TARGET DETECTION
       ===================================== */

    @Override
    public void changedConnection(Connection con) {

        if (!con.isUp()) return;

        DTNHost other = con.getOtherNode(getHost());

        if (other == null || other == getHost()) return;

        if (other.getGroupId().startsWith(agent.getTargetPrefix())) {

            double now = SimClock.getTime();

            objectiveFound.compute(other, (node, info) -> {

                if (info == null) {
                    info = DetectionInfo.of(
                            Double.NEGATIVE_INFINITY,
                            Double.NEGATIVE_INFINITY,
                            agent.getTargetCooldown(),
                            agent.isDestructiveTarget()
                    );
                }

                /* 🔥 register detection event */
                info.update(now);

                other.setColor(RED);
                targetDetectedThisStep = true;

                return info;
            });
        }
    }

    /* =====================================
       RL LOGIC
       ===================================== */

    private int selectAction(int state) {
        return agent.selectAction(state);
    }

    private void learn(double reward) {
        agent.learn(prevState, prevAction, reward, currentState);
    }

    /* =====================================
       REWARD FUNCTION (FIXED)
       ===================================== */

    private double computeReward() {

        double reward = -agent.getStepPenalty();
        int foundTargets = 0;

        for (DetectionInfo info : objectiveFound.values()) {

            if (info.consumeDetectionReward()) {
                foundTargets++;
            }
        }

        if (foundTargets > 0) {
            reward = agent.getFoundReward() * foundTargets;
        }

        return reward;
    }

    /* =====================================
       STATE UPDATE (🔥 CORE FIX)
       ===================================== */

    private void updateState() {

        /* first step */
        if (prevAction == -1) {
            stepCounter = 1;
            currentState = 1;
            return;
        }

        /* action 0 = straight → increase */
        if (prevAction == 0) {
            stepCounter++;
        }
        /* action 1 = turn → reset */
        else {
            stepCounter = 1;
        }

        currentState = stepCounter;
    }

    /* =====================================
       APPLY ACTION
       ===================================== */

    private void applyAction(int action) {

        /* turn */
        if (action == 1) {
            direction = rng.nextDouble() * 2 * Math.PI;
        }
    }

    /* =====================================
       PATH GENERATION
       ===================================== */

    private Path generatePath() {

        Path p = new Path(agent.getSpeed());

        p.addWaypoint(lastWaypoint);

        double nextX = lastWaypoint.getX() +
                agent.getSpeed() * Math.cos(direction);

        double nextY = lastWaypoint.getY() +
                agent.getSpeed() * Math.sin(direction);

        nextX = Math.max(0, Math.min(getMaxX(), nextX));
        nextY = Math.max(0, Math.min(getMaxY(), nextY));

        Coord next = new Coord(nextX, nextY);

        p.addWaypoint(next);
        lastWaypoint = next;

        return p;
    }

    /* =====================================
       MAIN RL LOOP
       ===================================== */

    @Override
    public Path getPath() {

        /* learn from previous step */
        if (prevAction != -1) {
            double reward = computeReward();
            learn(reward);
        }

        /* update state */
        updateState();

        /* choose action */
        int action = selectAction(currentState);

        /* 🔥 force turn if target detected */
        if (targetDetectedThisStep) {
            action = 1;
            targetDetectedThisStep = false;
        }

        /* store transition */
        prevState = currentState;
        prevAction = action;

        /* execute */
        applyAction(action);

        return generatePath();
    }

    /* =====================================
       INITIAL POSITION
       ===================================== */

    @Override
    public Coord getInitialLocation() {

        agent.tryLoad();

        Coord c = new Coord(
                rng.nextDouble() * getMaxX(),
                rng.nextDouble() * getMaxY()
        );

        lastWaypoint = c;

        return c;
    }

    /* =====================================
       GETTERS
       ===================================== */

    public RLAgent getAgent() {
        return agent;
    }

    public Map<DTNHost, DetectionInfo> getObjectiveFound() {
        return this.objectiveFound;
    }
}