package movement;

import core.*;
import mcrltest.agent.RLAgent;
import mcrltest.utils.DetectionInfo;

import java.awt.Color;
import java.util.HashMap;
import java.util.Map;

public class RLMovementModel extends MovementModel {

    private RLAgent agent;

    private int prevState;
    private int prevAction;

    private int currentState;

    /* state = number of straight steps before turning */
    private int stepCounter;

    private Coord lastWaypoint;
    private double direction;

    private Map<DTNHost, DetectionInfo> objectiveFound;

    /* flag to force turn after finding target */
    private boolean targetDetectedThisStep = false;

    private int[] RED = {255, 0, 0};

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

        System.out.println("Masuk Changed Connection RL Movement Model");

        if (!con.isUp()) {
            return;
        }

        DTNHost other = con.getOtherNode(getHost());

        if (other == null) {
            return;
        }

        System.out.println("Other Group ID : " + other.getGroupId() + "||" + other.getName());
        System.out.println("Target Prefix : " + agent.getTargetPrefix());

        if (other.getGroupId().startsWith(agent.getTargetPrefix())) {

            double now = SimClock.getTime();

            objectiveFound.compute(other, (node, info) -> {

                if (info == null) {
                    info = DetectionInfo.of(
                            Double.NEGATIVE_INFINITY,
                            Double.NEGATIVE_INFINITY,
                            agent.getTargetCooldown()
                    );
                } else {
                    System.out.println("||||||||||||||||||||||||||||||||||");
                    System.out.println("Target has been found before");
                    System.out.println("||||||||||||||||||||||||||||||||||\n");
                }

                info.update(now, agent.getTargetCooldown());

                /* change target color */
                other.setColor(RED);
                System.out.println("Change into RED\n");

                /* force turn next step */
                targetDetectedThisStep = true;

                System.out.println("++++++++++++++++++++++++++++++++++++");
                System.out.println("++++++++++++++++++++++++++++++++++++");
                System.out.println(node.getName() + " meet " + other.getName());
                System.out.println("++++++++++++++++++++++++++++++++++++");
                System.out.println("++++++++++++++++++++++++++++++++++++\n");

                return info;
            });
        }
    }

    /* =====================================
       RL ACTION SELECTION
       ===================================== */

    private int selectAction(int state) {
        return agent.selectAction(state);
    }

    /* =====================================
       LEARNING
       ===================================== */

    private void learn(double reward) {
        agent.learn(prevState, prevAction, reward, currentState);
    }

    /* =====================================
       REWARD FUNCTION
       ===================================== */

    private double computeReward() {

        double reward = -agent.getStepPenalty();

        int foundTargets = 0;

        for (DetectionInfo info : objectiveFound.values()) {

            if (info.hasAvailableReward()) {
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
            stepCounter = 0;
            return;
        }

        if (prevAction == 0) {
            stepCounter++;
        }
        else if (prevAction == 1) {
            stepCounter = 0;
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

        /* 1️⃣ learn from previous step */
        if (prevAction != -1) {

            double reward = computeReward();

            learn(reward);
        }

        /* 2️⃣ observe state */
        updateState();

        /* 3️⃣ choose action */
        int action = selectAction(currentState);

        /* force turn if target detected */
        if (targetDetectedThisStep) {
            action = 1;
            targetDetectedThisStep = false;
        }

        /* 4️⃣ store transition */
        prevState = currentState;
        prevAction = action;

        System.out.println("=================================");
        System.out.println("State : " + currentState);
        System.out.println("Action : " + action);
        System.out.println("=================================\n");

        /* 5️⃣ execute action */
        applyAction(action);

        /* 6️⃣ move agent */
        return generatePath();
    }

    /* =====================================
       INITIAL LOCATION
       ===================================== */

    @Override
    public Coord getInitialLocation() {

        Coord c = new Coord(
                rng.nextDouble() * getMaxX(),
                rng.nextDouble() * getMaxY()
        );

        lastWaypoint = c;

        return c;
    }

}