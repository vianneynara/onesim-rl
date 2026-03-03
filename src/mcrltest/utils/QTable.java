package mcrltest.utils;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class QTable {
    private Map<Integer, QValue> table;
    private Random random;

    public QTable() {
        table = new HashMap<>();
        random = new Random();
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

    public int getBestAction(int state) {
        initializeState(state);
        return table.get(state).getBestAction();
    }

    public void printTable() {
        for (Map.Entry<Integer, QValue> entry : table.entrySet()) {
            System.out.println("State " + entry.getKey() + " -> " + entry.getValue());
        }
    }
}