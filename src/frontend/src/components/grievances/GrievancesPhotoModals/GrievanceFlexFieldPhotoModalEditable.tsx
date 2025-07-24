import { Box } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useParams } from 'react-router-dom';
import { FormikFileField } from '@shared/Formik/FormikFileField';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import PhotoModal from '@core/PhotoModal/PhotoModal';

export interface GrievanceFlexFieldPhotoModalEditableProps {
  flexField: any;
  isCurrent?: boolean;
  isIndividual?: boolean;
  field;
  form;
}

export function GrievanceFlexFieldPhotoModalEditable({
  isCurrent,
  isIndividual,
  field,
  form,
  flexField,
}: GrievanceFlexFieldPhotoModalEditableProps): ReactElement {
  const [isEdited, setEdit] = useState(false);
  const { id } = useParams();
  const { businessArea } = useBaseUrl();

  const { data } = useQuery({
    queryKey: ['grievanceTicket', id, businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsRetrieve({
        businessAreaSlug: businessArea,
        id,
      }),
    enabled: !!id,
  });

  if (!data) {
    return null;
  }

  const flexFields = isIndividual
    ? data.ticketDetails?.individualDataUpdateTicketDetails?.individualData
        ?.flexFields
    : data.ticketDetails?.householdDataUpdateTicketDetails?.householdData
        ?.flexFields;

  const picUrl: string = isCurrent
    ? flexFields[flexField.name]?.previous_value
    : flexFields[flexField.name]?.value;

  return (
    <Box style={{ height: '100%' }} display="flex" alignItems="center">
      {isEdited || !picUrl ? (
        <Box style={{ height: '100%' }} display="flex" alignItems="center">
          <FormikFileField field={field} form={form} />
        </Box>
      ) : (
        <PhotoModal
          src={picUrl}
          variant="pictureClose"
          closeHandler={() => setEdit(true)}
        />
      )}
    </Box>
  );
}
