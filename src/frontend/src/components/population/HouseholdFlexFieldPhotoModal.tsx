import { Box } from '@mui/material';
import { useParams } from 'react-router-dom';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';

export function HouseholdFlexFieldPhotoModal({ field }): ReactElement {
  const { id } = useParams();
  const { businessArea, programId } = useBaseUrl();
  const { selectedProgram } = useProgramContext();

  const { data } = useQuery<HouseholdDetail>({
    queryKey: ['household', businessArea, id, programId, selectedProgram?.code],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsRetrieve({
        businessAreaSlug: businessArea,
        id: id,
        programCode: programId || selectedProgram?.code || '',
      }),
    enabled: !!businessArea && !!id && (!!programId || !!selectedProgram?.code),
  });

  if (!data) {
    return null;
  }

  const { flexFields } = data;
  const picUrl = flexFields[field.name];

  return picUrl ? (
    <PhotoModal src={picUrl} />
  ) : (
    <Box display="flex" alignItems="center">
      -
    </Box>
  );
}
