package mcrltest.utils;

import mcrltest.policy.BehaviorPolicy;
import mcrltest.policy.PolicyPersistence;

import java.io.*;
import java.util.HashMap;
import java.util.Map;

/**
 * Serializer universal (policy-aware).
 * Tidak tahu detail policy — hanya delegasi ke policy.
 */
public class QTableSerializer {

    /* =========================
       LOAD RESULT
    ========================= */

    public static class LoadResult {
        public final double totalReward;
        public final double episodeReward;
        public final int episode;

        public final String policyType;
        public final Map<String, Object> policyData;

        public LoadResult(double totalReward,
                          double episodeReward,
                          int episode,
                          String policyType,
                          Map<String, Object> policyData) {

            this.totalReward   = totalReward;
            this.episodeReward = episodeReward;
            this.episode       = episode;
            this.policyType    = policyType;
            this.policyData    = policyData;
        }
    }

    /* =========================
       SAVE JSON
    ========================= */

    public static void saveToJSON(String filename,
                                  QTable qTable,
                                  BehaviorPolicy policy,
                                  double totalReward,
                                  double episodeReward,
                                  int episode) throws IOException {

        new File(filename).getParentFile().mkdirs();

        try (PrintWriter pw = new PrintWriter(new FileWriter(filename))) {

            int nrofAction = qTable.getNrofAction();

            pw.println("{");

            /* ===== POLICY ===== */
            pw.println("\"policy\": {");

            if (policy instanceof PolicyPersistence) {

                PolicyPersistence p = (PolicyPersistence) policy;

                pw.println("\"type\": \"" + p.getPolicyType() + "\",");

                Map<String, Object> data = p.exportState();

                int count = 0;
                for (Map.Entry<String, Object> entry : data.entrySet()) {

                    pw.print("\"" + entry.getKey() + "\": ");

                    Object val = entry.getValue();

                    if (val instanceof Number) {
                        pw.print(val);
                    } else {
                        pw.print("\"" + val + "\"");
                    }

                    count++;
                    if (count < data.size()) pw.println(",");
                }
                pw.println();
            }

            pw.println("},");

            /* ===== TRAINING ===== */
            pw.println("\"training\": {");
            pw.println("\"totalReward\": " + totalReward + ",");
            pw.println("\"episodeReward\": " + episodeReward + ",");
            pw.println("\"episode\": " + episode);
            pw.println("},");

            /* ===== QTABLE ===== */
            pw.println("\"states\": [");

            boolean first = true;

            for (int state : qTable.getStates()) {

                if (!first) pw.println(",");
                first = false;

                pw.println("{");
                pw.println("\"state\": " + state + ",");

                pw.print("\"qValues\": [");
                for (int a = 0; a < nrofAction; a++) {
                    pw.print(qTable.getQValue(state, a));
                    if (a < nrofAction - 1) pw.print(",");
                }
                pw.println("],");

                if (qTable.isUseVisitCount()) {
                    pw.print("\"visitCounts\": [");
                    for (int a = 0; a < nrofAction; a++) {
                        pw.print(qTable.getVisitCount(state, a));
                        if (a < nrofAction - 1) pw.print(",");
                    }
                    pw.println("]");
                }

                pw.print("}");
            }

            pw.println();
            pw.println("]");
            pw.println("}");

            System.out.println("✅ Saved JSON: " + filename);
        }
    }

    /* =========================
       LOAD JSON
    ========================= */

    public static LoadResult loadFromJSON(String filename, QTable qTable) throws IOException {

        File file = new File(filename);
        if (!file.exists()) return null;

        BufferedReader br = new BufferedReader(new FileReader(file));

        String line;

        double totalReward = 0;
        double episodeReward = 0;
        int episode = 0;

        int state = -1;

        String policyType = "";
        Map<String, Object> policyData = new HashMap<>();

        int nrofAction = qTable.getNrofAction();

        while ((line = br.readLine()) != null) {

            line = line.trim();

            /* ===== POLICY ===== */
            if (line.startsWith("\"policy\"")) {

                while ((line = br.readLine()) != null) {

                    line = line.trim();

                    if (line.startsWith("\"type\"")) {
                        policyType = line.split(":")[1]
                                .replace("\"","")
                                .replace(",","")
                                .trim();
                    }

                    else if (line.contains(":")) {

                        String key = line.substring(1, line.indexOf("\":"));
                        String val = line.split(":")[1].replace(",","").trim();

                        try {
                            policyData.put(key, Double.parseDouble(val));
                        } catch (Exception e) {
                            policyData.put(key, val.replace("\"",""));
                        }
                    }

                    if (line.startsWith("}")) break;
                }
            }

            /* ===== TRAINING ===== */
            if (line.startsWith("\"totalReward\""))
                totalReward = Double.parseDouble(line.split(":")[1].replace(",","").trim());

            if (line.startsWith("\"episodeReward\""))
                episodeReward = Double.parseDouble(line.split(":")[1].replace(",","").trim());

            if (line.startsWith("\"episode\""))
                episode = Integer.parseInt(line.split(":")[1].replace(",","").trim());

            /* ===== QTABLE ===== */
            if (line.startsWith("\"state\"")) {
                state = Integer.parseInt(line.split(":")[1].replace(",","").trim());
            }

            if (line.startsWith("\"qValues\"")) {
                String values = line.substring(line.indexOf("[") + 1, line.indexOf("]"));
                String[] qVals = values.split(",");

                for (int i = 0; i < qVals.length; i++) {
                    qTable.setQValue(state, i, Double.parseDouble(qVals[i].trim()));
                }
            }

            if (line.startsWith("\"visitCounts\"")) {
                String values = line.substring(line.indexOf("[") + 1, line.indexOf("]"));
                String[] counts = values.split(",");

                for (int i = 0; i < counts.length; i++) {
                    qTable.setVisitCount(state, i, Integer.parseInt(counts[i].trim()));
                }
            }
        }

        br.close();

        System.out.println("✅ Loaded JSON: " + filename);

        return new LoadResult(totalReward, episodeReward, episode, policyType, policyData);
    }

