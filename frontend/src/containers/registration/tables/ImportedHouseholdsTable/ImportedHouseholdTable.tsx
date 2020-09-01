import React, { ReactElement, useState } from 'react';
import {
  AllImportedHouseholdsQueryVariables,
  ImportedHouseholdMinimalFragment,
  useAllImportedHouseholdsQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../../tables/UniversalTable';
import { ImportedHouseholdTableRow } from './ImportedHouseholdTableRow';
import { headCells } from './ImportedHouseholdTableHeadCells';
import { FormControlLabel, Checkbox, Grid, Box } from '@material-ui/core';

export function ImportedHouseholdTable({ rdiId }): ReactElement {
  const initialVariables = {
    rdiId,
  };
  const [showDuplicates, setShowDuplicates] = useState(false);
  return (
    <>
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

      <UniversalTable<
        ImportedHouseholdMinimalFragment,
        AllImportedHouseholdsQueryVariables
      >
        headCells={headCells}
        query={useAllImportedHouseholdsQuery}
        queriedObjectName='allImportedHouseholds'
        rowsPerPageOptions={[10, 15, 20]}
        initialVariables={initialVariables}
        isOnPaper={false}
        renderRow={(row) => (
          <ImportedHouseholdTableRow key={row.id} household={row} />
        )}
      />
    </>
  );
}
