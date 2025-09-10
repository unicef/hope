import { ImportCounters } from '../ImportCounters';
import { XlsxErrors } from './XlsxErrors';
import { ReactElement } from 'react';
import { ImportData } from '@restgenerated/models/ImportData';

export interface XlsxImportDataRepresentationPropTypes {
  xlsxImportData: ImportData;
  loading: boolean;
}
export function XlsxImportDataRepresentation({
  xlsxImportData,
  loading,
}: XlsxImportDataRepresentationPropTypes): ReactElement {
  if (!xlsxImportData || loading) {
    return null;
  }
  return (
    <>
      <XlsxErrors
        errors={xlsxImportData.xlsxValidationErrors}
      />
      <ImportCounters
        numberOfHouseholds={xlsxImportData.numberOfHouseholds}
        numberOfIndividuals={xlsxImportData.numberOfIndividuals}
      />
    </>
  );
}
