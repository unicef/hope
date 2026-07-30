// Roots exempt from the blanket post-mutation invalidation in providers.tsx, so reference
// data keeps its long staleTime. These are restQueryKey roots (see utils/queryKeys.ts) and
// must be updated alongside their readers — a stale root here silently stops matching.
// Any *choices* root is covered by the heuristic below.
const STATIC_QUERY_KEY_ROOTS = new Set<string>([
  'businessAreasUsersProfileRetrieve',
  'businessAreasRetrieve',
  'businessAreasGeoAreasList',
  'beneficiaryGroupsList',
]);

/** True when a query holds static reference data that user mutations never change. */
export function isStaticReferenceQuery(queryKey: readonly unknown[]): boolean {
  const root = queryKey[0];
  if (typeof root !== 'string') return false;
  // Exact match only — never a prefix, since many data keys start with `businessArea…`.
  if (STATIC_QUERY_KEY_ROOTS.has(root)) return true;
  return root.toLowerCase().includes('choices');
}
