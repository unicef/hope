import { Box, Checkbox, FormControlLabel, Grid } from '@material-ui/core';
import React, { ReactElement, useState } from 'react';
import {
  AllImportedIndividualsQueryVariables,
  HouseholdChoiceDataQuery,
  ImportedIndividualMinimalFragment,
  useAllImportedIndividualsQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './ImportedIndividualsTableHeadCells';
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
        <Grid container justify='flex-end' spacing={3}>
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
    </div>
  );
}
