package mcrltest.utils;

import core.Settings;
import mcrltest.policy.ThompsonSamplingPolicy.TSProperty;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import java.util.Set;

/**
 * Struktur data murni untuk Q-values dan visit counts.
 * Tidak tahu apapun tentang file I/O — itu urusan QTableSerializer.
 */
public class QTable {

    public static final String QTABLE_NS   = "QTable";
    public static final String NROF_ACTION   = "nrofAction";
    public static final String USE_VISITCOUNT = "useVisitCount";

    private final int nrofAction;
    private final boolean useVisitCount;

    private final Map<Integer, QValue> table = new HashMap<>();

    public QTable(Settings s) {
        Settings qSettings = new Settings(QTABLE_NS);
        this.nrofAction   = qSettings.getInt(NROF_ACTION);
        this.useVisitCount = qSettings.getBoolean(USE_VISITCOUNT, true);
    }

    /* =========================
       INIT
    ========================= */

    private void initializeState(int state) {
        table.computeIfAbsent(state, k -> new QValue(nrofAction, useVisitCount));
    }

    /* =========================
       BASIC OPERATIONS
    ========================= */

    public double getQValue(int state, int action) {
        initializeState(state);
        return table.get(state).getQ(action);
    }

    public void setQValue(int state, int action, double value) {
        initializeState(state);
        table.get(state).setQ(action, value);
    }

    public int getVisitCount(int state, int action) {
        initializeState(state);
        return table.get(state).getCount(action);
    }

    public void setVisitCount(int state, int action, int value) {
        initializeState(state);
        table.get(state).setCount(action, value);
    }

    public int getBestAction(int state, Random rng) {
        initializeState(state);
        return table.get(state).getBestAction(rng);
    }

    public double getMaxValue(int state) {
        initializeState(state);
        return table.get(state).getMaxValue();
    }

    /* =========================
       METADATA
    ========================= */

    public int getNrofAction()    { return nrofAction; }
    public boolean isUseVisitCount() { return useVisitCount; }

    /** Untuk QTableSerializer — iterasi semua state yang sudah ada. */
    public Set<Integer> getStates() {
        return table.keySet();
    }

    /* =========================
       DEBUG
    ========================= */

    public void printTable() {

        System.out.println("========== Q TABLE ==========");

        for (Map.Entry<Integer, QValue> entry : table.entrySet()) {

            int state    = entry.getKey();
            QValue q     = entry.getValue();

            System.out.print("State " + state + " → ");

            for (int a = 0; a < nrofAction; a++) {
                System.out.print("A" + a + "=" + q.getQ(a));
                if (useVisitCount) System.out.print(" (n=" + q.getCount(a) + ")");
                if (a < nrofAction - 1) System.out.print(" | ");
            }

            System.out.println();
        }

        System.out.println("================================");
    }
}