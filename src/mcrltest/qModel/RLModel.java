package mcrltest.qModel;

import core.Settings;
import mcrltest.utils.QTable;

public abstract class RLModel {

    public static final String RLMODEL_NS = "RLModel";

    public static final String ALPHA_S = "learningRate";
    public static final String LAMBDA_S = "discountFactor";
    public static final String INITIAL_Q_S = "initialQValue";

    protected final double alpha;
    protected final double gamma;
    protected final double initialQ;

    protected double totalTrainingReward = 0;

    protected final QTable qTable;

    public RLModel(Settings s) {
        Settings rlModelSettings = new Settings(RLMODEL_NS);

        this.alpha = rlModelSettings.getDouble(ALPHA_S, 0.1);
        this.gamma = rlModelSettings.getDouble(LAMBDA_S, 0.9);
        this.initialQ = rlModelSettings.getDouble(INITIAL_Q_S, 0.0);

        this.qTable = new QTable(rlModelSettings);
    }

    /**
     * Learning update rule implemented by subclasses
     */
    public abstract void update(int state, int action, double reward, int nextState);

    /**
     * Helper to get Q(s,a)
     */
    public double getQ(int state, int action) {
        return qTable.getQValue(state, action);
    }

    /**
     * Helper to set Q(s,a)
     */
    public void setQ(int state, int action, double value) {
        qTable.setQValue(state, action, value);
    }

    public QTable getQTable() {
        return qTable;
    }

    public double getTotalTrainingReward() {
        return totalTrainingReward;
    }
}