    /* =========================
       SAVE CSV
    ========================= */

    public static void saveToCSV(String filename,
                                 QTable qTable,
                                 BehaviorPolicy policy,
                                 double totalReward,
                                 double episodeReward,
                                 int episode) throws IOException {

        new File(filename).getParentFile().mkdirs();

        try (PrintWriter pw = new PrintWriter(new FileWriter(filename))) {

            int nrofAction = qTable.getNrofAction();

            /* ===== POLICY ===== */
            pw.println("#POLICY");

            if (policy instanceof PolicyPersistence) {

                PolicyPersistence p = (PolicyPersistence) policy;

                pw.println("type=" + p.getPolicyType());

                Map<String, Object> data = p.exportState();

                for (Map.Entry<String, Object> entry : data.entrySet()) {
                    pw.println(entry.getKey() + "=" + entry.getValue());
                }
            }

            /* ===== TRAINING ===== */
            pw.println("#TRAINING");
            pw.println(totalReward + "," + episodeReward + "," + episode);

            /* ===== QTABLE ===== */
            pw.println("#QTABLE");

            for (int state : qTable.getStates()) {

                StringBuilder sb = new StringBuilder();
                sb.append(state);

                for (int a = 0; a < nrofAction; a++) {
                    sb.append(",").append(qTable.getQValue(state, a));
                }

                if (qTable.isUseVisitCount()) {
                    for (int a = 0; a < nrofAction; a++) {
                        sb.append(",").append(qTable.getVisitCount(state, a));
                    }
                }

                pw.println(sb);
            }

            System.out.println("✅ Saved CSV: " + filename);
        }
    }

    /* =========================
       LOAD CSV
    ========================= */

    public static LoadResult loadFromCSV(String filename, QTable qTable) throws IOException {

        File file = new File(filename);
        if (!file.exists()) return null;

        BufferedReader br = new BufferedReader(new FileReader(file));

        String line;
        String mode = "";

        double totalReward = 0;
        double episodeReward = 0;
        int episode = 0;

        String policyType = "";
        Map<String, Object> policyData = new HashMap<>();

        int nrofAction = qTable.getNrofAction();

        while ((line = br.readLine()) != null) {

            line = line.trim();
            if (line.isEmpty()) continue;

            if (line.startsWith("#")) {
                mode = line;
                continue;
            }

            if (mode.equals("#POLICY")) {

                if (line.startsWith("type=")) {
                    policyType = line.split("=")[1];
                } else {
                    String[] parts = line.split("=");
                    policyData.put(parts[0], Double.parseDouble(parts[1]));
                }
            }

            else if (mode.equals("#TRAINING")) {
                String[] parts = line.split(",");
                totalReward = Double.parseDouble(parts[0]);
                episodeReward = Double.parseDouble(parts[1]);
                episode = Integer.parseInt(parts[2]);
            }

            else if (mode.equals("#QTABLE")) {

                String[] parts = line.split(",");

                int state = Integer.parseInt(parts[0]);
                int idx = 1;

                for (int a = 0; a < nrofAction; a++) {
                    qTable.setQValue(state, a, Double.parseDouble(parts[idx++]));
                }

                if (qTable.isUseVisitCount()) {
                    for (int a = 0; a < nrofAction; a++) {
                        qTable.setVisitCount(state, a, Integer.parseInt(parts[idx++]));
                    }
                }
            }
        }

        br.close();

        System.out.println("✅ Loaded CSV: " + filename);

        return new LoadResult(totalReward, episodeReward, episode, policyType, policyData);
    }
}