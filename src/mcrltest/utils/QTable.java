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
    public static final String ENABLE_SNAPSHOT = "enableSnapshot";

    private final int nrofAction;
    private final boolean useVisitCount;
    private final boolean enableSnapshot;

    private Map<Integer, QValue> table;

    public QTable(Settings s) {
        Settings qSettings = new Settings(QTABLE_NS);

        this.nrofAction = qSettings.getInt(NROF_ACTION);
        this.useVisitCount = qSettings.getBoolean(USE_VISITCOUNT, true);
        this.enableSnapshot = qSettings.getBoolean(ENABLE_SNAPSHOT, false);

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

    public void saveToCSV(String baseFilename,
                          double epsilon,
                          double totalReward,
                          int episode) {

        String filename = baseFilename;

        if (enableSnapshot) {
            filename = "data/qtable/qtable_episode_" + episode + ".csv";
        }

        try {
            File dir = new File("data/qtable");
            if (!dir.exists()) dir.mkdirs();

            PrintWriter pw = new PrintWriter(new FileWriter(filename));

            pw.println("epsilon,totalTrainingReward");
            pw.println(epsilon + "," + totalReward);
            pw.println();

            pw.print("state");

            for (int a = 0; a < nrofAction; a++) {

                pw.print(",q" + a);

                if (useVisitCount) {
                    pw.print(",count" + a);
                }
            }

            pw.println();

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
            br.readLine(); // epsilon
            br.readLine(); // empty
            br.readLine(); // table header

            String line;

            while ((line = br.readLine()) != null) {

                String[] parts = line.split(",");

                int index = 0;
                int state = Integer.parseInt(parts[index++]);

                initializeState(state);
                QValue q = table.get(state);

                for (int a = 0; a < nrofAction; a++) {

                    double qv = Double.parseDouble(parts[index++]);
                    q.setQ(a, qv);

                    if (useVisitCount) {

                        int count = Integer.parseInt(parts[index++]);
                        q.setCount(a, count);
                    }
                }
            }

            br.close();

            System.out.println("CSV QTable loaded.");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /* =========================
       SAVE JSON
    ========================= */

    public void saveToJSON(String baseFilename,
                           double epsilon,
                           double totalReward,
                           int episode) {

        String filename = baseFilename;

        if (enableSnapshot) {
            filename = "data/qtable/qtable_episode_" + episode + ".json";
        }

        try {

            File dir = new File("data/qtable");
            if (!dir.exists()) dir.mkdirs();

            PrintWriter pw = new PrintWriter(new FileWriter(filename));

            pw.println("{");
            pw.println("\"epsilon\": " + epsilon + ",");
            pw.println("\"totalReward\": " + totalReward + ",");
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

                if (line.startsWith("\"state\"")) {

                    state = Integer.parseInt(
                            line.split(":")[1].replace(",", "").trim()
                    );

                    initializeState(state);
                    actionIndex = 0;
                }

                if (line.startsWith("\"qValues\"")) {

                    String values = line
                            .substring(line.indexOf("[") + 1, line.indexOf("]"));

                    String[] qVals = values.split(",");

                    for (String q : qVals) {

                        table.get(state)
                                .setQ(actionIndex++, Double.parseDouble(q));
                    }
                }
            }

            br.close();

            System.out.println("JSON QTable loaded.");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}