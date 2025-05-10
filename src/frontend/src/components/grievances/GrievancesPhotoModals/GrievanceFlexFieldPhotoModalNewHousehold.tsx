import { Box } from '@mui/material';
import {
  AllEditHouseholdFieldsQuery,
  AllEditPeopleFieldsQuery,
  useHouseholdFlexFieldsQuery,
} from '@generated/graphql';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';

export interface GrievanceFlexFieldPhotoModalNewHouseholdProps {
  flexField:
    | AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'][number]
    | AllEditPeopleFieldsQuery['allEditPeopleFieldsAttributes'][number];
  householdId: string;
}

export function GrievanceFlexFieldPhotoModalNewHousehold({
  flexField,
  householdId,
}: GrievanceFlexFieldPhotoModalNewHouseholdProps): ReactElement {
  const { data } = useHouseholdFlexFieldsQuery({
    variables: { id: householdId },
    fetchPolicy: 'network-only',
  });
  if (!data) {
    return null;
  }

  const { flexFields } = data.household;

  const picUrl: string = flexFields[flexField.name];

  return (
    <Box style={{ height: '100%' }} display="flex" alignItems="center">
      {picUrl ? (
        <PhotoModal src={picUrl} />
      ) : (
        <Box style={{ height: '100%' }} display="flex" alignItems="center">
          -
        </Box>
      )}
    </Box>
  );
}
