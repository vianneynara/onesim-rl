package movement.util;

public class MovUtil {

		/**
	 * Computes a wall-bounce for a movement step that would exit the world bounds.
	 * <p>
	 * Uses parametric ray-vs-axis-aligned-box intersection to find the exact point
	 * where the step first crosses a boundary wall. The remaining distance after the
	 * wall contact is then reflected about that wall's normal, producing a physically
	 * plausible bounce trajectory without any random direction change.
	 *
	 * @param fromX starting X coordinate
	 * @param fromY starting Y coordinate
	 * @param toX   un-clipped target X (may be out of bounds)
	 * @param toY   un-clipped target Y (may be out of bounds)
	 * @return double[5] = { bounceX, bounceY, reflectedDirection, remainDX, remainDY }
	 * <p>
	 * Made by Claude
	 */
	public static double[] bounce(double fromX, double fromY, double toX, double toY, double maxX, double maxY) {
		double dx = toX - fromX;
		double dy = toY - fromY;

		// Find the smallest t in (0,1] at which the ray (fromX+t*dx, fromY+t*dy) hits a wall.
		double tMin = 1.0;
		boolean hitVertical = false;   // true → hit left/right wall (reflect dx)
		boolean hitHorizontal = false; // true → hit top/bottom wall (reflect dy)

		if (dx > 0 && toX >= maxX) {
			double t = (maxX - fromX) / dx;
			if (t < tMin) {
				tMin = t;
				hitVertical = true;
			}
		}
		if (dx < 0 && toX <= 0) {
			double t = -fromX / dx;
			if (t < tMin) {
				tMin = t;
				hitVertical = true;
			}
		}
		if (dy > 0 && toY >= maxY) {
			double t = (maxY - fromY) / dy;
			if (t < tMin) {
				tMin = t;
				hitHorizontal = true;
				hitVertical = false;
			}
		}
		if (dy < 0 && toY <= 0) {
			double t = -fromY / dy;
			if (t < tMin) {
				tMin = t;
				hitHorizontal = true;
				hitVertical = false;
			}
		}

		// Wall contact point (clamp to avoid floating-point drift outside bounds).
		double bounceX = Math.max(0, Math.min(maxX, fromX + tMin * dx));
		double bounceY = Math.max(0, Math.min(maxY, fromY + tMin * dy));

		// Remaining vector after the bounce point.
		double remDX = (1.0 - tMin) * dx;
		double remDY = (1.0 - tMin) * dy;

		// Reflect the remaining vector about the wall normal.
		if (hitVertical) remDX = -remDX;
		if (hitHorizontal) remDY = -remDY;

		// Derive the new direction angle from the reflected vector.
		double reflectedDir = Math.atan2(
			hitHorizontal ? -dy : dy,
			hitVertical ? -dx : dx);

		return new double[]{bounceX, bounceY, reflectedDir, remDX, remDY};
	}
}
