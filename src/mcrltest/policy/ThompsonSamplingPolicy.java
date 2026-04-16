package mcrltest.policy;

import core.Settings;
import mcrltest.utils.QTable;

import java.util.Collections;
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
       EXPORT / IMPORT (hanya untuk I/O)
       =============================== */

    /**
     * Dipanggil RLAgent saat save — mengembalikan snapshot tsMap.
     * QTable tidak ikut campur sama sekali.
     */
    public Map<String, TSProperty> exportTsMap() {
        return Collections.unmodifiableMap(tsMap);
    }

    /**
     * Dipanggil RLAgent setelah load — menerima tsMap dari LoadResult,
     * bukan dari QTable.
     */
    public void importTsMap(Map<String, TSProperty> loaded) {
        tsMap.clear();
        tsMap.putAll(loaded);
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
       POLICY PERSISTENCE
       =============================== */

    @Override
    public String getPolicyType() {
        return "ThompsonSampling";
    }

    @Override
    public Map<String, Object> exportState() {
        Map<String, Object> map = new HashMap<>();
        map.put("tsMap", tsMap);
        return map;
    }

    @Override
    public void importState(Map<String, Object> data) {
        if (data.containsKey("tsMap")) {
            tsMap.clear();
            tsMap.putAll((Map<String, TSProperty>) data.get("tsMap"));
        }
    }

    /* ===============================
       TS PROPERTY CLASS
       =============================== */

    public static class TSProperty {
        public double mean;
        public double variance;
        public int    count;

        public TSProperty(double mean, double variance) {
            this(mean, variance, 0);
        }

        public TSProperty(double mean, double variance, int count) {
            this.mean     = mean;
            this.variance = variance;
            this.count    = count;
        }

        public double getMean()     { return mean; }
        public double getVariance() { return variance; }
        public int    getCount()    { return count; }
    }
}