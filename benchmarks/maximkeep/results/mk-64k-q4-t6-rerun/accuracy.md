# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-29
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 10
max_turns: 6
num_ctx: `65536`

- label: `mk-64k-q4-t6-rerun`
- endpoint: `http://192.168.0.248:11434/v1`
- model: `fc-q4-nothink-64k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 32/100** (12 attempt(s) timed out, counted as misses)

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 6/10 | RequireTenantIntegrationAttribute.cs | FeatureAuthorizeAttribute.cs, ITenantIntegrationSettings.cs, McpController.cs, Program.cs, PulseController.cs, RemarkableController.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, TenantIntegrationSettings.cs, UsersController.cs, remarkable-handlers.js, remarkable-handlers.test.js, useRemarkableApi.ts | 21.6 |
| 2 | 7/10 | UserSecretsController.cs | IntegrationCatalog.cs, IntegrationCatalogTests.cs, RemarkableController.cs, RequireTenantIntegrationAttribute.cs, ReservedUserSecretKeyTests.cs, UserSecretsController.cs, useRemarkableApi.ts | 46.8 |
| 3 | 4/10 | BriefingController.cs | 062_daily_briefing_entity_type.sql, 20260410085751_AddMorningBriefing.cs, 20260411191417_AddUserSecretsAndImageStorage.Designer.cs, BriefingAssemblyJob.cs, BriefingController.cs, ITenantIntegrationSettings.cs, UserBriefingSettingsConfiguration.cs, index.vue | 96.8 |
| 4 | 0/10 | TenantIntegrationSettings.cs | 20250928121742_InitialCreateWithStateManagement.cs, 20251008201252_AddPredicateTypeConstraints.Designer.cs, 20251013070226_AddCurrentStateToEntity.Designer.cs, 2026-06-28-integration-catalog-and-remarkable-tenant-switch-design.md, 20260218124709_AddDefaultAreaPathToConnection.Designer.cs, 20260422082245_AddShadowAndPatternLibraryRepoClassifications.Designer.cs, AnthropicComprehensionClient.cs, AzureAiComprehensionClient.cs, AzureCompletionService.cs, AzureOpenAIEmbeddingService.cs, AzureVisionService.cs, ComprehensionAiClientFactory.cs, DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs, OllamaComprehensionClient.cs, OllamaEmbeddingService.cs, Program.cs, metadata_catalog_design.md | 125.5 |
| 5 | 1/10 | MigrationRunner.cs | 20250928121742_InitialCreateWithStateManagement.cs, AiAnalysisStrategy.cs, CLAUDE.md, MigrationRunner.cs, MigrationRunnerTests.cs, Program.cs, README.md, RUNBOOK-generic.md, SeedDataRegressionTests.cs, SqlFileExecutor.cs, VENDOR-BUNDLE-IMPROVEMENTS.md, application-modes.md, database.tf, technical-decisions-template.md, testing-checklist-template.md | 177.3 |
| 6 | 5/10 | FeatureProfileService.cs | FeatureAuthorizeAttribute.cs, FeatureProfileService.cs, FeatureProfilesController.cs, IFeatureProfileService.cs, feature-profiles.vue, featureProfile.ts, profile.ts, useFeatureProfile.ts | 226.0 |
| 7 | 4/10 | MemoryVaultService.cs | 2026-04-20-team-memory-vaults-spec.md, 20260314160628_AddPersonalRepositoryFields.cs, ENTRA-SETUP.md, Entity.cs, IMemoryVaultService.cs, MemoryController.cs, MemoryVaultService.cs, VaultPreservationTests.cs, memory-handlers.js, memory-vault-post-epic-a.puml, user-memory-vault.md | 289.6 |
| 8 | 1/10 | integrations.ts | 003_entity_types.sql, AdminIntegrationsController.cs, RequireTenantIntegrationAttribute.cs, TenantIntegrationSettings.cs, integrations.ts, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.js, remarkable-status.js | 368.8 |
| 9 | 4/10 | remarkable-handlers.js | CHANGELOG.md, IntegrationCatalog.cs, RequireTenantIntegrationAttribute.cs, feature-flags.js, feature.ts, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.js, remarkable-search.js, remarkable-status.js, remarkable-status.test.js, remarkable.js, remarkable.vue, useRemarkableApi.ts | 512.0 |
| 10 | 0/10 | AuthService.cs | AuthController.cs, EntraAuthController.cs, EntraOidcService.cs, claude_guidelines.md | 167.5 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
