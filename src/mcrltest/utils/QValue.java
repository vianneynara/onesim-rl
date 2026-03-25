package mcrltest.utils;

import java.util.ArrayList;
import java.util.Random;

public class QValue {
    private final double[] qValues;
    private final int[] visitCounts;

    public QValue(int nrofAction, boolean useVisitCount) {
        this.qValues = new double[nrofAction];

        visitCounts = useVisitCount ? new int[nrofAction] : null;
    }

    public double getQ(int action) {
        return qValues[action];
    }

    public void setQ(int action, double value) {
        qValues[action] = value;
    }

    public int getCount(int action) {
        return visitCounts[action];
    }

    public void setCount(int action, int value) {
        visitCounts[action] = value;
    }

    public int getBestAction(Random rng) {
        double best = Double.NEGATIVE_INFINITY;
        ArrayList<Integer> ties = new ArrayList<>();

        for (int i = 0; i < qValues.length; i++) {
            if (qValues[i] > best) {
                best = qValues[i];
                ties.clear();
                ties.add(i);

            } else if (qValues[i] == best) {
                ties.add(i);
            }
        }

        return ties.get(rng.nextInt(ties.size()));
    }

    public double getMaxValue() {
        double max = Double.NEGATIVE_INFINITY;

        for (double q : qValues) {
            max = Math.max(max, q);
        }

        return max;
    }
}