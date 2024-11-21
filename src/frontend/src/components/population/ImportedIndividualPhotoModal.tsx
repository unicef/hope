import * as React from 'react';
import {
  ImportedIndividualNode,
  useImportedIndividualPhotosQuery,
} from '@generated/graphql';
import { PhotoModal } from '@core/PhotoModal/PhotoModal';
import { useProgramContext } from 'src/programContext';

interface ImportedIndividualPhotoModalProps {
  individual: ImportedIndividualNode;
}

export function ImportedIndividualPhotoModal({
  individual,
}: ImportedIndividualPhotoModalProps): React.ReactElement {
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const { data } = useImportedIndividualPhotosQuery({
    variables: { id: individual?.id },
    fetchPolicy: 'network-only',
  });

  return (
    <PhotoModal
      src={data?.importedIndividual?.photo}
      variant="button"
      title={`${beneficiaryGroup?.memberLabel}'s Photo`}
    />
  );
}
