# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-28
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 3
max_turns: 6
num_ctx: `32768`

- label: `mk-32k-t6-600`
- endpoint: `http://192.168.0.4:11434/v1`
- model: `fc-q4-nothink-32k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 8/30**

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 2/3 | RequireTenantIntegrationAttribute.cs | FeatureAuthorizeAttribute.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js, useRemarkableApi.ts | 8.0 |
| 2 | 2/3 | UserSecretsController.cs | CHANGELOG.md, IntegrationCatalogTests.cs, RemarkableController.cs, ReservedUserSecretKeyTests.cs, UserSecretsController.cs, index.js, useRemarkableApi.ts, useUserSecretsApi.ts | 20.0 |
| 3 | 0/3 | BriefingController.cs | 062_daily_briefing_entity_type.sql, BriefingAssemblyJob.cs, ITenantIntegrationSettings.cs, TenantIntegrationSettings.cs, ai-settings.vue, index.vue | 31.0 |
| 4 | 0/3 | TenantIntegrationSettings.cs | 2026-06-28-integration-catalog-and-remarkable-tenant-switch-design.md, SettingsController.cs | 43.0 |
| 5 | 2/3 | MigrationRunner.cs | ApplicationMode.cs, MigrationRunner.cs, Program.cs | 55.7 |
| 6 | 1/3 | FeatureProfileService.cs | FeatureAuthorizeAttribute.cs, FeatureProfileService.cs, FeatureProfilesController.cs, IFeatureProfileService.cs, featureProfile.ts, useFeatureProfile.ts | 68.0 |
| 7 | 1/3 | MemoryVaultService.cs | 2026-04-20-team-memory-vaults-spec.md, 20260422082245_AddShadowAndPatternLibraryRepoClassifications.Designer.cs, Entity.cs, IMemoryVaultService.cs, MemoryVaultService.cs, user-memory-vault.md | 80.0 |
| 8 | 0/3 | integrations.ts | RequireTenantIntegrationAttribute.cs, inclusion-rules.spec.ts, predicate-visibility.spec.ts, remarkable-handlers.js, remarkable-list.js, remarkable-status.js | 113.0 |
| 9 | 0/3 | remarkable-handlers.js | CHANGELOG.md, RequireTenantIntegrationAttribute.cs, useRemarkableApi.ts | 132.3 |
| 10 | 0/3 | AuthService.cs | AuthAdminControllerTests.cs, AuthServiceTests.cs, EntraAuthController.cs, EntraOidcService.cs, auth.ts, index.js | 149.0 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
