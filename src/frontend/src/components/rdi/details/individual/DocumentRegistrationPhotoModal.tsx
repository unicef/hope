import PhotoModal from '@core/PhotoModal/PhotoModal';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { IndividualPhotoDetail } from '@restgenerated/models/IndividualPhotoDetail';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';

interface DocumentRegistrationPhotoModalProps {
  individual: IndividualDetail;
  documentNumber: string;
  documentId: string;
}

export function DocumentRegistrationPhotoModal({
  individual,
  documentNumber,
  documentId,
}: DocumentRegistrationPhotoModalProps): ReactElement {
  const { businessArea } = useBaseUrl();
  const { selectedProgram } = useProgramContext();

  const photoParams = {
    businessAreaSlug: businessArea,
    programCode: selectedProgram?.code || '',
    id: individual?.id,
  };
  const { data } = useQuery<IndividualPhotoDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsIndividualsPhotosRetrieve,
      photoParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsPhotosRetrieve(
        photoParams,
      ),
    enabled: !!businessArea && !!selectedProgram?.code && !!individual?.id,
  });

  const documentWithPhoto = data?.documents?.find(
    (doc) => doc.id === documentId,
  );

  return (
    <PhotoModal
      src={documentWithPhoto?.photo}
      linkText={documentNumber}
      variant="link"
      title="Document's Photo"
    />
  );
}
