package mcrltest.policy;

import java.util.Map;

public interface PolicyPersistence {

    String getPolicyType();

    Map<String, Object> exportState();

    void importState(Map<String, Object> data);
}