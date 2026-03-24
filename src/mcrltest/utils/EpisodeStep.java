package mcrltest.utils;

public class EpisodeStep {

    private final int state;
    private final int action;   // 0 = straight, 1 = turn
    private final double reward;

    public EpisodeStep(int state, int action, double reward) {
        this.state = state;
        this.action = action;
        this.reward = reward;
    }

    public int getState() {
        return state;
    }

    public int getAction() {
        return action;
    }

    public double getReward() {
        return reward;
    }

    public String toCSV() {
        return state + "," + action + "," + reward;
    }

    @Override
    public String toString() {

        String actionName = (action == 0) ? "STRAIGHT" : "TURN";

        return "EpisodeStep[state=" + state +
                ", action=" + actionName +
                ", reward=" + reward + "]";
    }
}
