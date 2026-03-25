package report;

import core.DTNHost;
import core.SimScenario;
import mcrltest.agent.RLAgent;
import mcrltest.utils.EpisodeStep;
import movement.RLMovementModel;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TrajectoryFrequencyReport extends Report {

    private Map<Integer, Integer> runFrequency;

    public TrajectoryFrequencyReport() {
        super();
        this.runFrequency = new HashMap<>();
    }

    @Override
    public void done() {
            /* ===== GET HOSTS PROPERLY ===== */
            List<DTNHost> hosts = SimScenario.getInstance().getHosts();

            for (DTNHost host : hosts) {

                if (host.getMovement() instanceof RLMovementModel) {

                    RLMovementModel movement =
                            (RLMovementModel) host.getMovement();

                    RLAgent agent = movement.getAgent();

                    if (agent == null) continue;

                    List<EpisodeStep> steps = agent.getEpisodeSteps();

                    int straightCount = 0;

                    for (EpisodeStep step : steps) {

                        if (step.getAction() == 0) {
                            // STRAIGHT
                            straightCount++;
                        }
                        else if (step.getAction() == 1) {
                            // TURN → record run

                            if (straightCount > 0) {
                                runFrequency.put(
                                        straightCount,
                                        runFrequency.getOrDefault(straightCount, 0) + 1
                                );
                            }

                            straightCount = 0;
                        }
                    }

                    /* handle ending without turn */
                    if (straightCount > 0) {
                        runFrequency.put(
                                straightCount,
                                runFrequency.getOrDefault(straightCount, 0) + 1
                        );
                    }
                }
            }

            /* ===== WRITE RESULT ===== */
            for (Map.Entry<Integer, Integer> entry : runFrequency.entrySet()) {
                write(entry.getKey() + "," + entry.getValue());
            }

        super.done();
    }
}