import PhotoModal from '@core/PhotoModal/PhotoModal';
import type { ReactElement } from 'react';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import type { IndividualPhotoDetail } from '@restgenerated/models/IndividualPhotoDetail';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';

interface DocumentPopulationPhotoModalProps {
  individual: IndividualDetail;
  documentNumber: string;
  documentId: string;
}

export function DocumentPopulationPhotoModal({
  individual,
  documentNumber,
  documentId,
}: DocumentPopulationPhotoModalProps): ReactElement {
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

  const documentWithPhoto = data?.documents?.find(
    (doc) => doc.id === documentId,
  );

  return (
    <PhotoModal
      src={isFetching ? undefined : documentWithPhoto?.photo}
      onOpen={() => refetch()}
      linkText={documentNumber}
      variant="link"
      title="Document's Photo"
    />
  );
}
