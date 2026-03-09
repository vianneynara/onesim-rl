package mcrltest.qModel;

import core.Settings;

public class QLearningModel extends RLModel {

    public QLearningModel(Settings s) {
        super(s);
    }

    @Override
    public void update(int state, int action, double reward, int nextState) {

        double currentQ = qTable.getQValue(state, action);

        double nextMaxQ = qTable.getMaxValue(nextState);

        double target = reward + gamma * nextMaxQ;

        double newQ = currentQ + alpha * (target - currentQ);

        qTable.setQValue(state, action, newQ);
    }
}