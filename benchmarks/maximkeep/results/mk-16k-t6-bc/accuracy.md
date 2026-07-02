# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-28
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 10
max_turns: 6
num_ctx: `16384`

- label: `mk-16k-t6-bc`
- endpoint: `http://192.168.0.22:11434/v1`
- model: `fc-q4-nothink-16k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 43/100** (6 attempt(s) timed out, counted as misses)

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 5/10 | RequireTenantIntegrationAttribute.cs | FeatureAuthorizeAttribute.cs, PulseController.cs, RelationshipsController.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.js, remarkable-list.test.js, remarkable-status.js, remarkable-status.test.js, useRemarkableApi.ts | 31.4 |
| 2 | 5/10 | UserSecretsController.cs | CHANGELOG.md, IntegrationCatalog.cs, RemarkableController.cs, ReservedUserSecretKeyTests.cs, UserSecretsController.cs, http-bridge.js, index.js, useRemarkableApi.ts | 66.9 |
| 3 | 3/10 | BriefingController.cs | 047_consolidate_predicates.sql, 20260410085751_AddMorningBriefing.cs, AzureOpenAIEmbeddingService.cs, BriefingAssemblyJob.cs, BriefingController.cs, ExternalIntegration.cs, ITenantIntegrationSettings.cs, TenantIntegrationSettings.cs, UserBriefingSettingsConfiguration.cs, ai-settings.vue, index.vue, useBriefingApi.ts, usePulseSettings.ts | 131.9 |
| 4 | 0/10 | TenantIntegrationSettings.cs | AzureCompletionService.cs, AzureOpenAIEmbeddingService.cs, AzureVisionService.cs, DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs | 145.2 |
| 5 | 5/10 | MigrationRunner.cs | ApplicationMode.cs, CLAUDE.md, CodebaseScanner.cs, IMigrationRunner.cs, MISSING_MULTI_APPLICATION_SUPPORT.md, MigrationRunner.cs, Program.cs, QWEN.md, application-modes.md, bundle-compose.bats, bundle-rotate-token.bats, check-migrations.sh | 191.6 |
| 6 | 9/10 | FeatureProfileService.cs | FeatureAuthorizeAttribute.cs, FeatureProfileService.cs, FeatureProfilesController.cs, IFeatureProfileService.cs, featureProfile.ts, profile.ts, useFeatureProfile.ts | 234.0 |
| 7 | 8/10 | MemoryVaultService.cs | 057_memory_entity_types.sql, 058_memory_relationship_predicates.sql, 2026-04-20-team-memory-vaults-spec.md, IJitProvisioningService.cs, IMemoryVaultService.cs, MemoryController.cs, MemoryVaultService.cs, Program.cs, index.js, memory-handlers.js, user-memory-vault.md | 282.2 |
| 8 | 3/10 | integrations.ts | integrations.ts, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.js, remarkable-status.js | 374.0 |
| 9 | 3/10 | remarkable-handlers.js | CHANGELOG.md, Program.cs, RequireTenantIntegrationAttribute.cs, feature-flags.js, index.js, mcp-setup.vue, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.js, remarkable-list.test.js, remarkable-status.js, remarkable-status.test.js, useRemarkableApi.ts | 542.7 |
| 10 | 2/10 | AuthService.cs | AuthController.cs, AuthModeService.cs, AuthService.cs, ClaimsPrincipalExtensions.cs, EntraAuthController.cs, EntraOidcService.cs, EntraStateCookie.cs | 470.5 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
