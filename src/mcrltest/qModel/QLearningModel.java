package mcrltest.qModel;

import core.Settings;

public class QLearningModel extends RLModel {

    public QLearningModel(Settings s) {
        super(s);
    }

    /**
     * Q(s,a) ← Q(s,a) + α[r + γ * maxQ(s′,a′) − Q(s,a)]
     */
    @Override
    public void update(int state, int action, double reward, int nextState) {

        double currentQ = qTable.getQValue(state, action);   // Q(s,a)

        double nextMaxQ = qTable.getMaxValue(nextState);     // maxQ(s',a')

        double target = reward + gamma * nextMaxQ;           // r + γ maxQ

        double newQ = currentQ + alpha * (target - currentQ);

        qTable.setQValue(state, action, newQ);

        totalTrainingReward += reward;
    }
}