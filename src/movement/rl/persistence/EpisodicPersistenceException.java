package movement.rl.persistence;

public class EpisodicPersistenceException extends RuntimeException {

    public EpisodicPersistenceException(String message, Throwable cause) {
        super(message, cause);
    }

    public EpisodicPersistenceException(String message) {
        super(message);
    }
}