"""Large-repository benchmark cases — Maxim Keep monorepo.

NOTE: Maxim Keep is a PRIVATE repository — it is not bundled with this project
and is not available to other users. These cases are committed for methodology
and for the maintainers' own measurements; external users cannot reproduce the
file-hit numbers without access to that corpus (and the default path below is
machine-specific). Treat this as a documented large-repo measurement, not a
runnable public benchmark.

Ground truth is written against the Maxim Keep repo (a large .NET 10 + Nuxt 3 +
Node MCP monorepo), NOT this repo. Point the harness at a checkout via
FASTCONTEXT_BENCH_REPO (defaults to the path below). Answers were verified by
hand on 2026-06-28 against the file that *defines/implements* each behaviour
(callers and interfaces are deliberately excluded from the truth set).

Purpose: the upstream cases.py runs against this small repo, which fits inside a
16k context window, so it cannot show whether a larger `num_ctx` helps. These
queries span a large polyglot tree (C# backend / Vue+TS frontend / JS MCP) so
that exploration trajectories are big enough to actually exercise the context
window. Run the same set at different `num_ctx` / `max_turns` to measure it.

Each case is (query, acceptable_ground_truth_basenames, grep_terms).
"""
from __future__ import annotations

import os

TARGET_REPO = os.getenv(
    "FASTCONTEXT_BENCH_REPO",
    "/mnt/wdblue/stewart/Projects/sasystem",
)

CASES = [
    (
        "Where is the authorization filter that returns 403 when a tenant integration is disabled by an admin?",
        {"RequireTenantIntegrationAttribute.cs"},
        "RequireTenantIntegration|integrationDisabled|OnAuthorizationAsync",
    ),
    (
        "Where does the generic user-secrets endpoint refuse the reserved reMarkable key with a 404?",
        {"UserSecretsController.cs"},
        "ReservedUserSecretKeys|remarkable-ssh|NotFound",
    ),
    (
        "Where are a new user's daily briefing default settings (enabled flag, timezone) created when they have none saved?",
        {"BriefingController.cs"},
        "GetOrCreateSettingsAsync|Timezone|Europe/London",
    ),
    (
        "Where is the uncached read that checks whether a tenant integration is enabled, backed by system_configuration?",
        {"TenantIntegrationSettings.cs"},
        "IsEnabledAsync|AsNoTracking|admin.integrations",
    ),
    (
        "Where does the API run EF Core database migrations on startup?",
        {"MigrationRunner.cs"},
        "MigrateAsync|Database.Migrate|MigrationRunner",
    ),
    (
        "Where is a user's per-feature access checked against their assigned feature profile?",
        {"FeatureProfileService.cs"},
        "HasFeatureAccessAsync|EnabledFeatures|GetUserProfileAsync",
    ),
    (
        "Where is a user's personal memory vault repository created if it does not already exist?",
        {"MemoryVaultService.cs"},
        "GetOrCreateVaultAsync|IsPersonal|OwnerUserId",
    ),
    (
        "Where is the frontend store that reports whether an integration is enabled, failing closed on error?",
        {"integrations.ts"},
        "useIntegrationsStore|isEnabled|fail-closed",
    ),
    (
        "Where do the MCP reMarkable tools detect that the integration is disabled by the administrator?",
        {"remarkable-handlers.js"},
        "isIntegrationDisabled|integrationDisabled|disabled by your administrator",
    ),
    (
        "Where are JWT tokens issued with the userId claim when a user logs in?",
        {"AuthService.cs"},
        "userId|GenerateToken|new Claim",
    ),
]
