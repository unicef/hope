import type { QueryKey } from '@tanstack/react-query';

// A RestService fetcher: a named static method taking one object arg (or none).
// We rely only on its `.name`.
type RestMethod = (...args: any[]) => unknown;

// Normalizes a RestService method name to the app's query-key root convention:
// drop the generated `rest` prefix and lower-case the first char. This reproduces the
// existing hand-written list prefixes exactly (restBusinessAreasProgramsList ->
// 'businessAreasProgramsList'), so derived keys match existing readers.
function normalizeRoot(name: string): string {
  const stripped = name.startsWith('rest') ? name.slice('rest'.length) : name;
  return stripped.charAt(0).toLowerCase() + stripped.slice(1);
}

// Derives a stable query key from a RestService method's identity, so keys are never
// hand-written and cannot drift from their reader/invalidator counterpart.
//   restQueryKey(method)         -> [root]          // list prefix / invalidation
//   restQueryKey(method, params) -> [root, params]  // detail / scoped reader
// List readers pass their pagination/filter object as `params`; their invalidators pass
// none, so the bare prefix matches every cached variant (default non-exact match).
export function restQueryKey(
  method: RestMethod,
  params?: Record<string, unknown>,
): QueryKey {
  const root = normalizeRoot(method.name);
  return params === undefined ? [root] : [root, params];
}
