import { Box } from '@mui/material';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import type { ReactElement } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import type { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';

export interface GrievanceFlexFieldPhotoModalNewHouseholdProps {
  flexField: {
    name?: string;
    [key: string]: any;
  };
  householdId: string;
}

export function GrievanceFlexFieldPhotoModalNewHousehold({
  flexField,
  householdId,
}: GrievanceFlexFieldPhotoModalNewHouseholdProps): ReactElement {
  const { businessArea, programId } = useBaseUrl();
  const { selectedProgram } = useProgramContext();

  const householdParams = {
    businessAreaSlug: businessArea,
    id: householdId,
    programCode: programId || selectedProgram?.code || '',
  };
  const { data } = useQuery<HouseholdDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsHouseholdsRetrieve,
      householdParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsRetrieve(householdParams),
    enabled:
      !!businessArea &&
      !!householdId &&
      (!!programId || !!selectedProgram?.code),
  });
  if (!data) {
    return null;
  }

  const picUrl: string = data.flexFields?.[flexField.name];

  return (
    <Box
      style={{ height: '100%' }}
      sx={{
        display: 'flex',
        alignItems: 'center',
      }}
    >
      {picUrl ? (
        <PhotoModal src={picUrl} />
      ) : (
        <Box
          style={{ height: '100%' }}
          sx={{
            display: 'flex',
            alignItems: 'center',
          }}
        >
          -
        </Box>
      )}
    </Box>
  );
}
