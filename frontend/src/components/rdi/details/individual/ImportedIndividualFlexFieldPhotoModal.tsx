import * as React from 'react';
import { useParams } from 'react-router-dom';
import { PhotoModal } from '../../../core/PhotoModal/PhotoModal';
import { useImportedIndividualFlexFieldsQuery } from '../../../../__generated__/graphql';

export function ImportedIndividualFlexFieldPhotoModal({
  field,
}): React.ReactElement {
  const { id } = useParams();
  const { data } = useImportedIndividualFlexFieldsQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });

  if (!data) {
    return null;
  }

  const { flexFields } = data.importedIndividual;
  const picUrl = flexFields[field.name];

  return <PhotoModal src={picUrl} />;
}
