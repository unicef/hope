import { Box } from '@mui/material';
import { useParams } from 'react-router-dom';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

export function IndividualFlexFieldPhotoModal({ field }): ReactElement {
  const { id } = useParams();
  const { businessArea, programId } = useBaseUrl();

  const { data } = useQuery<IndividualDetail>({
    queryKey: ['individual', businessArea, programId, id],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id: id,
      }),
    enabled: !!businessArea && !!programId && !!id,
  });

  if (!data) {
    return null;
  }

  const picUrl = data.flexFields?.[field.name];

  return picUrl ? (
    <PhotoModal src={picUrl} />
  ) : (
    <Box style={{ height: '100%' }} display="flex" alignItems="center">
      -
    </Box>
  );
}
