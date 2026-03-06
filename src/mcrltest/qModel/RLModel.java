package mcrltest.qModel;

import mcrltest.utils.QTable;

public abstract class RLModel {

    protected final double alpha;
    protected final double gamma;
    protected final double initialQ;

    protected final QTable qTable;

    public RLModel(QTable qTable, double alpha, double gamma, double initialQ) {
        this.alpha = alpha;
        this.gamma = gamma;
        this.initialQ = initialQ;
        this.qTable = qTable;
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
}