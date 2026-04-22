package mcrltest.utils;

import core.SimClock;

import java.io.Serializable;

/**
 * DetectionInfo stores information about a detected target and
 * manages reward cooldown to prevent repeated rewards every tick.
 *
 * Used by RLMovementModel to track when a target was seen and
 * whether a reward can be granted again.
 */
public class DetectionInfo implements Serializable {

    private double lastDetectionTime;
    private double lastRewardTime;
    private double cooldown;

    private int nrofMeet;

    private boolean destructive;

    private boolean newlyDetected;
    private boolean alreadyRewarded;

    private DetectionInfo(double lastDetectionTime,
                          double lastRewardTime,
                          double cooldown,
                          boolean destructive) {

        this.lastDetectionTime = lastDetectionTime;
        this.lastRewardTime = lastRewardTime;
        this.cooldown = cooldown;

        this.destructive = destructive;

        this.nrofMeet = 0;
        this.newlyDetected = false;
        this.alreadyRewarded = false;
    }

    public static DetectionInfo of(double lastDetectionTime,
                                   double lastRewardTime,
                                   double cooldown,
                                   boolean destructive) {

        return new DetectionInfo(
                lastDetectionTime,
                lastRewardTime,
                cooldown,
                destructive
        );
    }

    /**
     * Called when connection (detection) happens
     */
    public void update(double now) {
        this.lastDetectionTime = now;
        this.nrofMeet++;
        this.newlyDetected = true;
    }

    /**
     * 🔥 MAIN REWARD LOGIC
     */
    public boolean consumeDetectionReward() {

        double now = SimClock.getTime();

        /* =========================
           🔴 DESTRUCTIVE TARGET
           ========================= */
        if (destructive) {
            if (alreadyRewarded) {
                return false;
            }

            if (newlyDetected) {
                newlyDetected = false;
                alreadyRewarded = true;
                lastRewardTime = now;
                return true;
            }

            return false;
        }

        /* =========================
        🔵 NON-DESTRUCTIVE TARGET
        ========================= */
        else {
            if (newlyDetected) {

                /* 🔥 FIRST TIME: always reward */
                if (lastRewardTime == Double.NEGATIVE_INFINITY) {

                    newlyDetected = false;
                    lastRewardTime = now;

                    return true;
                }

                /* 🔥 NEXT TIMES: respect cooldown */
                if (now - lastRewardTime >= cooldown) {
                    newlyDetected = false;
                    lastRewardTime = now;

                    return true;
                }
            }

            return false;
        }
    }

    public int getNrofMeet() {
        return nrofMeet;
    }

    public boolean isDestructive() {
        return destructive;
    }
}