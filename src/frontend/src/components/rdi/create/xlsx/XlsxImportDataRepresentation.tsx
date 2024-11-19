import {
  XlsxImportDataQueryResult,
  XlsxRowErrorNode,
} from '@generated/graphql';
import { ImportCounters } from '../ImportCounters';
import { XlsxErrors } from './XlsxErrors';
import { ReactElement } from 'react';

export interface XlsxImportDataRepresentationPropTypes {
  xlsxImportData: XlsxImportDataQueryResult['data']['importData'];
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
        errors={xlsxImportData.xlsxValidationErrors as XlsxRowErrorNode[]}
      />
      <ImportCounters
        numberOfHouseholds={xlsxImportData.numberOfHouseholds}
        numberOfIndividuals={xlsxImportData.numberOfIndividuals}
      />
    </>
  );
}
