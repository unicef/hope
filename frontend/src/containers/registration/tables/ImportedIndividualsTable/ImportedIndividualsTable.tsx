import React, { ReactElement, useState } from 'react';
import {
  AllImportedIndividualsQueryVariables,
  ImportedIndividualMinimalFragment,
  useAllImportedIndividualsQuery,
  useHouseholdChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { FormControlLabel, Checkbox, Grid, Box } from '@material-ui/core';
import { UniversalTable } from '../../../tables/UniversalTable';
import { ImportedIndividualsTableRow } from './ImportedIndividualsTableRow';
import { headCells } from './ImportedIndividualsTableHeadCells';

interface ImportedIndividualsTableProps {
  rdiId?: string;
  household?: string;
  title?: string;
  showCheckbox?: boolean;
  rowsPerPageOptions?: number[];
  isOnPaper?: boolean;
}

export function ImportedIndividualsTable({
  rdiId,
  isOnPaper = false,
  title,
  household,
  rowsPerPageOptions = [10, 15, 20],
  showCheckbox,
}: ImportedIndividualsTableProps): ReactElement {
  const [showDuplicates, setShowDuplicates] = useState(false);

  const initialVariables = {
    rdiId,
    household,
    duplicatesOnly: showDuplicates,
  };

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();
  return (
    <>
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
    </>
  );
}
