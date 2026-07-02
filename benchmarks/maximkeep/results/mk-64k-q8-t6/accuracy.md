# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-29
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 10
max_turns: 6
num_ctx: `65536`

- label: `mk-64k-q8-t6`
- endpoint: `http://192.168.0.248:11434/v1`
- model: `fc-q8-nothink-64k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 44/100** (2 attempt(s) timed out, counted as misses)

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 4/10 | RequireTenantIntegrationAttribute.cs | FeatureAuthorizeAttribute.cs, Program.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.test.js, remarkable-status.test.js, useRemarkableApi.ts | 25.9 |
| 2 | 8/10 | UserSecretsController.cs | RemarkableController.cs, ReservedUserSecretKeyTests.cs, UserSecretsController.cs, useRemarkableApi.ts | 55.5 |
| 3 | 4/10 | BriefingController.cs | 062_daily_briefing_entity_type.sql, 063_default_briefing_sources.sql, 20260410085751_AddMorningBriefing.cs, BriefingAssemblyJob.cs, BriefingAssemblyService.cs, BriefingController.cs, usePulseSettings.ts | 92.4 |
| 4 | 0/10 | TenantIntegrationSettings.cs | 20250928121742_InitialCreateWithStateManagement.cs, 20251008201252_AddPredicateTypeConstraints.Designer.cs, 20260106131654_AddDocumentSourceTracking.Designer.cs, 20260422082245_AddShadowAndPatternLibraryRepoClassifications.Designer.cs, 20260422084024_AddComprehensionJobTable.Designer.cs, AzureCompletionService.cs, AzureOpenAIEmbeddingService.cs, DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs, Program.cs, SystemConfigurationEntityConfiguration.cs, architecture.vue | 144.6 |
| 5 | 6/10 | MigrationRunner.cs | IMigrationRunner.cs, MigrationRunner.cs, Program.cs, application-modes.md | 177.3 |
| 6 | 8/10 | FeatureProfileService.cs | FeatureAuthorizeAttribute.cs, FeatureProfileConfiguration.cs, FeatureProfileService.cs, FeatureProfilesController.cs, UserFeatureProfileConfiguration.cs, featureProfile.ts | 209.3 |
| 7 | 7/10 | MemoryVaultService.cs | 057_memory_entity_types.sql, 058_memory_relationship_predicates.sql, GetMemoryContextHandler.cs, JitProvisioningService.cs, MemoryVaultService.cs, user-memory-vault.md | 237.0 |
| 8 | 3/10 | integrations.ts | TenantIntegrationSettings.cs, feature-flags.js, index.vue, integrations-store.spec.ts, integrations.ts, remarkable-handlers.js, remarkable-list.js, remarkable-status.js, remarkable.vue | 331.3 |
| 9 | 0/10 | remarkable-handlers.js | FeatureFlagsController.cs, McpClaudeProvider.cs, RemarkableController.cs, RequireTenantIntegrationAttribute.cs, feature-flags.js, featureFlags.ts, remarkable-list.js, remarkable-status.js, remarkable-status.test.js, remarkable.js, remarkable.vue, useRemarkableApi.ts | 385.5 |
| 10 | 4/10 | AuthService.cs | AuthAdminController.cs, AuthController.cs, AuthService.cs, EntraAuthController.cs, EntraHandoffCookie.cs, EntraOidcService.cs, Program.cs, auth.ts | 450.8 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
