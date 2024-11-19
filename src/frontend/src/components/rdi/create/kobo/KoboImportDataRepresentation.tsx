import {
  KoboErrorNode,
  KoboImportDataQueryHookResult,
} from '@generated/graphql';
import { ImportCounters } from '../ImportCounters';
import { ErrorsKobo } from './KoboErrors';
import { ReactElement } from 'react';

export interface KoboImportDataRepresentationPropTypes {
  koboImportData: KoboImportDataQueryHookResult['data']['koboImportData'];
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
