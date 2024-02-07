import * as React from 'react';
import {
  KoboErrorNode,
  KoboImportDataQueryHookResult,
} from '../../../../__generated__/graphql';
import { ImportCounters } from '../ImportCounters';
import { ErrorsKobo } from './KoboErrors';

export interface KoboImportDataRepresentationPropTypes {
  koboImportData: KoboImportDataQueryHookResult['data']['koboImportData'];
  loading: boolean;
}
export function KoboImportDataRepresentation({
  koboImportData,
  loading,
}: KoboImportDataRepresentationPropTypes): React.ReactElement {
  if (!koboImportData || loading) {
    return null;
  }
  return (
    <>
      <ErrorsKobo
        errors={koboImportData.koboValidationErrors as KoboErrorNode[]}
      />
      <ImportCounters
        numberOfHouseholds={koboImportData.numberOfHouseholds}
        numberOfIndividuals={koboImportData.numberOfIndividuals}
      />
    </>
  );
}
