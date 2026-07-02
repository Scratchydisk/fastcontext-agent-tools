# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-29
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 10
max_turns: 6
num_ctx: `65536`

- label: `mk-64k-f16-t6`
- endpoint: `http://192.168.0.248:11434/v1`
- model: `fc-f16-nothink-64k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 44/100** (6 attempt(s) timed out, counted as misses)

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 8/10 | RequireTenantIntegrationAttribute.cs | FeatureAuthorizeAttribute.cs, Program.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js, remarkable-handlers.test.js, useRemarkableApi.ts | 20.6 |
| 2 | 8/10 | UserSecretsController.cs | IntegrationCatalog.cs, MetadataController.cs, RemarkableController.cs, ReservedUserSecretKeyTests.cs, UserSecretsController.cs, UsersController.cs, remarkable-handlers.test.js, tagged_block_common.py, useRemarkableApi.ts | 43.0 |
| 3 | 2/10 | BriefingController.cs | 062_daily_briefing_entity_type.sql, 20260410085751_AddMorningBriefing.Designer.cs, 20260410085751_AddMorningBriefing.cs, BriefingAssemblyJob.cs, BriefingController.cs, UserBriefingSettingsConfiguration.cs | 64.7 |
| 4 | 1/10 | TenantIntegrationSettings.cs | DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs, Program.cs, SystemConfigurationEntityConfiguration.cs, TenantIntegrationSettings.cs | 89.0 |
| 5 | 4/10 | MigrationRunner.cs | ApplicationMode.cs, BrandingOptions.cs, MigrationRunner.cs, Program.cs, SqlFileExecutor.cs, application-modes.md | 129.6 |
| 6 | 6/10 | FeatureProfileService.cs | 20260218124709_AddDefaultAreaPathToConnection.Designer.cs, FeatureAuthorizeAttribute.cs, FeatureProfile.cs, FeatureProfileConfiguration.cs, FeatureProfileService.cs, IFeatureProfileService.cs, UserFeatureProfile.cs, UserFeatureProfileConfiguration.cs, featureProfile.ts, profile.ts, useFeatureProfile.ts | 153.6 |
| 7 | 4/10 | MemoryVaultService.cs | 057_memory_entity_types.sql, 2026-04-20-team-memory-vaults-spec.md, CreateEntityHandler.cs, EntityTypeNames.cs, IJitProvisioningService.cs, IMemoryVaultService.cs, JitProvisioningService.cs, MemoryVaultService.cs, Program.cs, index.js, memory-handlers.js, user-memory-vault.md | 159.1 |
| 8 | 5/10 | integrations.ts | exclusion-rules.ts, feature-flags.js, inclusion-rules.spec.ts, inclusion-rules.ts, integrations-store.spec.ts, integrations.ts, predicate-visibility.spec.ts, predicate-visibility.ts, useEntityFilter.ts | 268.4 |
| 9 | 2/10 | remarkable-handlers.js | ExternalIntegration.cs, feature-flags.js, index.js, remarkable-handlers.js, remarkable-list.js, remarkable-status.js, remarkable.js | 324.2 |
| 10 | 4/10 | AuthService.cs | AuthAdminController.cs, AuthController.cs, AuthService.cs, ClaimsPrincipalExtensions.cs, EntraAuthController.cs, EntraOidcService.cs, EntraStateCookie.cs, Program.cs, auth.ts | 350.8 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
