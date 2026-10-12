import { Box } from '@mui/material';
import { useParams } from 'react-router-dom';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import type { ReactElement } from 'react';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/index';
import { restQueryKey } from '@utils/queryKeys';
import type { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { useQuery } from '@tanstack/react-query';
import {
  getTicketFieldChange,
  normalizeTicketFieldChange,
} from '../utils/ticketData';

export interface GrievanceFlexFieldPhotoModalProps {
  field;
  isCurrent?: boolean;
  isIndividual?: boolean;
}

export function GrievanceFlexFieldPhotoModal({
  field,
  isCurrent,
  isIndividual,
}: GrievanceFlexFieldPhotoModalProps): ReactElement {
  const { id } = useParams();
  const { businessAreaSlug } = useBaseUrl();

  const { data } = useQuery<GrievanceTicketDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasGrievanceTicketsRetrieve,
      { businessAreaSlug, id },
    ),
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsRetrieve({
        businessAreaSlug,
        id: id,
      }),
  });

  if (!data) {
    return null;
  }

  const { value, previousValue } = normalizeTicketFieldChange(
    getTicketFieldChange(data.ticketDetails, field.name, isIndividual),
    isIndividual,
  );
  const picUrl: string = isCurrent ? previousValue : value;
  return picUrl ? (
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
  );
}
