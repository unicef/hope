// import { RestService } from '@restgenerated/services/RestService';
// import { useQuery } from '@tanstack/react-query';
import { useCachedMe } from './useCachedMe';

export function usePermissions(): string[] {
  //TODO: uncomment this
  // const { data: meData, isLoading: meDataLoading } = useQuery({
  //   queryKey: ['profile'],
  //   queryFn: () => {
  //     return RestService.restProfileRetrieve();
  //   },
  // });

  const { data, loading } = useCachedMe();
  if (loading || !data) {
    return [];
  }
  return data.me.permissionsInScope || [];
}
