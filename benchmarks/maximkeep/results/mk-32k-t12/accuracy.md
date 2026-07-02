# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-28
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 3
max_turns: 12
num_ctx: `32768`

- label: `mk-32k-t12`
- endpoint: `http://192.168.0.4:11434/v1`
- model: `fc-q4-nothink-32k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 11/30** (1 attempt(s) timed out, counted as misses)

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 2/3 | RequireTenantIntegrationAttribute.cs | CHANGELOG.md, FeatureAuthorizeAttribute.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js, remarkable-list.test.js, remarkable-status.test.js | 12.0 |
| 2 | 2/3 | UserSecretsController.cs | CHANGELOG.md, ImplementationContextController.cs, MemoryBookmarksController.cs, ReservedUserSecretKeyTests.cs, UserSecretsController.cs, index.js, useRemarkableApi.ts | 23.0 |
| 3 | 1/3 | BriefingController.cs | 044_feature_profiles.sql, 062_daily_briefing_entity_type.sql, 063_default_briefing_sources.sql, 2026-04-10-morning-briefing.md, 20260411210606_AddUserSecretTable.Designer.cs, BriefingController.cs, useBriefingApi.ts | 35.0 |
| 4 | 0/3 | TenantIntegrationSettings.cs | 20250928121742_InitialCreateWithStateManagement.cs, 20251008201252_AddPredicateTypeConstraints.Designer.cs, 2026-04-23-architecture-area-design.md, 20260218124709_AddDefaultAreaPathToConnection.Designer.cs, 20260422082245_AddShadowAndPatternLibraryRepoClassifications.Designer.cs, DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs, Program.cs | 44.3 |
| 5 | 0/3 | MigrationRunner.cs | 20250928121742_InitialCreateWithStateManagement.cs, 20260422082245_AddShadowAndPatternLibraryRepoClassifications.Designer.cs, Program.cs, SeedDataRegressionTests.cs, SqlFileExecutor.cs, check-migrations.sh | 53.0 |
| 6 | 2/3 | FeatureProfileService.cs | FeatureAuthorizeAttribute.cs, FeatureProfileService.cs, FeatureProfilesController.cs, IFeatureProfileService.cs, featureProfile.ts, profile.ts, useFeatureProfile.ts | 65.0 |
| 7 | 3/3 | MemoryVaultService.cs | 2026-04-20-team-memory-vaults-spec.md, MemoryController.cs, MemoryVaultService.cs, user-memory-vault.md | 83.3 |
| 8 | 0/3 | integrations.ts | EntityCard.vue, inclusion-rules.spec.ts, predicate-visibility.spec.ts, remarkable-handlers.js | 102.0 |
| 9 | 0/3 | remarkable-handlers.js | feature-flags.js, remarkable-status.js, useRemarkableApi.ts | 154.3 |
| 10 | 1/3 | AuthService.cs | AuthService.cs, Program.cs, README.md, WP-033-Document-References-Required-Reading.md, apps.tf, outputs.tf | 118.7 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
