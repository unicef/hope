import * as React from 'react';
import { UniversalTable } from '@containers/tables/UniversalTable';
import {
  AllSanctionListIndividualsQueryVariables,
  useAllSanctionListIndividualsQuery,
  AllSanctionListIndividualsQuery,
} from '@generated/graphql';
import { SanctionListIndividualsTableRow } from './SanctionListIndividualsTableRow';
import { headCells } from './SanctionListIndividualsHeadCells';

export function SanctionListIndividualsTable({ filter }): React.ReactElement {
  const initialVariables = {
    fullNameContains: filter.fullName,
    referenceNumber: filter.referenceNumber,
  };
  return (
    <UniversalTable<
    AllSanctionListIndividualsQuery['allSanctionListIndividuals']['edges'][number]['node'],
    AllSanctionListIndividualsQueryVariables
    >
      headCells={headCells}
      query={useAllSanctionListIndividualsQuery}
      queriedObjectName="allSanctionListIndividuals"
      initialVariables={initialVariables}
      renderRow={(row) => (
        <SanctionListIndividualsTableRow key={row.id} individual={row} />
      )}
    />
  );
}
