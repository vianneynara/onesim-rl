package mcrltest.qModel;

import mcrltest.utils.QTable;

public class QLearningModel extends RLModel {

    public QLearningModel(QTable qTable, double alpha, double gamma, double initialQ) {
        super(qTable, alpha, gamma, initialQ);
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