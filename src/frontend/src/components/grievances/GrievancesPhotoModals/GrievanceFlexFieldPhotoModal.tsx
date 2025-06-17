import { Box } from '@mui/material';
import { useParams } from 'react-router-dom';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';ox } from '@mui/material';
import { useParams } from 'react-router-dom';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';rt { Box } from '@mui/material';
import { useParams } from 'react-router-dom';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';

export interface GrievanceFlexFieldPhotoModalProps {
  field: {
    name?: string;
    [key: string]: any;
  };
  isCurrent?: boolean;
  isIndividual?: boolean;
}

export function GrievanceFlexFieldPhotoModal({
  field,
  isCurrent,
  isIndividual,
}: GrievanceFlexFieldPhotoModalProps): ReactElement {
  const { id } = useParams();
  const { data } = useGrievanceTicketFlexFieldsQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });
  if (!data) {
    return null;
  }

  const flexFields = isIndividual
    ? data.grievanceTicket?.individualDataUpdateTicketDetails?.individualData
        ?.flexFields
    : data.grievanceTicket?.householdDataUpdateTicketDetails?.householdData
        ?.flexFields;

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
