// Exempts static reference data (choices, geo areas, permissions) from the blanket
// post-mutation invalidation in providers.tsx, so it keeps its long staleTime. Query
// keys are derived from the fetcher via restQueryKey (see utils/queryKeys.ts).
const STATIC_QUERY_KEY_ROOTS = new Set<string>([
  'profile', // permissions / current-user profile (usePermissions, AppBar)
  'businessArea', // business-area details
  'allAreasTree', // geo areas
  'beneficiaryGroups',
  // restChoicesCountriesList / any *choices* root is covered by the heuristic below.
]);

/** True when a query holds static reference data that user mutations never change. */
export function isStaticReferenceQuery(queryKey: readonly unknown[]): boolean {
  const root = queryKey[0];
  // Only string roots can be static; list keys with an object first element are data.
  if (typeof root !== 'string') return false;
  // Exact match only — never a prefix, since many data keys start with `businessArea…`.
  if (STATIC_QUERY_KEY_ROOTS.has(root)) return true;
  // Every choices endpoint is reference data (e.g. programChoices, choicesPaymentPlanStatusList).
  return root.toLowerCase().includes('choices');
}
