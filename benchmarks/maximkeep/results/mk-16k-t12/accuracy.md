# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-28
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 3
max_turns: 12
num_ctx: `16384`

- label: `mk-16k-t12`
- endpoint: `http://192.168.0.4:11434/v1`
- model: `fc-q4-nothink-16k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 12/30**

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 2/3 | RequireTenantIntegrationAttribute.cs | FeatureAuthorizeAttribute.cs, IntegrationsController.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js | 12.0 |
| 2 | 2/3 | UserSecretsController.cs | RemarkableController.cs, ReservedUserSecretKeyTests.cs, UserSecretsController.cs | 24.0 |
| 3 | 1/3 | BriefingController.cs | 062_daily_briefing_entity_type.sql, BriefingAssemblyJob.cs, BriefingController.cs, usePulseSettings.ts | 38.0 |
| 4 | 0/3 | TenantIntegrationSettings.cs | 20250928121742_InitialCreateWithStateManagement.cs, AnthropicComprehensionClient.cs, BriefingAssemblyService.cs, ITenantIntegrationSettings.cs, OllamaVisionService.cs, Program.cs, RagPipelineService.cs, architecture.md, architecture.vue, metadata_catalog_design.md, uat-docker.md | 48.0 |
| 5 | 1/3 | MigrationRunner.cs | ApplicationMode.cs, MigrationRunner.cs, Program.cs, SqlFileExecutor.cs | 71.7 |
| 6 | 1/3 | FeatureProfileService.cs | FeatureAuthorizeAttribute.cs, FeatureProfileService.cs, FeatureProfilesController.cs, IFeatureProfileService.cs, Program.cs, featureProfile.ts, profile.ts, useFeatureProfile.ts | 89.0 |
| 7 | 2/3 | MemoryVaultService.cs | MemoryVaultService.cs, QWEN.md, user-memory-vault.md | 103.7 |
| 8 | 1/3 | integrations.ts | 2026-06-28-integration-catalog-remarkable-tenant-switch.md, TenantIntegrationSettings.cs, index.vue, integrations.ts | 147.0 |
| 9 | 1/3 | remarkable-handlers.js | CHANGELOG.md, ITenantIntegrationSettings.cs, IntegrationCatalog.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js, useRemarkableApi.ts | 202.3 |
| 10 | 1/3 | AuthService.cs | AuthService.cs, EntraOidcService.cs | 237.3 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
