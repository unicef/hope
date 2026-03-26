import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { IndividualPhotoDetail } from '@restgenerated/models/IndividualPhotoDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';

interface IndividualPhotoModalProps {
  individual: IndividualDetail;
}

export function IndividualPhotoModal({
  individual,
}: IndividualPhotoModalProps): ReactElement {
  const { businessArea } = useBaseUrl();
  const { selectedProgram } = useProgramContext();

  const { data } = useQuery<IndividualPhotoDetail>({
    queryKey: [
      'individualPhotos',
      businessArea,
      selectedProgram?.code,
      individual?.id,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsPhotosRetrieve({
        businessAreaSlug: businessArea,
        programCode: selectedProgram?.code || '',
        id: individual?.id,
      }),
    enabled: !!businessArea && !!selectedProgram?.code && !!individual?.id,
  });

  return (
    <PhotoModal
      src={data?.photo}
      variant="button"
      title="Individuals's Photo"
    />
  );
}
