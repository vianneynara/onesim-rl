package mcrltest.policy;

import core.Settings;
import mcrltest.utils.QTable;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class ThompsonSamplingPolicy implements BehaviorPolicy, PolicyPersistence {

    public static final String TS_NS = "BehaviorPolicy.Thompson";

    private final double initialVariance;
    private final Map<String, TSProperty> tsMap = new HashMap<>();

    public ThompsonSamplingPolicy(Settings s) {
        Settings set = new Settings(TS_NS);
        this.initialVariance = set.getDouble("initialVariance", 1.0);
    }

    private ThompsonSamplingPolicy(double initialVariance) {
        this.initialVariance = initialVariance;
    }

    /* ===============================
       SELECT ACTION
    =============================== */

    @Override
    public Integer selectAction(int state, QTable qTable, Random random) {

        int nActions = qTable.getNrofAction();

        double bestSample = Double.NEGATIVE_INFINITY;
        int bestAction = 0;

        for (int a = 0; a < nActions; a++) {

            TSProperty prop = tsMap.computeIfAbsent(
                    key(state, a),
                    k -> new TSProperty(0.0, initialVariance)
            );

            double sample = prop.mean +
                    Math.sqrt(Math.max(prop.variance, 0.0)) * random.nextGaussian();

            if (sample > bestSample) {
                bestSample = sample;
                bestAction = a;
            }
        }

        return bestAction;
    }

    /* ===============================
       UPDATE
    =============================== */

    @Override
    public void update(int state, int action, double reward, Random random) {

        TSProperty prop = tsMap.computeIfAbsent(
                key(state, action),
                k -> new TSProperty(0.0, initialVariance)
        );

        int n = prop.count + 1;

        double oldMean = prop.mean;
        double newMean = oldMean + (reward - oldMean) / n;

        double newVar;

        if (n == 1) {
            newVar = initialVariance;
        } else {
            double m2Old = (n >= 3) ? prop.variance * (n - 2) : 0.0;
            double m2New = m2Old + (reward - oldMean) * (reward - newMean);
            newVar = m2New / (n - 1);
        }

        newVar = Math.max(newVar, 1e-6);

        prop.mean     = newMean;
        prop.variance = newVar;
        prop.count    = n;
    }

    /* ===============================
       UTIL
    =============================== */

    private String key(int state, int action) {
        return state + "_" + action;
    }

    /* ===============================
       REPLICATE
    =============================== */

    @Override
    public BehaviorPolicy replicate() {
        return new ThompsonSamplingPolicy(initialVariance);
    }

    @Override
    public String getName() {
        return "ThompsonSampling";
    }

    /* ===============================
       POLICY PERSISTENCE (FIXED)
    =============================== */

    @Override
    public String getPolicyType() {
        return "ThompsonSampling";
    }

    @Override
    public Map<String, Object> exportState() {

        Map<String, Object> root = new HashMap<>();
        Map<String, Object> serializedTS = new HashMap<>();

        for (Map.Entry<String, TSProperty> entry : tsMap.entrySet()) {

            TSProperty p = entry.getValue();

            Map<String, Object> obj = new HashMap<>();
            obj.put("mean", p.mean);
            obj.put("variance", p.variance);
            obj.put("count", p.count);

            serializedTS.put(entry.getKey(), obj);
        }

        root.put("tsMap", serializedTS);
        return root;
    }

    /* ===============================
       🔥 SAFE IMPORT (FIXED)
    =============================== */

    @Override
    public void importState(Map<String, Object> data) {

        if (!data.containsKey("tsMap")) return;

        tsMap.clear();

        Object tsObj = data.get("tsMap");

        Map<String, Object> serializedTS;

        /* ✅ CASE 1: NORMAL MAP */
        if (tsObj instanceof Map) {
            serializedTS = (Map<String, Object>) tsObj;
        }

        /* ⚠️ CASE 2: STRING (your parser problem) */
        else if (tsObj instanceof String) {

            serializedTS = new HashMap<>();

            String str = ((String) tsObj)
                    .replace("{", "")
                    .replace("}", "")
                    .replace("\"", "");

            String[] pairs = str.split(",");

            for (String p : pairs) {

                if (!p.contains("=")) continue;

                String[] kv = p.split("=");

                String key = kv[0].trim();
                String val = kv[1].trim();

                // val format: mean=..., variance=..., count=...
                TSProperty prop = parseTSProperty(val);
                serializedTS.put(key, prop);
            }
        }

        else {
            return;
        }

        /* 🔥 FINAL LOAD */
        for (Map.Entry<String, Object> entry : serializedTS.entrySet()) {

            Object obj = entry.getValue();

            if (obj instanceof TSProperty) {
                tsMap.put(entry.getKey(), (TSProperty) obj);
                continue;
            }

            if (!(obj instanceof Map)) continue;

            Map<String, Object> map = (Map<String, Object>) obj;

            double mean     = getDouble(map.get("mean"), 0.0);
            double variance = getDouble(map.get("variance"), initialVariance);
            int count       = getInt(map.get("count"), 0);

            tsMap.put(entry.getKey(), new TSProperty(mean, variance, count));
        }
    }

    /* ===============================
       🔥 HELPERS
    =============================== */

    private TSProperty parseTSProperty(String str) {

        double mean = 0.0;
        double variance = initialVariance;
        int count = 0;

        String[] parts = str.split(",");

        for (String part : parts) {

            if (part.contains("mean"))
                mean = Double.parseDouble(part.split("=")[1]);

            if (part.contains("variance"))
                variance = Double.parseDouble(part.split("=")[1]);

            if (part.contains("count"))
                count = Integer.parseInt(part.split("=")[1]);
        }

        return new TSProperty(mean, variance, count);
    }

    private double getDouble(Object o, double def) {
        return (o instanceof Number) ? ((Number) o).doubleValue() : def;
    }

    private int getInt(Object o, int def) {
        return (o instanceof Number) ? ((Number) o).intValue() : def;
    }

    /* ===============================
       TS PROPERTY
    =============================== */

    public static class TSProperty {
        public double mean;
        public double variance;
        public int count;

        public TSProperty(double mean, double variance) {
            this(mean, variance, 0);
        }

        public TSProperty(double mean, double variance, int count) {
            this.mean = mean;
            this.variance = variance;
            this.count = count;
        }
    }
}