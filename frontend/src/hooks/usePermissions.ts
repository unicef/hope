import { useBusinessArea } from './useBusinessArea';
import { useCachedMe } from './useCachedMe';

export function usePermissions(): string[] {
  const { data, loading } = useCachedMe();
  const businessArea = useBusinessArea();
  if (loading || !data) {
    return null;
  }
  // eslint-disable-next-line no-restricted-syntax
  for (const businessAreaEdge of data.me.businessAreas.edges) {
    if (businessArea === businessAreaEdge.node.slug)
      return businessAreaEdge.node.permissions;
  }
  return [];
}
