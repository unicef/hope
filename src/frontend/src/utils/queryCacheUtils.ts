// Query keys in this app are hand-written string-array literals (not derived from
// restgenerated), so they drift. The global MutationCache.onSuccess in providers.tsx
// invalidates every query after any successful mutation to keep the UI fresh, but static
// reference data (choices, geo areas, permissions) is never changed by those mutations and
// carries a deliberately long staleTime. This predicate exempts that data from the blanket
// invalidation so it is not needlessly refetched after every write.
const STATIC_QUERY_KEY_ROOTS = new Set<string>([
  'profile', // permissions / current-user profile (usePermissions, AppBar)
  'businessArea', // business-area details
  'allAreasTree', // geo areas
  'beneficiaryGroups',
  'restChoicesCountriesList',
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
