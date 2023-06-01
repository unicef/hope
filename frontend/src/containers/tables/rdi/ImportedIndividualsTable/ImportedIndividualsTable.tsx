import { Box, Checkbox, FormControlLabel, Grid } from '@material-ui/core';
import React, { ReactElement, useState } from 'react';
import {
  AllImportedIndividualsQueryVariables,
  AllMergedIndividualsQueryVariables,
  HouseholdChoiceDataQuery,
  ImportedIndividualMinimalFragment,
  MergedIndividualMinimalFragment,
  useAllImportedIndividualsQuery,
  useAllMergedIndividualsQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells as importedIndividualHeadCells } from './ImportedIndividualsTableHeadCells';
import { headCells as mergedIndividualHeadCells } from './MergedIndividualsTableHeadCells';
import { ImportedIndividualsTableRow } from './ImportedIndividualsTableRow';

interface ImportedIndividualsTableProps {
  rdiId: string;
  household?: string;
  title?: string;
  showCheckbox?: boolean;
  rowsPerPageOptions?: number[];
  isOnPaper?: boolean;
  businessArea: string;
  choicesData: HouseholdChoiceDataQuery;
  isMerged: boolean;
}

export function ImportedIndividualsTable({
  rdiId,
  isOnPaper = false,
  title,
  household,
  rowsPerPageOptions = [10, 15, 20],
  showCheckbox,
  businessArea,
  choicesData,
  isMerged,
}: ImportedIndividualsTableProps): ReactElement {
  const [showDuplicates, setShowDuplicates] = useState(false);

  const initialVariables = {
    rdiId,
    household,
    duplicatesOnly: showDuplicates,
    businessArea,
  };

  return (
    <div data-cy='imported-individuals-table'>
      {showCheckbox && (
        <Grid container justifyContent='flex-end' spacing={3}>
          <Grid item>
            <Box p={3}>
              <FormControlLabel
                control={
                  <Checkbox
                    color='primary'
                    checked={showDuplicates}
                    onChange={() => setShowDuplicates(!showDuplicates)}
                  />
                }
                label='Show duplicates only'
              />
            </Box>
          </Grid>
        </Grid>
      )}
      {isMerged ?
          <UniversalTable<
            MergedIndividualMinimalFragment,
            AllMergedIndividualsQueryVariables
          >
            title={title}
            headCells={mergedIndividualHeadCells}
            query={useAllMergedIndividualsQuery}
            queriedObjectName='allMergedIndividuals'
            rowsPerPageOptions={rowsPerPageOptions}
            initialVariables={initialVariables}
            isOnPaper={isOnPaper}
            renderRow={(row) => (
              <ImportedIndividualsTableRow
                choices={choicesData}
                key={row.id}
                isMerged={isMerged}
                individual={row}
              />
            )}
          />
        :
          <UniversalTable<
        ImportedIndividualMinimalFragment,
        AllImportedIndividualsQueryVariables
      >
        title={title}
        headCells={importedIndividualHeadCells}
        query={useAllImportedIndividualsQuery}
        queriedObjectName='allImportedIndividuals'
        rowsPerPageOptions={rowsPerPageOptions}
        initialVariables={initialVariables}
        isOnPaper={isOnPaper}
        renderRow={(row) => (
          <ImportedIndividualsTableRow
            choices={choicesData}
            key={row.id}
            isMerged={isMerged}
            individual={row}
          />
        )}
      />
      }
    </div>
  );
}
