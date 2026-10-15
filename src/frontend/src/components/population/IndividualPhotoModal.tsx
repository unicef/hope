import PhotoModal from '@core/PhotoModal/PhotoModal';
import type { ReactElement } from 'react';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import type { IndividualPhotoDetail } from '@restgenerated/models/IndividualPhotoDetail';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
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

  const individualPhotosParams = {
    businessAreaSlug: businessArea,
    programCode: selectedProgram?.code || '',
    id: individual?.id,
  };

  const { data, isFetching, refetch } = useQuery<IndividualPhotoDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsIndividualsPhotosRetrieve,
      individualPhotosParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsPhotosRetrieve(
        individualPhotosParams,
      ),
    // Signed blob URLs expire quickly, so fetch a fresh one each time the modal opens.
    enabled: false,
  });

  return (
    <PhotoModal
      src={isFetching ? undefined : data?.photo}
      onOpen={() => refetch()}
      variant="button"
      title="Individuals's Photo"
    />
  );
}
