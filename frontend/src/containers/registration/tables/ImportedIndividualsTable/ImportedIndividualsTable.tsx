import React, {ReactElement, useState} from 'react';
import {Box, Checkbox, FormControlLabel, Grid} from '@material-ui/core';
import {
  AllImportedIndividualsQueryVariables,
  ImportedIndividualMinimalFragment,
  useAllImportedIndividualsQuery,
  useHouseholdChoiceDataQuery,
} from '../../../../__generated__/graphql';
import {UniversalTable} from '../../../tables/UniversalTable';
import {LoadingComponent} from '../../../../components/LoadingComponent';
import {ImportedIndividualsTableRow} from './ImportedIndividualsTableRow';
import {headCells} from './ImportedIndividualsTableHeadCells';

interface ImportedIndividualsTableProps {
  rdiId?: string;
  household?: string;
  title?: string;
  showCheckbox?: boolean;
  rowsPerPageOptions?: number[];
  isOnPaper?: boolean;
  businessArea: string;
}

export function ImportedIndividualsTable({
  rdiId,
  isOnPaper = false,
  title,
  household,
  rowsPerPageOptions = [10, 15, 20],
  showCheckbox,
  businessArea,
}: ImportedIndividualsTableProps): ReactElement {
  const [showDuplicates, setShowDuplicates] = useState(false);

  const initialVariables = {
    rdiId,
    household,
    duplicatesOnly: showDuplicates,
    businessArea,
  };

  const { data: choicesData, loading } = useHouseholdChoiceDataQuery();

  if (loading) return <LoadingComponent />;

  if (!choicesData) {
    return null;
  }

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
