package report;

import core.DTNHost;
import core.SimScenario;
import mcrltest.utils.DetectionInfo;
import movement.RLMovementModel;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TargetDetectionReport extends Report {

    private Map<DTNHost, Integer> targetDetection;

    public TargetDetectionReport() {
        super();
        this.targetDetection = new HashMap<>();
    }

    @Override
    public void done() {
            /* ===== GET HOSTS PROPERLY ===== */
            List<DTNHost> hosts = SimScenario.getInstance().getHosts();

            for (DTNHost host : hosts) {

                if (host.getMovement() instanceof RLMovementModel) {

                    RLMovementModel movement =
                            (RLMovementModel) host.getMovement();

                    Map<DTNHost, DetectionInfo> objectiveFound = movement.getObjectiveFound();

                    for (Map.Entry<DTNHost, DetectionInfo> step : objectiveFound.entrySet()) {
                        DTNHost theHost = step.getKey();
                        int count = step.getValue().getNrofMeet();

                        targetDetection.put(theHost, count);
                    }
                }
            }

            write("Total Target Found: " + targetDetection.size() + "/" + hosts.size());

            /* ===== WRITE RESULT ===== */
            for (Map.Entry<DTNHost, Integer> entry : targetDetection.entrySet()) {
                write(entry.getKey().getName() + "," + entry.getValue());
            }

        super.done();
    }
}