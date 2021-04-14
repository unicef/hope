import { useMeQuery } from '../__generated__/graphql';
import { useBusinessArea } from './useBusinessArea';

export function usePermissions(): string[] {
  const { data, loading } = useMeQuery({
    fetchPolicy: 'cache-and-network',
  });
  const businessArea = useBusinessArea();
  if (loading) {
    return null;
  }
  // eslint-disable-next-line no-restricted-syntax
  for (const businessAreaEdge of data.me.businessAreas.edges) {
    if (businessArea === businessAreaEdge.node.slug)
      return businessAreaEdge.node.permissions;
  }
  return [];
}
