import type { QueryKey } from '@tanstack/react-query';

// A RestService fetcher. Only its `.name` is used.
type RestMethod = (...args: any[]) => unknown;

// restBusinessAreasProgramsList -> 'businessAreasProgramsList'
function normalizeRoot(name: string): string {
  const stripped = name.startsWith('rest') ? name.slice('rest'.length) : name;
  return stripped.charAt(0).toLowerCase() + stripped.slice(1);
}

// Derives the key from the fetcher's identity so readers and invalidators cannot drift.
//   restQueryKey(method)         -> [root]          // invalidators: matches every variant
//   restQueryKey(method, params) -> [root, params]  // readers
export function restQueryKey(
  method: RestMethod,
  params?: Record<string, unknown>,
): QueryKey {
  const root = normalizeRoot(method.name);
  return params === undefined ? [root] : [root, params];
}
