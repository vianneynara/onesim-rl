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

    /* 🔥 mode */
    private boolean destructive;

    /* 🔥 flags */
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
//            System.out.println("==============================");
//            System.out.println("DESTRUCTIVE");

            if (alreadyRewarded) {
//                System.out.println("HAVE ALREADY BEING REWARDED");
//                System.out.println("==============================");
                return false;
            }

            if (newlyDetected) {
//                System.out.println("FIRST MEET, GIVE REWARD");
//                System.out.println("==============================");
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
//                System.out.println("==============================");
//                System.out.println("NON - DESTRUCTIVE");

                /* 🔥 FIRST TIME: always reward */
                if (lastRewardTime == Double.NEGATIVE_INFINITY) {
//                    System.out.println("FIRST TIME MEET,GIVE REWARD");
//                    System.out.println("==============================");

                    newlyDetected = false;
                    lastRewardTime = now;

                    return true;
                }

//                System.out.println("DIFFERENT : " + (now - lastRewardTime));
//                System.out.println("COOLDOWN : " +cooldown);
//                System.out.println("==============================");

                /* 🔥 NEXT TIMES: respect cooldown */
                if (now - lastRewardTime >= cooldown) {
//                    System.out.println("==============================");
//                    System.out.println("HAVE PAST THE COOLDOWN");
//                    System.out.println("==============================");

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