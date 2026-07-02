# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-29
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 10
max_turns: 6
num_ctx: `131072`

- label: `mk-128k-t6-bc`
- endpoint: `http://192.168.0.22:11434/v1`
- model: `fc-q4-nothink-128k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 37/100** (4 attempt(s) timed out, counted as misses)

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 8/10 | RequireTenantIntegrationAttribute.cs | CHANGELOG.md, FeatureAuthorizeAttribute.cs, FeatureProfilesController.cs, McpController.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.test.js, remarkable-status.test.js, useRemarkableApi.ts | 35.4 |
| 2 | 6/10 | UserSecretsController.cs | CHANGELOG.md, IntegrationCatalog.cs, RequireTenantIntegrationAttribute.cs, ReservedUserSecretKeyTests.cs, UserSecretsController.cs, http-bridge.js, remarkable.vue, useRemarkableApi.ts, useUserSecretsApi.ts | 81.0 |
| 3 | 1/10 | BriefingController.cs | 039_service_capability_framework.sql, 044_feature_profiles.sql, 062_daily_briefing_entity_type.sql, 063_default_briefing_sources.sql, 20260409173818_AddTemporalRelationshipsAndExternalUrl.Designer.cs, 20260410085751_AddMorningBriefing.cs, 20260411191417_AddUserSecretsAndImageStorage.Designer.cs, 20260422082245_AddShadowAndPatternLibraryRepoClassifications.Designer.cs, 20260422084358_FixComprehensionJobColumnTypes.Designer.cs, 20260627131551_EntraIntegration.Designer.cs, 20260627141537_AddDataProtectionKeys.Designer.cs, BreakGlassSeeder.cs, BriefingAssemblyJob.cs, BriefingController.cs, ITenantIntegrationSettings.cs, TenantIntegrationSettings.cs, UserBriefingSettingsConfiguration.cs, useBriefingApi.ts | 127.6 |
| 4 | 0/10 | TenantIntegrationSettings.cs | 20250928121742_InitialCreateWithStateManagement.cs, 20251008201252_AddPredicateTypeConstraints.Designer.cs, 2026-06-28-integration-catalog-and-remarkable-tenant-switch-design.md, 2026-06-28-integration-catalog-remarkable-tenant-switch.md, 20260106131654_AddDocumentSourceTracking.Designer.cs, 20260216141646_AddFieldMappings.Designer.cs, 20260218124709_AddDefaultAreaPathToConnection.Designer.cs, 20260322093723_AddWorkSessionTables.Designer.cs, 20260422082245_AddShadowAndPatternLibraryRepoClassifications.Designer.cs, 20260627141537_AddDataProtectionKeys.Designer.cs, AzureCompletionService.cs, AzureOpenAIEmbeddingService.cs, AzureVisionService.cs, DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs, OllamaEmbeddingService.cs, Program.cs, SystemConfigurationEntityConfiguration.cs, metadata_catalog_design.md | 177.0 |
| 5 | 5/10 | MigrationRunner.cs | ApplicationMode.cs, IMigrationRunner.cs, MigrationRunner.cs, MigrationRunnerTests.cs, Program.cs, SeedDataRegressionTests.cs, StateQueryService.cs, application-modes.md | 194.4 |
| 6 | 7/10 | FeatureProfileService.cs | FeatureAuthorizeAttribute.cs, FeatureProfileService.cs, FeatureProfilesController.cs, IFeatureProfileService.cs, UserFeatureProfile.cs, featureProfile.ts, profile.ts, useFeatureProfile.ts | 231.0 |
| 7 | 7/10 | MemoryVaultService.cs | 2026-04-20-team-memory-vaults-spec.md, ENTRA-SETUP.md, IMemoryVaultService.cs, JitProvisioningService.cs, MemoryVaultService.cs, Program.cs, VaultPreservationTests.cs, user-memory-vault.md | 304.9 |
| 8 | 0/10 | integrations.ts | AdminIntegrationsController.cs, CHANGELOG.md, RequireTenantIntegrationAttribute.cs, TenantIntegrationSettings.cs, TenantIntegrationSettingsTests.cs, index.vue, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.js, remarkable-list.test.js, remarkable-status.js, remarkable.vue, settings.vue, useRemarkableApi.ts | 389.8 |
| 9 | 2/10 | remarkable-handlers.js | CHANGELOG.md, IntegrationCatalog.cs, RequireTenantIntegrationAttribute.cs, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.js, remarkable-status.js, useRemarkableApi.ts | 464.4 |
| 10 | 1/10 | AuthService.cs | AuthAdminController.cs, AuthController.cs, AuthService.cs, AuthServiceTests.cs, ClaimsPrincipalExtensionsTests.cs, EntraAuthController.cs, EntraOidcService.cs, api-client.js, auth.ts, complete.vue, generate_api_reference.py, index.js, login.vue, useAiApi.ts, useBriefingAdminApi.ts, useEntityInlineEdit.ts, useGuidanceApi.ts, usePulseMultiRepository.ts | 538.6 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
