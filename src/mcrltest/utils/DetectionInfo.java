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
public class DetectionInfo {
    /** Last time this target was detected */
    private double lastDetectionTime;

    /** Last time reward was granted */
    private double lastRewardTime;

    /** Minimum time between rewards */
    private double cooldown;

    private int nrofMeet;

    /**
     * Private constructor (use factory method)
     */
    private DetectionInfo(double lastDetectionTime,
                          double lastRewardTime,
                          double cooldown) {

        this.lastDetectionTime = lastDetectionTime;
        this.lastRewardTime = lastRewardTime;
        this.cooldown = cooldown;
        this.nrofMeet = 0;
    }

    /**
     * Factory method used for initialization
     */
    public static DetectionInfo of(double lastDetectionTime,
                                   double lastRewardTime,
                                   double cooldown) {

        return new DetectionInfo(lastDetectionTime, lastRewardTime, cooldown);
    }

    /**
     * Update detection timestamp when target is seen.
     */
    public void update(double now, double cooldown) {

        this.lastDetectionTime = now;
        this.cooldown = cooldown;

        System.out.println("BEFORE NUMBER OF MEET = " + this.nrofMeet);
        this.nrofMeet++;
        System.out.println("AFTER NUMBER OF MEET = " + this.nrofMeet);

    }

    /**
     * Check whether a reward can be granted again.
     *
     * Reward is allowed only if cooldown has passed.
     */
    public boolean hasAvailableReward() {

        double now = SimClock.getTime();

        if (now - lastRewardTime >= cooldown) {

            lastRewardTime = now;
            return true;

        }

        return false;
    }

    /**
     * Get last time this target was detected.
     */
    public double getLastDetectionTime() {
        return lastDetectionTime;
    }

    /**
     * Get last time reward was given.
     */
    public double getLastRewardTime() {
        return lastRewardTime;
    }

    /**
     * Get reward cooldown duration.
     */
    public double getCooldown() {
        return cooldown;
    }

    public int getNrofMeet() {
        return nrofMeet;
    }

    @Override
    public String toString() {
        return "DetectionInfo{" +
                "lastDetectionTime=" + lastDetectionTime +
                ", lastRewardTime=" + lastRewardTime +
                ", cooldown=" + cooldown +
                '}';
    }
}