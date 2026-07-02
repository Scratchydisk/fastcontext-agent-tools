# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-29
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 10
max_turns: 6
num_ctx: `16384`

- label: `mk-16k-q8-t6`
- endpoint: `http://192.168.0.248:11434/v1`
- model: `fc-q8-nothink-16k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 38/100** (4 attempt(s) timed out, counted as misses)

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 3/10 | RequireTenantIntegrationAttribute.cs | FeatureAuthorizeAttribute.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs | 22.6 |
| 2 | 5/10 | UserSecretsController.cs | IntegrationCatalog.cs, MetadataController.cs, RemarkableController.cs, UserSecretsController.cs, http-bridge.js, index.js, useUserSecretsApi.ts | 49.1 |
| 3 | 1/10 | BriefingController.cs | 044_feature_profiles.sql, 062_daily_briefing_entity_type.sql, 063_default_briefing_sources.sql, 20260410085751_AddMorningBriefing.cs, BriefingAssemblyJob.cs, BriefingController.cs, CreateEntityHandler.cs, UserBriefingSettingsConfiguration.cs, index.vue, useBriefingApi.ts | 82.4 |
| 4 | 0/10 | TenantIntegrationSettings.cs | 20250928121742_InitialCreateWithStateManagement.Designer.cs, 20250928121742_InitialCreateWithStateManagement.cs, 20251008201252_AddPredicateTypeConstraints.Designer.cs, 20260218124709_AddDefaultAreaPathToConnection.Designer.cs, 20260322093723_AddWorkSessionTables.Designer.cs, 20260422082245_AddShadowAndPatternLibraryRepoClassifications.Designer.cs, AzureVisionService.cs, DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs, Program.cs, architecture.vue | 114.0 |
| 5 | 4/10 | MigrationRunner.cs | MigrationRunner.cs, Program.cs | 143.2 |
| 6 | 7/10 | FeatureProfileService.cs | 044_feature_profiles.sql, 20260115132118_AddFeatureProfiles.cs, FeatureAuthorizeAttribute.cs, FeatureProfileConfiguration.cs, FeatureProfileService.cs, UserFeatureProfile.cs, UserFeatureProfileConfiguration.cs, featureProfile.ts, profile.ts, useFeatureProfile.ts | 181.0 |
| 7 | 6/10 | MemoryVaultService.cs | 057_memory_entity_types.sql, JitProvisioningService.cs, MemoryVaultService.cs, RepositoryConfiguration.cs, memory-handlers.js, user-memory-vault.md | 186.0 |
| 8 | 3/10 | integrations.ts | RequireTenantIntegrationAttributeTests.cs, index.vue, integrations-store.spec.ts, integrations.ts, predicate-visibility.ts, remarkable-handlers.js, remarkable-status.js | 296.6 |
| 9 | 3/10 | remarkable-handlers.js | CHANGELOG.md, IntegrationCatalog.cs, RemarkableController.cs, RequireTenantIntegrationAttribute.cs, feature-flags.js, remarkable-handlers.js, remarkable-status.js, remarkable.js | 385.6 |
| 10 | 6/10 | AuthService.cs | AuthAdminController.cs, AuthController.cs, AuthService.cs, EntraAuthController.cs, EntraOidcService.cs, Program.cs, auth.ts | 412.4 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
