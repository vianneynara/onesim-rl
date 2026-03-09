package mcrltest.utils;

import core.Settings;

import java.util.ArrayList;
import java.util.Random;

public class QValue {
    private final double[] qValues;
    private final int[] visitCounts; // Only used if Monte Carlo

    private final int nrofAction;
    private final boolean useVisitCount;

    public QValue(int nrofAction, boolean useVisitCount) {
        this.nrofAction = nrofAction;
        this.useVisitCount = useVisitCount;

        this.qValues = new double[nrofAction];
        this.visitCounts = useVisitCount ? new int[nrofAction] : null;
    }

    public double getQ(int action) {
        validateAction(action);
        return qValues[action];
    }

    public void setQ(int action, double value) {
        validateAction(action);
        qValues[action] = value;
    }

    public int getCount(int action) {
        validateAction(action);
        return visitCounts[action];
    }

    public void setCount(int action, int value) {
        validateAction(action);
        visitCounts[action] = value;
    }

    public int getBestAction(Random random) {
        double maxValue = Double.NEGATIVE_INFINITY;
        ArrayList<Integer> ties = new ArrayList<>();

        for (int i = 0; i < qValues.length; i++) {
            if (qValues[i] > maxValue) {
                maxValue = qValues[i];
                ties.clear();
                ties.add(i);
            } else if (qValues[i] == maxValue) {
                ties.add(i);
            }
        }

        return ties.get(random.nextInt(ties.size()));
    }

    public double getMaxValue() {
        double max = Double.NEGATIVE_INFINITY;
        for (double q : qValues) {
            max = Math.max(max, q);
        }
        return max;
    }

    private void validateAction(int action) {
        if (action < 0 || action >= qValues.length) {
            throw new IllegalArgumentException("Invalid action index: " + action);
        }
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < qValues.length; i++) {
            sb.append("Action ")
                    .append(i)
                    .append(" = ")
                    .append(qValues[i]);

            if (useVisitCount) {
                sb.append(" (count=")
                        .append(visitCounts[i])
                        .append(")");
            }

            sb.append("\n");
        }
        return sb.toString();
    }
}