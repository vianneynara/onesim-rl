package mcrltest.policy;

import java.util.Map;

/**
 * Interface opsional yang diimplementasikan oleh policy
 * yang perlu menyimpan state internalnya (contoh: ThompsonSamplingPolicy).
 *
 * Policy seperti EpsilonGreedyPolicy dan UCBPolicy
 * tidak perlu mengimplementasikan interface ini.
 */
public interface PolicyPersistence {

    /**
     * Identifier unik untuk tipe policy ini.
     * Digunakan saat load untuk memastikan policy yang tersimpan
     * sesuai dengan policy yang sedang digunakan.
     * Contoh: "ThompsonSampling", "EpsilonGreedy"
     */
    String getPolicyType();

    /**
     * Ekspor state internal policy ke Map untuk disimpan.
     * Dipanggil oleh QTableSerializer saat save.
     */
    Map<String, Object> exportState();

    /**
     * Import state internal policy dari Map hasil load.
     * Dipanggil oleh RLAgent setelah load berhasil.
     */
    void importState(Map<String, Object> state);
}