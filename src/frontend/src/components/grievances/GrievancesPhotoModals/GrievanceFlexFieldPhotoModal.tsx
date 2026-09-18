import { Box } from '@mui/material';
import { useParams } from 'react-router-dom';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import type { ReactElement } from 'react';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/index';
import { restQueryKey } from '@utils/queryKeys';
import type { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { useQuery } from '@tanstack/react-query';

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

  // individualData is camelized by the REST client, householdData is not
  const ticketData = isIndividual
    ? data.ticketDetails?.individualData
    : data.ticketDetails?.householdData;
  const flexFields = isIndividual
    ? ticketData?.flexFields
    : ticketData?.flex_fields;
  // core IMAGE fields (photo, consent_sign) sit next to flex_fields, not inside them
  const change = flexFields?.[field.name] ?? ticketData?.[field.name];

  const previousValue = isIndividual
    ? change?.previousValue
    : change?.previous_value;
  const picUrl: string = isCurrent ? previousValue : change?.value;
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
