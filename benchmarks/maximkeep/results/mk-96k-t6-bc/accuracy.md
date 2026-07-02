# Accuracy benchmark — Maxim Keep (large repo)

Run: 2026-06-28
Target repo: `/mnt/wdblue/stewart/Projects/sasystem`
Iterations per query: 10
max_turns: 6
num_ctx: `98304`

- label: `mk-96k-t6-bc`
- endpoint: `http://192.168.0.22:11434/v1`
- model: `fc-q4-nothink-96k:latest`
- FC_MAX_TOKENS: `4000`
- FC_TEMPERATURE: `0.2`
- FASTCONTEXT_REROOT_PATHS: `1`

**File-hit rate: 37/100** (7 attempt(s) timed out, counted as misses)

| # | hits | expected | files cited (any iter) | avg tool calls |
|---|------|----------|------------------------|----------------|
| 1 | 10/10 | RequireTenantIntegrationAttribute.cs | CHANGELOG.md, FeatureAuthorizeAttribute.cs, PulseController.cs, RequireTenantIntegrationAttribute.cs, RequireTenantIntegrationAttributeTests.cs, remarkable-handlers.js, remarkable-handlers.test.js, remarkable-list.js, remarkable-list.test.js, remarkable-status.js, remarkable-status.test.js | 31.3 |
| 2 | 6/10 | UserSecretsController.cs | CHANGELOG.md, IntegrationCatalog.cs, McpController.cs, RemarkableController.cs, ReservedUserSecretKeyTests.cs, UserSecretsController.cs, index.js, useRemarkableApi.ts, useUserSecretsApi.ts | 62.8 |
| 3 | 2/10 | BriefingController.cs | 062_daily_briefing_entity_type.sql, 2026-04-10-morning-briefing.md, BriefingAssemblyJob.cs, BriefingController.cs, FeatureProfile.cs, ITenantIntegrationSettings.cs, ai-settings.vue, briefing-sources.vue, feature.ts, featureFlags.ts, index.vue, integrations-store.spec.ts, useBriefingApi.ts | 127.0 |
| 4 | 0/10 | TenantIntegrationSettings.cs | 20250928154953_MakeTaxonomyFieldsOptional.Designer.cs, 20251008201252_AddPredicateTypeConstraints.Designer.cs, 20251026124437_AddEntityTypeHierarchyAndPredicateEnhancements.Designer.cs, 20251215130854_RemoveUrnFromEntity.Designer.cs, 20251221124304_AddIsHierarchicalToPredicateDefinition.Designer.cs, 20260106131654_AddDocumentSourceTracking.Designer.cs, 20260115120338_AddUserSoftDelete.Designer.cs, 20260216141646_AddFieldMappings.Designer.cs, 20260218124709_AddDefaultAreaPathToConnection.Designer.cs, 20260322093723_AddWorkSessionTables.Designer.cs, 20260409173818_AddTemporalRelationshipsAndExternalUrl.Designer.cs, 20260410085751_AddMorningBriefing.Designer.cs, 20260418183203_AddUserEncryptionKey.Designer.cs, 20260422082245_AddShadowAndPatternLibraryRepoClassifications.Designer.cs, 20260422084024_AddComprehensionJobTable.Designer.cs, 20260627141537_AddDataProtectionKeys.Designer.cs, AnthropicComprehensionClient.cs, AzureCompletionService.cs, AzureOpenAIEmbeddingService.cs, AzureVisionService.cs, ComprehensionAiClientFactory.cs, DelegatingCompletionService.cs, DelegatingEmbeddingService.cs, DelegatingVisionService.cs, OllamaComprehensionClient.cs, OllamaEmbeddingService.cs, Program.cs, SystemConfigurationEntityConfiguration.cs, architecture.vue | 135.4 |
| 5 | 4/10 | MigrationRunner.cs | ApplicationMode.cs, BrandingOptions.cs, CodebaseScanner.cs, IMigrationRunner.cs, MigrationRunner.cs, MigrationRunnerTests.cs, Program.cs, SeedDataRegressionTests.cs, application-modes.md | 206.2 |
| 6 | 5/10 | FeatureProfileService.cs | FeatureAuthorizeAttribute.cs, FeatureProfile.cs, FeatureProfileService.cs, FeatureProfilesController.cs, IFeatureProfileService.cs, featureProfile.ts, profile.ts, useFeatureProfile.ts | 249.1 |
| 7 | 5/10 | MemoryVaultService.cs | 2026-04-20-team-memory-vaults-spec.md, 2026-06-27-entra-id-integration-design.md, Entity.cs, IMemoryVaultService.cs, MemoryController.cs, MemoryVaultService.cs, Program.cs, VaultStats.vue, memory-vault-post-epic-a.puml, scratchpad.md, user-memory-vault.md | 291.1 |
| 8 | 2/10 | integrations.ts | TenantIntegrationSettings.cs, implementation-context.js, inclusion-rules.spec.ts, index.vue, integrations-store.spec.ts, integrations.ts, predicate-visibility.spec.ts, remarkable-handlers.js, taxonomy-basic.test.js, taxonomy-integration.test.js | 327.4 |
| 9 | 2/10 | remarkable-handlers.js | CHANGELOG.md, IntegrationCatalog.cs, RequireTenantIntegrationAttribute.cs, index.js, mcp-setup.vue, remarkable-handlers.js, remarkable-list.js, remarkable-status.js, useRemarkableApi.ts | 435.4 |
| 10 | 1/10 | AuthService.cs | AuthController.cs, AuthService.cs, BrandingOptions.cs, ClaimsPrincipalExtensions.cs, ClaimsPrincipalExtensionsTests.cs, DiagramController.cs, PulseController.cs, UserSecretsController.cs, api-auth.client.ts, auth-store.spec.ts, auth.ts, claude_guidelines.md, token-expiry.spec.ts | 404.4 |

A *hit* means a returned citation pointed at the accepted ground-truth file (the file that defines/implements the behaviour). Results vary run to run (sampling); use BENCH_ITERS>1 and re-run to confirm.
