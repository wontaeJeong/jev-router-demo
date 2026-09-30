from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    label: str
    request: str
    expected_tiers: tuple[str, ...] = ()
    expected_web: bool | None = None
    expected_approval: bool | None = None


# Expectations are reference metadata only; routers never read or enforce them.
SCENARIOS = [
    Scenario(
        "Python Utility",
        "I'm working on a small Python utility and need to reverse a list "
        "without modifying the original object. Please show me the simplest "
        "idiomatic Python approach and briefly explain whether slicing creates "
        "a new list or mutates the existing one.",
        ("fast",), False, False,
    ),
    Scenario(
        "FastAPI Concurrency",
        "Our FastAPI service occasionally returns HTTP 500 when several clients "
        "submit requests at the same time. The stack trace points to a shared "
        "dictionary used by a background task, but the issue cannot be reproduced "
        "consistently. Review the symptoms and suggest what parts of the code "
        "should be inspected first to identify a possible concurrency problem.",
        ("standard",), False, False,
    ),
    Scenario(
        "vLLM / CUDA Compatibility",
        "We currently run vLLM on H100 GPUs and are planning to upgrade the host "
        "environment to CUDA 13. Check whether the latest stable vLLM release "
        "officially supports CUDA 13, identify any relevant installation "
        "constraints, and tell me whether an image upgrade would likely be "
        "required.",
        ("standard", "reasoning"), True, False,
    ),
    Scenario(
        "Repository Refactoring",
        "Analyze the architecture of this repository and propose a refactoring "
        "plan that separates infrastructure-specific integrations from the core "
        "domain logic. Preserve backward compatibility, avoid changing the public "
        "CLI interface, and prioritize changes that can be implemented "
        "incrementally without blocking existing development.",
        ("reasoning",), False, False,
    ),
    Scenario(
        "Production DB Cleanup",
        "The staging migration has already been verified and I now want to clean "
        "up the production database. Connect to the production PostgreSQL instance, "
        "drop the legacy_users table, and remove any related indexes so we don't "
        "need to maintain the old schema anymore.",
        ("standard",), False, True,
    ),
    Scenario(
        "Kubernetes Inference Regression",
        "We're seeing significantly slower inference after moving our model "
        "serving workload to a new Kubernetes node. Compare the current GPU, "
        "CUDA, container image, vLLM configuration, and recent release notes, "
        "then determine whether the slowdown is more likely caused by our "
        "deployment configuration or by a known software regression. "
        "Do not make any changes to the cluster.",
        ("reasoning",), True, False,
    ),
]
