import { useCachedMe } from './useCachedMe';

export function usePermissions(): string[] {
  const { data, loading } = useCachedMe();
  if (loading || !data) {
    return [];
  }
  return data.me.permissionsInScope || [];
}
