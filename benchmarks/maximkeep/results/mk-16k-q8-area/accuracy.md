# Maxim Keep — exact vs area (right-neighbourhood) hit

Run: 2026-06-29
Model: fc-q8-nothink-16k:latest  iters: 10  max_turns: 6
area-hit = a citation is in the SAME DIRECTORY as the ground-truth file.

**Exact-hit: 39/100**
**Area-hit: 51/100**

| # | truth | truth dirs | exact | area |
|---|---|---|---|---|
| 1 | RequireTenantIntegrationAttribute.cs | 1 | 7/10 | 8/10 |
| 2 | UserSecretsController.cs | 1 | 7/10 | 7/10 |
| 3 | BriefingController.cs | 1 | 1/10 | 1/10 |
| 4 | TenantIntegrationSettings.cs | 1 | 0/10 | 2/10 |
| 5 | MigrationRunner.cs | 1 | 5/10 | 5/10 |
| 6 | FeatureProfileService.cs | 1 | 6/10 | 6/10 |
| 7 | MemoryVaultService.cs | 1 | 5/10 | 5/10 |
| 8 | integrations.ts | 1 | 2/10 | 4/10 |
| 9 | remarkable-handlers.js | 1 | 1/10 | 8/10 |
| 10 | AuthService.cs | 1 | 5/10 | 5/10 |
