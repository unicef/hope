import * as React from 'react';
import {
  XlsxImportDataQueryResult,
  XlsxRowErrorNode,
} from '../../../../__generated__/graphql';
import { ImportCounters } from '../ImportCounters';
import { XlsxErrors } from './XlsxErrors';

export interface XlsxImportDataRepresentationPropTypes {
  xlsxImportData: XlsxImportDataQueryResult['data']['importData'];
  loading: boolean;
}
export function XlsxImportDataRepresentation({
  xlsxImportData,
  loading,
}: XlsxImportDataRepresentationPropTypes): React.ReactElement {
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
