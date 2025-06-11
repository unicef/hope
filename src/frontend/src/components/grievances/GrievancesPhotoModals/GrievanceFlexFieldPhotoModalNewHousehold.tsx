import { Box } from '@mui/material';
import {
  AllEditHouseholdFieldsQuery,
  AllEditPeopleFieldsQuery,
} from '@generated/graphql';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';

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
  const { businessArea, programId } = useBaseUrl();
  const { selectedProgram } = useProgramContext();

  const { data } = useQuery<HouseholdDetail>({
    queryKey: [
      'household',
      businessArea,
      householdId,
      programId,
      selectedProgram?.slug,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsRetrieve({
        businessAreaSlug: businessArea,
        id: householdId,
        programSlug: programId || selectedProgram?.slug || '',
      }),
    enabled:
      !!businessArea &&
      !!householdId &&
      (!!programId || !!selectedProgram?.slug),
  });
  if (!data) {
    return null;
  }

  const picUrl: string = data.flexFields?.[flexField.name];

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
