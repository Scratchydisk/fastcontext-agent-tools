# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-28
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 3
max_turns: 6
num_ctx: `16384`

- label: `mk-16k-t6`
- endpoint: `http://192.168.0.4:11434/v1`
- model: `fc-q4-nothink-16k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 8/30**

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 1/3 | RequireTenantIntegrationAttribute.cs | AssignmentsController.cs, AuthController.cs, BrandingController.cs, ExportController.cs, FeatureProfilesController.cs, McpController.cs, PulseController.cs, RelationshipsController.cs, RepositoriesController.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, useRemarkableApi.ts | 10.7 |
| 2 | 2/3 | UserSecretsController.cs | CHANGELOG.md, IntegrationCatalog.cs, UserSecretsController.cs, http-bridge.js, useUserSecretsApi.ts | 23.3 |
| 3 | 1/3 | BriefingController.cs | BriefingAssemblyJob.cs, BriefingController.cs, index.vue | 34.0 |
| 4 | 0/3 | TenantIntegrationSettings.cs | 20250928121742_InitialCreateWithStateManagement.cs, DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs, ITenantIntegrationSettings.cs, Program.cs, RequireTenantIntegrationAttribute.cs, SystemConfigurationEntityConfiguration.cs | 45.0 |
| 5 | 0/3 | MigrationRunner.cs | 20260322093723_AddWorkSessionTables.cs, ApplicationMode.cs, CLAUDE.md, Program.cs, application-modes.md, check-migrations.sh | 56.3 |
| 6 | 1/3 | FeatureProfileService.cs | 20260422084024_AddComprehensionJobTable.Designer.cs, FeatureAuthorizeAttribute.cs, FeatureProfileService.cs, FeatureProfilesController.cs, IFeatureProfileService.cs, Program.cs, featureProfile.ts, profile.ts, useFeatureProfile.ts | 68.0 |
| 7 | 2/3 | MemoryVaultService.cs | 2026-04-20-team-memory-vaults-spec.md, IMemoryVaultService.cs, MemoryVaultService.cs, memory-vault-post-epic-a.puml, user-memory-vault.md | 89.7 |
| 8 | 1/3 | integrations.ts | TenantIntegrationSettings.cs, integrations.ts, remarkable-handlers.js, remarkable-list.js, remarkable-status.js | 124.3 |
| 9 | 0/3 | remarkable-handlers.js | CHANGELOG.md, RemarkableController.cs, RequireTenantIntegrationAttribute.cs, feature.ts, remarkable-list.js, remarkable-status.js, remarkable.js, useRemarkableApi.ts | 161.3 |
| 10 | 0/3 | AuthService.cs | EntraAuthController.cs, auth.ts | 179.0 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
