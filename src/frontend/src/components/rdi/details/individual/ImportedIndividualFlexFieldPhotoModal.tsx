import { useParams } from 'react-router-dom';
import { ReactElement } from 'react';
import PhotoModal from '@components/core/PhotoModal/PhotoModal';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

export function ImportedIndividualFlexFieldPhotoModal({ field }): ReactElement {
  const { id } = useParams();
  const { businessArea, programId } = useBaseUrl();

  const { data } = useQuery<IndividualDetail>({
    queryKey: ['individual', businessArea, programId, id],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id: id,
      }),
    enabled: !!businessArea && !!programId && !!id,
  });

  if (!data) {
    return null;
  }

  const picUrl = data.flexFields?.[field.name];

  return <PhotoModal src={picUrl} />;
}
