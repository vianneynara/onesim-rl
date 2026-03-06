package movement;

import core.*;
import mcrltest.agent.RLAgent;

import java.util.*;

public class RLMovementModel extends MovementModel {

    public static final String RL_NS = "RLMovement";

    private RLAgent agent;

    private int prevState;
    private int prevAction;
    private int currentState;
    private int currentAction;

    private int stepCounter;

    private Coord lastWaypoint;
    private double direction;

    private final Set<Integer> availableActions = Set.of(0,1);

    private Map<DTNHost, DetectionInfo> objectiveFound;

    public RLMovementModel(Settings settings) {
        super(settings);

        this.agent = new RLAgent(settings);

        this.prevState = 0;
        this.prevAction = -1;
        this.currentState = 0;
        this.currentAction = -1;

        this.stepCounter = 0;

        this.direction = rng.nextDouble() * 2 * Math.PI;

        this.objectiveFound = new HashMap<>();
    }

    protected RLMovementModel(RLMovementModel proto) {
        super(proto);

        this.agent = proto.agent;

        this.prevState = 0;
        this.prevAction = -1;
        this.currentState = 0;
        this.currentAction = -1;

        this.stepCounter = 0;

        this.direction = proto.direction;

        this.objectiveFound = new HashMap<>();
    }

    @Override
    public MovementModel replicate() {
        return new RLMovementModel(this);
    }

    /* ===============================
       TARGET DETECTION
       =============================== */

    @Override
    public void changedConnection(Connection con) {

        if (!con.isUp()) return;

        DTNHost other = con.getOtherNode(getHost());

        if (other == null) return;

        if (other.getGroupId().startsWith(agent.getTargetPrefix())) {

            double now = SimClock.getTime();

            objectiveFound.compute(other,(node,info)->{

                if(info == null)
                    info = DetectionInfo.of(Double.NEGATIVE_INFINITY,0);

                info.update(now, agent.getTargetCooldown());

                return info;
            });
        }
    }

    /* ===============================
       RL ACTION SELECTION
       =============================== */

    private int selectAction(int state){
        return agent.selectAction(state);
    }

    /* ===============================
       RL UPDATE
       =============================== */

    private void learn(double reward){

        agent.learn(prevState, prevAction, reward, currentState);

    }

    /* ===============================
       REWARD CALCULATION
       =============================== */

    private double computeReward(){

        double reward = -agent.getStepPenalty();

        int foundTargets = 0;

        for(DetectionInfo info : objectiveFound.values()){

            if(info.hasAvailableReward()){
                foundTargets++;
            }

        }

        if(foundTargets > 0){
            reward = agent.getFoundReward() * foundTargets;
        }

        return reward;
    }

    /* ===============================
       MOVEMENT
       =============================== */

    @Override
    public Path getPath() {

        /* -------- RL UPDATE -------- */

        if(prevAction != -1){

            double reward = computeReward();

            learn(reward);

        }

        /* -------- STATE UPDATE -------- */

        if(currentAction == -1){

            stepCounter = 0;

        } else if(currentAction == 0){

            stepCounter++;

        } else if(currentAction == 1){

            stepCounter = 0;

        }

        currentState = stepCounter;

        /* -------- ACTION SELECTION -------- */

        int action = selectAction(currentState);

        prevState = currentState;
        prevAction = action;
        currentAction = action;

        /* -------- APPLY ACTION -------- */

        if(action == 1){

            direction = rng.nextDouble() * 2 * Math.PI;

        }

        /* -------- PATH GENERATION -------- */

        Path p = new Path(agent.getAgentSpeed());

        p.addWaypoint(lastWaypoint);

        double nextX = lastWaypoint.getX() +
                agent.getAgentSpeed() * Math.cos(direction);

        double nextY = lastWaypoint.getY() +
                agent.getAgentSpeed() * Math.sin(direction);

        nextX = Math.max(0, Math.min(getMaxX(), nextX));
        nextY = Math.max(0, Math.min(getMaxY(), nextY));

        Coord next = new Coord(nextX,nextY);

        p.addWaypoint(next);

        lastWaypoint = next;

        return p;
    }

    /* ===============================
       INITIAL POSITION
       =============================== */

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