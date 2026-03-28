package mcrltest.utils;

import core.Settings;

import java.io.*;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class QTable {

    public static final String QTABLE_NS = "QTable";
    public static final String NROF_ACTION = "nrofAction";
    public static final String USE_VISITCOUNT = "useVisitCount";

    private final int nrofAction;
    private final boolean useVisitCount;

    private Map<Integer, QValue> table;

    /* ===== Stored metadata ===== */
    private double loadedEpsilon = 0;
    private double loadedTotalReward = 0;
    private int loadedEpisode = 0;

    public QTable(Settings s) {
        Settings qSettings = new Settings(QTABLE_NS);

        this.nrofAction = qSettings.getInt(NROF_ACTION);
        this.useVisitCount = qSettings.getBoolean(USE_VISITCOUNT, true);

        table = new HashMap<>();
    }

    private void initializeState(int state) {
        table.putIfAbsent(state, new QValue(nrofAction, useVisitCount));
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
       SAVE CSV
    ========================= */

    public void saveToCSV(String filename,
                          double epsilon,
                          double totalReward,
                          int episode) {

        try {

            File file = new File(filename);
            file.getParentFile().mkdirs();

            PrintWriter pw = new PrintWriter(new FileWriter(file));

            /* ===== METADATA ===== */
            pw.println("epsilon,totalTrainingReward,episode");
            pw.println(epsilon + "," + totalReward + "," + episode);
            pw.println();

            /* ===== HEADER ===== */
            pw.print("state");

            for (int a = 0; a < nrofAction; a++) {
                pw.print(",q" + a);
                if (useVisitCount) {
                    pw.print(",count" + a);
                }
            }

            pw.println();

            /* ===== DATA ===== */
            for (Map.Entry<Integer, QValue> entry : table.entrySet()) {

                int state = entry.getKey();
                QValue q = entry.getValue();

                pw.print(state);

                for (int a = 0; a < nrofAction; a++) {

                    pw.print("," + q.getQ(a));

                    if (useVisitCount) {
                        pw.print("," + q.getCount(a));
                    }
                }

                pw.println();
            }

            pw.close();

            System.out.println("Saved CSV → " + filename);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /* =========================
       LOAD CSV
    ========================= */

    public void loadFromCSV(String filename) {

        try {

            File file = new File(filename);

            if (!file.exists()) {
                System.out.println("No CSV QTable found.");
                return;
            }

            BufferedReader br = new BufferedReader(new FileReader(file));

            br.readLine(); // header

            String[] meta = br.readLine().split(",");

            loadedEpsilon = Double.parseDouble(meta[0]);
            loadedTotalReward = Double.parseDouble(meta[1]);
            loadedEpisode = Integer.parseInt(meta[2]);

            br.readLine(); // empty
            br.readLine(); // table header

            String line;

            while ((line = br.readLine()) != null) {

                String[] parts = line.split(",");

                int idx = 0;
                int state = Integer.parseInt(parts[idx++]);

                initializeState(state);
                QValue q = table.get(state);

                for (int a = 0; a < nrofAction; a++) {

                    q.setQ(a, Double.parseDouble(parts[idx++]));

                    if (useVisitCount) {
                        q.setCount(a, Integer.parseInt(parts[idx++]));
                    }
                }
            }

            br.close();

            System.out.println("CSV loaded.");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /* =========================
       SAVE JSON
    ========================= */

    public void saveToJSON(String filename,
                           double epsilon,
                           double totalReward,
                           int episode) {

        try {

            File file = new File(filename);
            file.getParentFile().mkdirs();

            PrintWriter pw = new PrintWriter(new FileWriter(file));

            pw.println("{");
            pw.println("\"epsilon\": " + epsilon + ",");
            pw.println("\"totalReward\": " + totalReward + ",");
            pw.println("\"episode\": " + episode + ",");
            pw.println("\"states\": [");

            boolean first = true;

            for (Map.Entry<Integer, QValue> entry : table.entrySet()) {

                if (!first) pw.println(",");
                first = false;

                int state = entry.getKey();
                QValue q = entry.getValue();

                pw.println("{");
                pw.println("\"state\": " + state + ",");

                pw.print("\"qValues\": [");
                for (int a = 0; a < nrofAction; a++) {
                    pw.print(q.getQ(a));
                    if (a < nrofAction - 1) pw.print(",");
                }
                pw.println("],");

                if (useVisitCount) {
                    pw.print("\"visitCounts\": [");
                    for (int a = 0; a < nrofAction; a++) {
                        pw.print(q.getCount(a));
                        if (a < nrofAction - 1) pw.print(",");
                    }
                    pw.println("]");
                }

                pw.print("}");
            }

            pw.println();
            pw.println("]");
            pw.println("}");

            pw.close();

            System.out.println("Saved JSON → " + filename);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /* =========================
       LOAD JSON
    ========================= */

    public void loadFromJSON(String filename) {

        try {

            File file = new File(filename);

            if (!file.exists()) {
                System.out.println("No JSON QTable found.");
                return;
            }

            BufferedReader br = new BufferedReader(new FileReader(file));

            String line;
            int state = -1;
            int actionIndex = 0;

            while ((line = br.readLine()) != null) {

                line = line.trim();

                if (line.startsWith("\"epsilon\"")) {
                    loadedEpsilon = Double.parseDouble(line.split(":")[1].replace(",", "").trim());
                }

                if (line.startsWith("\"totalReward\"")) {
                    loadedTotalReward = Double.parseDouble(line.split(":")[1].replace(",", "").trim());
                }

                if (line.startsWith("\"episode\"")) {
                    loadedEpisode = Integer.parseInt(line.split(":")[1].replace(",", "").trim());
                }

                if (line.startsWith("\"state\"")) {
                    state = Integer.parseInt(line.split(":")[1].replace(",", "").trim());
                    initializeState(state);
                    actionIndex = 0;
                }

                if (line.startsWith("\"qValues\"")) {

                    String values = line.substring(line.indexOf("[") + 1, line.indexOf("]"));
                    String[] qVals = values.split(",");

                    for (String q : qVals) {
                        table.get(state).setQ(actionIndex++, Double.parseDouble(q));
                    }
                }

                if (line.startsWith("\"visitCounts\"")) {

                    String values = line.substring(line.indexOf("[") + 1, line.indexOf("]"));
                    String[] counts = values.split(",");

                    int idx = 0;
                    for (String c : counts) {
                        table.get(state).setCount(idx++, Integer.parseInt(c));
                    }
                }
            }

            br.close();

            System.out.println("JSON loaded.");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public double getLoadedEpsilon() {
        return loadedEpsilon;
    }

    public double getLoadedTotalReward() {
        return loadedTotalReward;
    }

    public int getLoadedEpisode() {
        return loadedEpisode;
    }

    public void printTable() {

        System.out.println("========== Q TABLE ==========");

        for (Map.Entry<Integer, QValue> entry : table.entrySet()) {

            int state = entry.getKey();
            QValue q = entry.getValue();

            System.out.print("State " + state + " → ");

            for (int a = 0; a < nrofAction; a++) {

                System.out.print("A" + a + "=" + q.getQ(a));

                if (useVisitCount) {
                    System.out.print(" (n=" + q.getCount(a) + ")");
                }

                if (a < nrofAction - 1) {
                    System.out.print(" | ");
                }
            }

            System.out.println();
        }

        System.out.println("================================");
    }
}