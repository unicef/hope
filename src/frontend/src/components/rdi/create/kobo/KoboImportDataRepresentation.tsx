import { ImportCounters } from '../ImportCounters';
import { ErrorsKobo } from './KoboErrors';
import type { ReactElement } from 'react';
import type { KoboImportData } from '@restgenerated/models/KoboImportData';

export interface KoboImportDataRepresentationPropTypes {
  koboImportData: KoboImportData;
  loading: boolean;
}
export function KoboImportDataRepresentation({
  koboImportData,
  loading,
}: KoboImportDataRepresentationPropTypes): ReactElement {
  if (!koboImportData || loading) {
    return null;
  }
  return (
    <>
      <ErrorsKobo errors={koboImportData.koboValidationErrors} />
      <ImportCounters
        numberOfHouseholds={koboImportData.numberOfHouseholds}
        numberOfIndividuals={koboImportData.numberOfIndividuals}
      />
    </>
  );
}
