package mcrltest.utils;

import java.util.Random;

public class QValue {
    private double straight; // action 0
    private double turn;     // action 1

    public QValue() {
        this.straight = 0.0;
        this.turn = 0.0;
    }

    // action: 0 = straight, 1 = turn
    public double get(int action) {
        if (action == 0) {
            return straight;
        } else if (action == 1) {
            return turn;
        } else {
            throw new IllegalArgumentException("Invalid action: must be 0 or 1");
        }
    }

    public void set(int action, double value) {
        if (action == 0) {
            straight = value;
        } else if (action == 1) {
            turn = value;
        } else {
            throw new IllegalArgumentException("Invalid action: must be 0 or 1");
        }
    }

    // What is the current best action?
    public int getBestAction(Random random) {
        return (straight == turn)
                ? (random.nextBoolean() ? 0 : 1)
                : (straight > turn ? 0 : 1);
    }

    public double getMaxValue() {
        return Math.max(straight, turn);
    }

    @Override
    public String toString() {
        return "Straight(0)=" + straight + ", Turn(1)=" + turn;
    }
}
