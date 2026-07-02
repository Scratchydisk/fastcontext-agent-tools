# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-28
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 3
max_turns: 6
num_ctx: `49152`

- label: `mk-48k-t6-600`
- endpoint: `http://192.168.0.4:11434/v1`
- model: `fc-q4-nothink-48k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 11/30** (1 attempt(s) timed out, counted as misses)

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 3/3 | RequireTenantIntegrationAttribute.cs | RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.js, useRemarkableApi.ts | 8.0 |
| 2 | 1/3 | UserSecretsController.cs | ReservedUserSecretKeyTests.cs, UserSecretsController.cs, http-bridge.js | 20.3 |
| 3 | 2/3 | BriefingController.cs | 062_daily_briefing_entity_type.sql, 20260410085751_AddMorningBriefing.cs, BriefingAssemblyJob.cs, BriefingController.cs | 35.3 |
| 4 | 0/3 | TenantIntegrationSettings.cs | AzureCompletionService.cs, AzureOpenAIEmbeddingService.cs, AzureVisionService.cs, DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs, OllamaEmbeddingService.cs, Program.cs, SystemConfigurationEntityConfiguration.cs | 47.0 |
| 5 | 1/3 | MigrationRunner.cs | ApplicationMode.cs, MigrationRunner.cs, Program.cs | 39.3 |
| 6 | 2/3 | FeatureProfileService.cs | FeatureAuthorizeAttribute.cs, FeatureProfileService.cs, FeatureProfilesController.cs, IFeatureProfileService.cs, featureProfile.ts, profile.ts | 71.0 |
| 7 | 0/3 | MemoryVaultService.cs | 2026-04-20-memory-retrieval-first-slice-spec.md, 2026-04-20-team-memory-vaults-spec.md, BriefingAssemblyJob.cs, IMemoryVaultService.cs, JitProvisioningService.cs, user-memory-vault.md | 86.0 |
| 8 | 0/3 | integrations.ts | 2026-06-28-integration-catalog-remarkable-tenant-switch.md, index.vue, remarkable-status.js, settings.vue | 106.0 |
| 9 | 0/3 | remarkable-handlers.js | CHANGELOG.md, RequireTenantIntegrationAttribute.cs, remarkable-handlers.test.js, remarkable-list.js, remarkable-status.js, remarkable.js, useRemarkableApi.ts | 126.0 |
| 10 | 2/3 | AuthService.cs | AuthController.cs, AuthService.cs, EntraAuthController.cs, login.vue | 141.0 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
