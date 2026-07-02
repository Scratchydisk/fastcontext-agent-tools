# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-28
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 3
max_turns: 6
num_ctx: `32768`

- label: `mk-32k-t6`
- endpoint: `http://192.168.0.4:11434/v1`
- model: `fc-q4-nothink-32k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 14/30** (2 attempt(s) timed out, counted as misses)

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 0/3 | RequireTenantIntegrationAttribute.cs | CHANGELOG.md, FeatureProfilesController.cs, McpController.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js, remarkable-handlers.test.js, useRemarkableApi.ts | 8.0 |
| 2 | 3/3 | UserSecretsController.cs | IntegrationCatalog.cs, UserSecretsController.cs, useRemarkableApi.ts, useUserSecretsApi.ts | 21.7 |
| 3 | 2/3 | BriefingController.cs | 062_daily_briefing_entity_type.sql, BriefingAssemblyJob.cs, BriefingController.cs | 33.7 |
| 4 | 0/3 | TenantIntegrationSettings.cs | 20250928121742_InitialCreateWithStateManagement.cs, 20251008201252_AddPredicateTypeConstraints.Designer.cs, 20260218124709_AddDefaultAreaPathToConnection.Designer.cs, 20260422082245_AddShadowAndPatternLibraryRepoClassifications.Designer.cs, DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs, metadata_catalog_design.md | 47.3 |
| 5 | 2/3 | MigrationRunner.cs | IMigrationRunner.cs, MigrationRunner.cs, Program.cs, check-migrations.sh | 62.7 |
| 6 | 2/3 | FeatureProfileService.cs | FeatureProfileService.cs, FeatureProfilesController.cs, IFeatureProfileService.cs, profile.ts | 75.3 |
| 7 | 3/3 | MemoryVaultService.cs | 2026-04-20-team-memory-vaults-spec.md, 2026-06-27-entra-id-integration-design.md, 2026-06-27-entra-id-integration.md, IMemoryVaultService.cs, MemoryVaultService.cs, user-memory-vault.md | 88.7 |
| 8 | 0/3 | integrations.ts | TenantIntegrationSettings.cs, inclusion-rules.spec.ts, predicate-visibility.spec.ts | 149.3 |
| 9 | 2/3 | remarkable-handlers.js | CHANGELOG.md, RequireTenantIntegrationAttribute.cs, remarkable-handlers.js, remarkable-list.js, remarkable-status.js, remarkable.js, tool-categories.js, useRemarkableApi.ts | 173.0 |
| 10 | 0/3 | AuthService.cs | auth.ts | 61.7 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
