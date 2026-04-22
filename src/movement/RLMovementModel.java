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

        this.prevState = proto.prevState;
        this.prevAction = proto.prevAction;
        this.currentState = proto.currentState;

        this.stepCounter = proto.stepCounter;
        this.direction = proto.direction;

        this.lastWaypoint = proto.lastWaypoint;

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
       REWARD
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
       STATE UPDATE
    ===================================== */

    private void updateState() {

        if (prevAction == -1) {
            return;
        }

        if (prevAction == 0) {
            stepCounter++;   // go straight → continue
        } else {
            stepCounter = 1; // turn → reset
        }

        currentState = stepCounter;
    }

    /* =====================================
       APPLY ACTION
    ===================================== */

    private void applyAction(int action) {

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

        double nextX = lastWaypoint.getX()
                + agent.getSpeed() * Math.cos(direction);

        double nextY = lastWaypoint.getY()
                + agent.getSpeed() * Math.sin(direction);

        nextX = Math.max(0, Math.min(getMaxX(), nextX));
        nextY = Math.max(0, Math.min(getMaxY(), nextY));

        Coord next = new Coord(nextX, nextY);

        p.addWaypoint(next);
        lastWaypoint = next;

        return p;
    }

    /* =====================================
       MAIN LOOP
    ===================================== */

    @Override
    public Path getPath() {

        if (prevAction != -1) {
            double reward = computeReward();
            learn(reward);
        }

        updateState();

        prevState = currentState;

        prevAction = targetDetectedThisStep
                ? 1
                : selectAction(currentState);

        targetDetectedThisStep = false;

        applyAction(prevAction);

        Map<String, Object> state = new HashMap<>();
        state.put("x", lastWaypoint.getX());
        state.put("y", lastWaypoint.getY());
        state.put("direction", direction);
        state.put("state", currentState);
        state.put("step", stepCounter);
        state.put("prevAction", prevAction);
        state.put("prevState", prevState);

        agent.setAgentState(state);

        return generatePath();
    }

    /* =====================================
       INITIAL POSITION (FIXED)
    ===================================== */

    @Override
    public Coord getInitialLocation() {

        agent.tryLoad();

        Map<String, Object> state = agent.getAgentState();

        if (state != null && state.containsKey("x")) {

            double x = ((Number) state.get("x")).doubleValue();
            double y = ((Number) state.get("y")).doubleValue();

            this.direction = ((Number) state.getOrDefault("direction", 0.0)).doubleValue();
            this.currentState = ((Number) state.getOrDefault("state", 1)).intValue();
            this.stepCounter = ((Number) state.getOrDefault("step", 1)).intValue();
            this.prevAction = ((Number) state.getOrDefault("prevAction", -1)).intValue();
            this.prevState  = ((Number) state.getOrDefault("prevState", currentState)).intValue();

            Coord c = new Coord(x, y);
            lastWaypoint = c;

            System.out.println("📍 Loaded Position → (" + x + ", " + y + ")");
            System.out.println("➡️ Direction: " + direction +
                    ", State: " + currentState +
                    ", prevAction: " + prevAction);

            return c;
        }

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