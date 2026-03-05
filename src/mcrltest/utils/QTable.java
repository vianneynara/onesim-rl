package mcrltest.utils;

import core.Settings;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class QTable {
    public static final String NROF_ACTION = "nrofAction";
    public static final String USE_VISITCOUNT = "useVisitCount";
    public static final String QTABLE_NS = "QTable";

    private final int nrofAction;
    private final boolean useVisitCount;

    private Map<Integer, QValue> table;

    public QTable(Settings s) {
        Settings QValueSettings = new Settings(QTABLE_NS);

        this.useVisitCount = QValueSettings.getBoolean(USE_VISITCOUNT, true);
        this.nrofAction = QValueSettings.getInt(NROF_ACTION);

        table = new HashMap<>();
    }

    private void initializeState(int state) {
        table.putIfAbsent(state, new QValue(nrofAction, useVisitCount));
    }

    public double getQValue(int state, int action) {
        initializeState(state);
        return table.get(state).getQ(action);
    }

    public void setQValue(int state, int action, double value) {
        initializeState(state);
        table.get(state).setQ(action, value);
    }

    public double getCount(int state, int action) {
        initializeState(state);
        return table.get(state).getCount(action);
    }

    public void setCount(int state, int action, int value) {
        initializeState(state);
        table.get(state).setCount(action, value);
    }

    public int getBestAction(int state, Random random) {
        initializeState(state);
        return table.get(state).getBestAction(random);
    }

    public double getMaxValue(int state) {
        initializeState(state);
        return table.get(state).getMaxValue();
    }

    public void printTable() {
        for (Map.Entry<Integer, QValue> entry : table.entrySet()) {
            System.out.println("State " + entry.getKey() + " -> " + entry.getValue());
        }
    }
}