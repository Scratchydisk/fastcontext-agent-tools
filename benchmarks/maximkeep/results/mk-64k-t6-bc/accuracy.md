# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-28
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 10
max_turns: 6
num_ctx: `65536`

- label: `mk-64k-t6-bc`
- endpoint: `http://192.168.0.22:11434/v1`
- model: `fc-q4-nothink-64k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 28/100** (11 attempt(s) timed out, counted as misses)

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 6/10 | RequireTenantIntegrationAttribute.cs | FeatureAuthorizeAttribute.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.js, remarkable-list.test.js, remarkable-status.test.js, useRemarkableApi.ts | 18.4 |
| 2 | 5/10 | UserSecretsController.cs | EntitiesController.cs, IntegrationCatalog.cs, RemarkableController.cs, ReservedUserSecretKeyTests.cs, UserSecretsController.cs, http-bridge.js, index.js, useRemarkableApi.ts | 55.2 |
| 3 | 0/10 | BriefingController.cs | 061_briefing_topic_entity_type.sql, 062_daily_briefing_entity_type.sql, 063_default_briefing_sources.sql, BriefingAssemblyJob.cs, BriefingAssemblyService.cs, ITenantIntegrationSettings.cs, TenantIntegrationSettings.cs, UserBriefingSettingsConfiguration.cs | 67.1 |
| 4 | 1/10 | TenantIntegrationSettings.cs | 001_system_configuration.sql, 20250928121742_InitialCreateWithStateManagement.cs, 20251008201252_AddPredicateTypeConstraints.Designer.cs, 20260422084024_AddComprehensionJobTable.Designer.cs, AdminIntegrationsController.cs, AzureCompletionService.cs, AzureOpenAIEmbeddingService.cs, DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs, MeIntegrationsController.cs, Program.cs, SystemConfigurationEntityConfiguration.cs, TenantIntegrationSettings.cs, architecture.vue, metadata_catalog_design.md | 124.7 |
| 5 | 4/10 | MigrationRunner.cs | 20250928121742_InitialCreateWithStateManagement.cs, ApplicationMode.cs, CodebaseScanner.cs, MigrationRunner.cs, Program.cs, SeedDataRegressionTests.cs, SqlFileExecutor.cs, application-modes.md, deploy.sh | 189.6 |
| 6 | 2/10 | FeatureProfileService.cs | FeatureAuthorizeAttribute.cs, FeatureProfileService.cs, FeatureProfilesController.cs, IFeatureProfileService.cs | 197.2 |
| 7 | 4/10 | MemoryVaultService.cs | 2026-04-20-memory-retrieval-first-slice-spec.md, 2026-04-20-team-memory-vaults-spec.md, 2026-06-27-entra-id-integration-design.md, 20260422082245_AddShadowAndPatternLibraryRepoClassifications.Designer.cs, Entity.cs, IMemoryVaultService.cs, MemoryController.cs, MemoryVaultService.cs, README.md, VaultPreservationTests.cs, user-memory-vault.md | 255.9 |
| 8 | 2/10 | integrations.ts | AdminIntegrationsController.cs, inclusion-rules.spec.ts, index.vue, integrations-store.spec.ts, integrations.ts, predicate-toggles.spec.ts, remarkable.vue, usePredicateToggles.ts | 371.2 |
| 9 | 3/10 | remarkable-handlers.js | 2026-06-20-opencode-mimocode-first-class-design.md, CHANGELOG.md, RemarkableController.cs, RequireTenantIntegrationAttribute.cs, feature-flags.js, feature.ts, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.js, remarkable-status.js, useRemarkableApi.ts | 477.2 |
| 10 | 1/10 | AuthService.cs | AuthService.cs, AuthServiceTests.cs, EntraHandoffCookie.cs, EntraStateCookie.cs, IAuthService.cs, Program.cs, auth.ts | 262.8 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
