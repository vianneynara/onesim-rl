package mcrltest.utils;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class QTable {
    private Map<Integer, QValue> table;

    public QTable() {
        table = new HashMap<>();
    }

    private void initializeState(int state) {
        table.putIfAbsent(state, new QValue());
    }

    public double getQValue(int state, int action) {
        initializeState(state);
        return table.get(state).get(action);
    }

    public void setQValue(int state, int action, double value) {
        initializeState(state);
        table.get(state).set(action, value);
    }

    public int getBestAction(int state, Random random) {
        initializeState(state);
        return table.get(state).getBestAction(random);
    }

    public void printTable() {
        for (Map.Entry<Integer, QValue> entry : table.entrySet()) {
            System.out.println("State " + entry.getKey() + " -> " + entry.getValue());
        }
    }
}