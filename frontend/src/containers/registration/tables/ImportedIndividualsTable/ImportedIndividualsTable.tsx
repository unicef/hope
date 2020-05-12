import React, { ReactElement } from 'react';
import {
  AllImportedIndividualsQueryVariables,
  ImportedIndividualMinimalFragment,
  useAllImportedIndividualsQuery,
  useHouseholdChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../../tables/UniversalTable';
import { ImportedIndividualsTableRow } from './ImportedIndividualsTableRow';
import { headCells } from './ImportedIndividualsTableHeadCells';

interface ImportedIndividualsTableProps {
  rdiId?: string;
  household?: string;
  title?: string;
  isOnPaper?: boolean;
  rowsPerPageOptions?: number[];
}

export function ImportedIndividualsTable({
  rdiId,
  isOnPaper = false,
  title,
  household,
  rowsPerPageOptions = [10, 15, 20],
}: ImportedIndividualsTableProps): ReactElement {
  const initialVariables = {
    rdiId,
    household,
  };

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();
  return (
    <UniversalTable<
      ImportedIndividualMinimalFragment,
      AllImportedIndividualsQueryVariables
    >
      title={title}
      headCells={headCells}
      query={useAllImportedIndividualsQuery}
      queriedObjectName='allImportedIndividuals'
      rowsPerPageOptions={rowsPerPageOptions}
      initialVariables={initialVariables}
      isOnPaper={isOnPaper}
      renderRow={(row) => (
        <ImportedIndividualsTableRow
          choices={choicesData}
          key={row.id}
          individual={row}
        />
      )}
    />
  );
}
