package movement.util;

import org.apache.commons.math3.random.RandomGenerator;

import java.util.Objects;
import java.util.Random;

/**
 * Minimal adapter from {@link java.util.Random} to Commons-Math {@link RandomGenerator}.
 * This keeps all random draws (Gaussian TS, Beta TS, tie-breaking) on the same RNG stream.
 */
public class AdaptedJavaRandom implements RandomGenerator {
	private final Random delegate;

	public AdaptedJavaRandom(Random delegate) {
		this.delegate = Objects.requireNonNull(delegate, "delegate");
	}

	@Override
	public void setSeed(int seed) {
		delegate.setSeed(seed);
	}

	@Override
	public void setSeed(int[] seed) {
		// Collapse int[] seed into a long using a simple mixing function.
		long mixed = 0L;
		for (int s : seed) {
			mixed = mixed * 31L + s;
		}
		delegate.setSeed(mixed);
	}

	@Override
	public void setSeed(long seed) {
		delegate.setSeed(seed);
	}

	@Override
	public void nextBytes(byte[] bytes) {
		delegate.nextBytes(bytes);
	}

	@Override
	public int nextInt() {
		return delegate.nextInt();
	}

	@Override
	public int nextInt(int n) {
		return delegate.nextInt(n);
	}

	@Override
	public long nextLong() {
		return delegate.nextLong();
	}

	@Override
	public boolean nextBoolean() {
		return delegate.nextBoolean();
	}

	@Override
	public float nextFloat() {
		return delegate.nextFloat();
	}

	@Override
	public double nextDouble() {
		return delegate.nextDouble();
	}

	@Override
	public double nextGaussian() {
		return delegate.nextGaussian();
	}
}