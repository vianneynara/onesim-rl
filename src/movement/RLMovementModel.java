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

    private int stepCounter;

    private Coord lastWaypoint;
    private double direction;

    private Map<DTNHost, DetectionInfo> objectiveFound;

    private boolean targetDetectedThisStep = false;

    private final int[] RED = {255, 0, 0};

    public RLMovementModel(Settings settings) {
        super(settings);

        this.agent = new RLAgent(settings);

        this.prevState = 0;
        this.prevAction = -1;
        this.currentState = 0;

        this.stepCounter = 0;
        this.direction = rng.nextDouble() * 2 * Math.PI;

        this.objectiveFound = new HashMap<>();
    }

    protected RLMovementModel(RLMovementModel proto) {
        super(proto);

        this.agent = new RLAgent(new Settings(RLAgent.RLAGENT_NS));

        this.prevState = 0;
        this.prevAction = -1;
        this.currentState = 0;

        this.stepCounter = 0;
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
                            agent.isDestructiveTarget() // 🔥 IMPORTANT
                    );
                }

                /* 🔥 detection event */
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

    /* 🔥 FIXED REWARD */
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

    private void updateState() {

        if (prevAction == -1) {
            stepCounter = 0;
            return;
        }

        if (prevAction == 0) stepCounter++;
        else stepCounter = 0;

        currentState = stepCounter;
    }

    private void applyAction(int action) {
        if (action == 1) {
            direction = rng.nextDouble() * 2 * Math.PI;
        }
    }

    private Path generatePath() {

        Path p = new Path(agent.getSpeed());

        p.addWaypoint(lastWaypoint);

        double nextX = lastWaypoint.getX() + agent.getSpeed() * Math.cos(direction);
        double nextY = lastWaypoint.getY() + agent.getSpeed() * Math.sin(direction);

        nextX = Math.max(0, Math.min(getMaxX(), nextX));
        nextY = Math.max(0, Math.min(getMaxY(), nextY));

        Coord next = new Coord(nextX, nextY);

        p.addWaypoint(next);
        lastWaypoint = next;

        return p;
    }

    @Override
    public Path getPath() {

        if (prevAction != -1) {
            double reward = computeReward();
            learn(reward);
        }

        updateState();

        int action = selectAction(currentState);

        if (targetDetectedThisStep) {
            action = 1;
            targetDetectedThisStep = false;
        }

        prevState = currentState;
        prevAction = action;

        applyAction(action);

        return generatePath();
    }

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

    public RLAgent getAgent() {
        return agent;
    }

    public Map<DTNHost, DetectionInfo> getObjectiveFound() {
        return this.objectiveFound;
    }
}