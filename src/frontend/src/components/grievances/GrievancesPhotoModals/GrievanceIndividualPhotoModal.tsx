import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/index';
import { IndividualPhotoDetail } from '@restgenerated/models/IndividualPhotoDetail';
import { useQuery } from '@tanstack/react-query';
import { useProgramContext } from 'src/programContext';

interface GrievanceIndividualPhotoModalProps {
  isCurrent?: boolean;
  individualId?: string;
  photoPath?: string;
}

export function GrievanceIndividualPhotoModal({
  isCurrent,
  individualId,
  photoPath,
}: GrievanceIndividualPhotoModalProps): ReactElement {
  const { businessArea } = useBaseUrl();
  const { selectedProgram } = useProgramContext();

  const { data } = useQuery<IndividualPhotoDetail>({
    queryKey: [
      'individualPhotos',
      businessArea,
      selectedProgram?.slug,
      individualId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsPhotosRetrieve({
        businessAreaSlug: businessArea,
        programSlug: selectedProgram?.slug || '',
        id: individualId,
      }),
    enabled:
      !!isCurrent &&
      !!businessArea &&
      !!selectedProgram?.slug &&
      !!individualId,
  });

  // For current value: fetch from API
  // For new value: photoPath is now a full URL from backend (using default_storage.url())
  const photoUrl = isCurrent ? data?.photo : photoPath || null;

  if (!photoUrl) {
    return <>-</>;
  }

  return <PhotoModal src={photoUrl} />;
}
