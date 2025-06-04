import { useParams } from 'react-router-dom';
import { ReactElement } from 'react';
import { useIndividualFlexFieldsQuery } from '@generated/graphql';
import PhotoModal from '@components/core/PhotoModal/PhotoModal';

export function ImportedIndividualFlexFieldPhotoModal({ field }): ReactElement {
  const { id } = useParams();
  const { data } = useIndividualFlexFieldsQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });

  if (!data) {
    return null;
  }

  const { flexFields } = data.individual;
  const picUrl = flexFields[field.name];

  return <PhotoModal src={picUrl} />;
}
