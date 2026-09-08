import PhotoModal from '@core/PhotoModal/PhotoModal';
import type { ReactElement } from 'react';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/index';
import { restQueryKey } from '@utils/queryKeys';
import type { IndividualPhotoDetail } from '@restgenerated/models/IndividualPhotoDetail';
import { useQuery } from '@tanstack/react-query';
import { useProgramContext } from 'src/programContext';

interface GrievanceIndividualPhotoModalProps {
  isCurrent?: boolean;
  individualId?: string;
  photoPath?: string;
  programCode?: string;
}

export function GrievanceIndividualPhotoModal({
  isCurrent,
  individualId,
  photoPath,
  programCode,
}: GrievanceIndividualPhotoModalProps): ReactElement {
  const { businessArea } = useBaseUrl();
  const { selectedProgram } = useProgramContext();

  const effectiveProgramCode = programCode || selectedProgram?.code || '';
  const individualPhotosParams = {
    businessAreaSlug: businessArea,
    programCode: effectiveProgramCode,
    id: individualId || '',
  };
  const { data } = useQuery<IndividualPhotoDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsIndividualsPhotosRetrieve,
      individualPhotosParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsPhotosRetrieve(
        individualPhotosParams,
      ),
    enabled:
      !!isCurrent && !!businessArea && !!effectiveProgramCode && !!individualId,
  });

  // For current value: fetch from API
  // For new value: photoPath is now a full URL from backend (using default_storage.url())
  const photoUrl = isCurrent ? data?.photo : photoPath || null;

  if (!photoUrl) {
    return <>-</>;
  }

  return <PhotoModal src={photoUrl} />;
}
