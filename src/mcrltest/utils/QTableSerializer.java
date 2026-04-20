package mcrltest.utils;

import mcrltest.policy.BehaviorPolicy;
import mcrltest.policy.PolicyPersistence;

import java.io.*;
import java.util.*;

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
       JSON WRITER
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
        else if (val instanceof List) {

            pw.print("[");
            List<?> list = (List<?>) val;

            for (int i = 0; i < list.size(); i++) {
                writeJsonValue(pw, list.get(i));
                if (i < list.size() - 1) pw.print(",");
            }

            pw.print("]");
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
            pw.println("]");

            pw.println("}");
        }

        System.out.println("✅ Saved JSON: " + filename);
    }

    /* =========================
       SIMPLE JSON PARSER
    ========================= */

    private static Object parseValue(String s) {

        s = s.trim();

        if (s.startsWith("{")) return parseObject(s);
        if (s.startsWith("[")) return parseArray(s);
        if (s.startsWith("\"")) return s.substring(1, s.length() - 1);

        if ("true".equalsIgnoreCase(s)) return true;
        if ("false".equalsIgnoreCase(s)) return false;
        if ("null".equalsIgnoreCase(s)) return null;

        try {
            if (s.contains(".")) return Double.parseDouble(s);
            return Integer.parseInt(s);
        } catch (Exception e) {
            return s;
        }
    }

    private static Map<String, Object> parseObject(String s) {

        Map<String, Object> map = new HashMap<>();

        s = s.trim();
        s = s.substring(1, s.length() - 1); // remove {}

        int i = 0;

        while (i < s.length()) {

            if (s.charAt(i) == '"') {

                int keyEnd = s.indexOf('"', i + 1);
                String key = s.substring(i + 1, keyEnd);

                int colon = s.indexOf(":", keyEnd);
                int valueStart = colon + 1;

                int braceCount = 0;
                int bracketCount = 0;
                int j = valueStart;

                for (; j < s.length(); j++) {
                    char c = s.charAt(j);

                    if (c == '{') braceCount++;
                    if (c == '}') braceCount--;
                    if (c == '[') bracketCount++;
                    if (c == ']') bracketCount--;

                    if (c == ',' && braceCount == 0 && bracketCount == 0) break;
                }

                String valueStr = s.substring(valueStart, j).trim();
                map.put(key, parseValue(valueStr));

                i = j + 1;
            } else {
                i++;
            }
        }

        return map;
    }

    private static List<Object> parseArray(String s) {

        List<Object> list = new ArrayList<>();

        s = s.trim();
        s = s.substring(1, s.length() - 1); // remove []

        int i = 0;

        while (i < s.length()) {

            int braceCount = 0;
            int bracketCount = 0;
            int j = i;

            for (; j < s.length(); j++) {
                char c = s.charAt(j);

                if (c == '{') braceCount++;
                if (c == '}') braceCount--;
                if (c == '[') bracketCount++;
                if (c == ']') bracketCount--;

                if (c == ',' && braceCount == 0 && bracketCount == 0) break;
            }

            String val = s.substring(i, j).trim();
            if (!val.isEmpty()) {
                list.add(parseValue(val));
            }

            i = j + 1;
        }

        return list;
    }

    /* =========================
       LOAD JSON (FIXED)
    ========================= */

    public static LoadResult loadFromJSON(String filename, QTable qTable) throws IOException {

        File file = new File(filename);
        if (!file.exists()) return null;

        StringBuilder sb = new StringBuilder();
        BufferedReader br = new BufferedReader(new FileReader(file));

        String line;
        while ((line = br.readLine()) != null) {
            sb.append(line.trim());
        }
        br.close();

        Map<String, Object> root = parseObject(sb.toString());

        /* POLICY */
        Map<String, Object> policyMap = (Map<String, Object>) root.get("policy");

        String policyType = (String) policyMap.get("type");

        Map<String, Object> policyData = new HashMap<>(policyMap);
        policyData.remove("type");

        /* AGENT STATE */
        Map<String, Object> agentState =
                (Map<String, Object>) root.getOrDefault("agentState", new HashMap<>());

        /* TRAINING */
        Map<String, Object> training = (Map<String, Object>) root.get("training");

        double totalReward = ((Number) training.get("totalReward")).doubleValue();
        double episodeReward = ((Number) training.get("episodeReward")).doubleValue();
        int episode = ((Number) training.get("episode")).intValue();

        /* QTABLE */
        List<Map<String, Object>> states =
                (List<Map<String, Object>>) root.get("states");

        int nrofAction = qTable.getNrofAction();

        for (Map<String, Object> s : states) {

            int state = ((Number) s.get("state")).intValue();

            List<Object> qVals = (List<Object>) s.get("qValues");
            for (int i = 0; i < nrofAction; i++) {
                qTable.setQValue(state, i,
                        ((Number) qVals.get(i)).doubleValue());
            }

            if (qTable.isUseVisitCount() && s.containsKey("visitCounts")) {

                List<Object> counts = (List<Object>) s.get("visitCounts");

                for (int i = 0; i < nrofAction; i++) {
                    qTable.setVisitCount(state, i,
                            ((Number) counts.get(i)).intValue());
                }
            }
        }

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