"""Feature flags for enabling/disabling features.

All features should check these flags before loading.
Features must work when disabled (graceful degradation).
"""

# Power Profiler feature
ENABLE_POWER_PROFILER = True

# Test Sequences feature
ENABLE_TEST_SEQUENCES = True

# Smart Suggestions feature
ENABLE_SMART_SUGGESTIONS = False

# Dashboard feature (future)
ENABLE_DASHBOARD = False

