import { useParams } from 'react-router-dom';
import type { ReactElement } from 'react';
import PhotoModal from '@components/core/PhotoModal/PhotoModal';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useQuery } from '@tanstack/react-query';

export function ImportedIndividualFlexFieldPhotoModal({ field }): ReactElement {
  const { id } = useParams();
  const { businessArea, programId } = useBaseUrl();

  const individualParams = {
    businessAreaSlug: businessArea,
    programCode: programId,
    id: id,
  };
  const { data } = useQuery<IndividualDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsIndividualsRetrieve,
      individualParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsRetrieve(
        individualParams,
      ),
    enabled: !!businessArea && !!programId && !!id,
  });

  if (!data) {
    return null;
  }

  const picUrl = data.flexFields?.[field.name];

  return <PhotoModal src={picUrl} />;
}
