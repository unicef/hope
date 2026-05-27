import { Box } from '@mui/material';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';

export interface GrievanceFlexFieldPhotoModalNewIndividualProps {
  flexField: {
    name?: string;
    [key: string]: any;
  };
  individualId: string;
}

export function GrievanceFlexFieldPhotoModalNewIndividual({
  flexField,
  individualId,
}: GrievanceFlexFieldPhotoModalNewIndividualProps): ReactElement {
  const { businessArea, programId } = useBaseUrl();
  const { selectedProgram } = useProgramContext();

  const { data } = useQuery<IndividualDetail>({
    queryKey: [
      'individual',
      businessArea,
      programId,
      individualId,
      selectedProgram?.code,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsRetrieve({
        businessAreaSlug: businessArea,
        programCode: programId || selectedProgram?.code || '',
        id: individualId,
      }),
    enabled:
      !!businessArea &&
      !!individualId &&
      (!!programId || !!selectedProgram?.code),
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
