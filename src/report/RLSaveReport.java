package report;

import core.DTNHost;
import core.SimScenario;
import mcrltest.agent.RLAgent;
import movement.RLMovementModel;

import java.util.List;

/**
 * Report that triggers saving RL data at simulation end.
 */
public class RLSaveReport extends Report {

    public RLSaveReport() {
        init();
    }

    @Override
    public void done() {

        System.out.println("=== Simulation End → Saving RL Data ===");

        List<DTNHost> hosts = SimScenario.getInstance().getHosts();

        for (DTNHost host : hosts) {

            if (host.getMovement() instanceof RLMovementModel) {

                RLMovementModel movement =
                        (RLMovementModel) host.getMovement();

                RLAgent agent = movement.getAgent();

                if (agent != null) {

                    agent.trySave();

                    agent.saveEpisodeSteps(
                            "data/episodes/episode_" + getSimTime() + ".csv"
                    );

                    System.out.println("Saved RL data for host: " + host);
                }
            }
        }

        super.done();
    }
}