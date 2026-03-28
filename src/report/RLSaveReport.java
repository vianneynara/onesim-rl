package report;

import core.DTNHost;
import core.SimScenario;
import mcrltest.agent.RLAgent;
import mcrltest.qModel.MonteCarloModel;
import mcrltest.qModel.RLModel;
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

                    RLModel model = agent.getRlModel();

                    /* =====================================
                       MONTE CARLO CHECK
                       ===================================== */
                    if (model instanceof MonteCarloModel) {
                        System.out.println("===================================================");
                        System.out.println("BEFORE UPDATE");
                        System.out.println("===================================================");
                        agent.getQTable().printTable();

                        System.out.println("Monte Carlo detected → running episode update");
                        ((MonteCarloModel) model).updateEpisode(agent.getEpisodeSteps());

                        System.out.println("===================================================");
                        System.out.println("AFTER UPDATE");
                        System.out.println("===================================================");
                        agent.getQTable().printTable();
                    }

                    /* =====================================
                       SAVE DATA
                       ===================================== */
                    agent.trySave();

                    agent.saveEpisodeSteps(getSimTime());

                    System.out.println("Saved RL data for host: " + host);
                }
            }
        }

        super.done();
    }
}