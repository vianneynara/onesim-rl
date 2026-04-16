package mcrltest.utils;

import mcrltest.policy.BehaviorPolicy;
import mcrltest.policy.PolicyPersistence;

import java.io.*;
import java.util.HashMap;
import java.util.Map;

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

        public final Map<String, Object> agentState;

        public LoadResult(double totalReward,
                          double episodeReward,
                          int episode,
                          String policyType,
                          Map<String, Object> policyData,
                          Map<String, Object> agentState) {

            this.totalReward   = totalReward;
            this.episodeReward = episodeReward;
            this.episode       = episode;
            this.policyType    = policyType;
            this.policyData    = policyData;
            this.agentState    = agentState;
        }
    }

    /* =========================
       JSON HELPER
    ========================= */

    private static void writeJsonValue(PrintWriter pw, Object val) {

        if (val == null) {
            pw.print("null");
        }
        else if (val instanceof Number || val instanceof Boolean) {
            pw.print(val);
        }
        else if (val instanceof Map) {

            pw.print("{");

            Map<?, ?> map = (Map<?, ?>) val;
            int count = 0;

            for (Map.Entry<?, ?> e : map.entrySet()) {
                pw.print("\"" + e.getKey() + "\": ");
                writeJsonValue(pw, e.getValue());

                if (++count < map.size()) pw.print(",");
            }

            pw.print("}");
        }
        else {
            pw.print("\"" + val.toString().replace("\"", "\\\"") + "\"");
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
                                  int episode,
                                  Map<String, Object> agentState
    ) throws IOException {

        new File(filename).getParentFile().mkdirs();

        try (PrintWriter pw = new PrintWriter(new FileWriter(filename))) {

            int nrofAction = qTable.getNrofAction();

            pw.println("{");

            /* POLICY */
            pw.println("\"policy\": {");

            if (policy instanceof PolicyPersistence) {
                PolicyPersistence p = (PolicyPersistence) policy;

                pw.println("\"type\": \"" + p.getPolicyType() + "\",");

                Map<String, Object> data = p.exportState();

                int count = 0;
                for (Map.Entry<String, Object> entry : data.entrySet()) {
                    pw.print("\"" + entry.getKey() + "\": ");
                    writeJsonValue(pw, entry.getValue());

                    if (++count < data.size()) pw.println(",");
                }
                pw.println();
            }

            pw.println("},");

            /* AGENT STATE */
            pw.print("\"agentState\": ");
            writeJsonValue(pw, agentState != null ? agentState : new HashMap<>());
            pw.println(",");

            /* TRAINING */
            pw.println("\"training\": {");
            pw.println("\"totalReward\": " + totalReward + ",");
            pw.println("\"episodeReward\": " + episodeReward + ",");
            pw.println("\"episode\": " + episode);
            pw.println("},");

            /* QTABLE */
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
                pw.println("]");

                if (qTable.isUseVisitCount()) {
                    pw.print(",\"visitCounts\": [");
                    for (int a = 0; a < nrofAction; a++) {
                        pw.print(qTable.getVisitCount(state, a));
                        if (a < nrofAction - 1) pw.print(",");
                    }
                    pw.print("]");
                }

                pw.print("}");
            }

            pw.println();
            pw.println("],");

            /* ROOT */
            pw.println("\"totalReward\": " + totalReward + ",");
            pw.println("\"episodeReward\": " + episodeReward + ",");
            pw.println("\"episode\": " + episode);

            pw.println("}");
        }

        System.out.println("✅ Saved JSON: " + filename);
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
        Map<String, Object> agentState = new HashMap<>();

        int nrofAction = qTable.getNrofAction();

        while ((line = br.readLine()) != null) {

            line = line.trim();

            /* POLICY */
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
                        String val = line.split(":", 2)[1].replace(",","").trim();

                        try {
                            policyData.put(key, Double.parseDouble(val));
                        } catch (Exception e) {
                            policyData.put(key, val.replace("\"",""));
                        }
                    }

                    if (line.startsWith("}")) break;
                }
            }

            /* AGENT STATE */
            if (line.startsWith("\"agentState\"")) {

                String json = line.substring(line.indexOf("{") + 1, line.lastIndexOf("}"));

                String[] pairs = json.split(",");

                for (String pair : pairs) {
                    if (!pair.contains(":")) continue;

                    String[] kv = pair.split(":", 2);

                    String key = kv[0].replace("\"","").trim();
                    String val = kv[1].replace("\"","").trim();

                    try {
                        agentState.put(key, Double.parseDouble(val));
                    } catch (Exception e) {
                        agentState.put(key, val);
                    }
                }
            }

            /* TRAINING */
            if (line.startsWith("\"totalReward\""))
                totalReward = Double.parseDouble(line.split(":")[1].replace(",","").trim());

            if (line.startsWith("\"episodeReward\""))
                episodeReward = Double.parseDouble(line.split(":")[1].replace(",","").trim());

            if (line.startsWith("\"episode\""))
                episode = Integer.parseInt(line.split(":")[1].replace(",","").trim());

            /* QTABLE */
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

        return new LoadResult(
                totalReward,
                episodeReward,
                episode,
                policyType,
                policyData,
                agentState
        );
    }

    /* =========================
       SAVE CSV
    ========================= */

    public static void saveToCSV(String filename,
                                 QTable qTable,
                                 BehaviorPolicy policy,
                                 double totalReward,
                                 double episodeReward,
                                 int episode,
                                 Map<String, Object> agentState
    ) throws IOException {

        new File(filename).getParentFile().mkdirs();

        try (PrintWriter pw = new PrintWriter(new FileWriter(filename))) {

            int nrofAction = qTable.getNrofAction();

            pw.println("#POLICY");

            if (policy instanceof PolicyPersistence) {
                PolicyPersistence p = (PolicyPersistence) policy;

                pw.println("type=" + p.getPolicyType());

                for (Map.Entry<String, Object> entry : p.exportState().entrySet()) {
                    pw.println(entry.getKey() + "=" + entry.getValue());
                }
            }

            pw.println("#AGENT_STATE");

            if (agentState != null) {
                for (Map.Entry<String, Object> entry : agentState.entrySet()) {
                    pw.println(entry.getKey() + "=" + entry.getValue());
                }
            }

            pw.println("#TRAINING");
            pw.println(totalReward + "," + episodeReward + "," + episode);

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
        }

        System.out.println("✅ Saved CSV: " + filename);
    }

    /* =========================
       LOAD CSV
    ========================= */

    public static LoadResult loadFromCSV(String filename, QTable qTable) throws IOException {

        File file = new File(filename);
        if (!file.exists()) return null;

        BufferedReader br = new BufferedReader(new FileReader(file));

        String line, mode = "";

        double totalReward = 0;
        double episodeReward = 0;
        int episode = 0;

        String policyType = "";
        Map<String, Object> policyData = new HashMap<>();
        Map<String, Object> agentState = new HashMap<>();

        int nrofAction = qTable.getNrofAction();

        while ((line = br.readLine()) != null) {

            line = line.trim();
            if (line.isEmpty()) continue;

            if (line.startsWith("#")) {
                mode = line;
                continue;
            }

            switch (mode) {

                case "#POLICY":
                    if (line.startsWith("type=")) {
                        policyType = line.split("=", 2)[1];
                    } else {
                        String[] parts = line.split("=", 2);
                        try {
                            policyData.put(parts[0], Double.parseDouble(parts[1]));
                        } catch (Exception e) {
                            policyData.put(parts[0], parts[1]);
                        }
                    }
                    break;

                case "#AGENT_STATE":
                    String[] parts = line.split("=", 2);
                    if (parts.length == 2) {
                        try {
                            agentState.put(parts[0], Double.parseDouble(parts[1]));
                        } catch (Exception e) {
                            agentState.put(parts[0], parts[1]);
                        }
                    }
                    break;

                case "#TRAINING":
                    String[] t = line.split(",");
                    totalReward = Double.parseDouble(t[0]);
                    episodeReward = Double.parseDouble(t[1]);
                    episode = Integer.parseInt(t[2]);
                    break;

                case "#QTABLE":
                    String[] q = line.split(",");
                    int state = Integer.parseInt(q[0]);
                    int idx = 1;

                    for (int a = 0; a < nrofAction; a++) {
                        qTable.setQValue(state, a, Double.parseDouble(q[idx++]));
                    }

                    if (qTable.isUseVisitCount()) {
                        for (int a = 0; a < nrofAction; a++) {
                            qTable.setVisitCount(state, a, Integer.parseInt(q[idx++]));
                        }
                    }
                    break;
            }
        }

        br.close();

        System.out.println("✅ Loaded CSV: " + filename);

        return new LoadResult(
                totalReward,
                episodeReward,
                episode,
                policyType,
                policyData,
                agentState
        );
    }
}