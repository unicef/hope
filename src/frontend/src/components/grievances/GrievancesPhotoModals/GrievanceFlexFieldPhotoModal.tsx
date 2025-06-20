import { Box } from '@mui/material';
import { useParams } from 'react-router-dom';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/index';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
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
    queryKey: ['businessAreasGrievanceTicketsRetrieve', businessAreaSlug, id],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsRetrieve({
        businessAreaSlug,
        id: id,
      }),
  });

  if (!data) {
    return null;
  }

  const flexFields = isIndividual
    ? data?.ticketDetails?.individualData?.flex_fields
    : data.ticketDetails?.householdDataUpdateTicketDetails?.householdData
        ?.flex_fields;

  const picUrl: string = isCurrent
    ? flexFields[field.name]?.previous_value
    : flexFields[field.name]?.value;
  return picUrl ? (
    <PhotoModal src={picUrl} />
  ) : (
    <Box style={{ height: '100%' }} display="flex" alignItems="center">
      -
    </Box>
  );
}
