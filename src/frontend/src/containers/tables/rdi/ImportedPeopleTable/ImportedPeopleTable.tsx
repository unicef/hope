import { Box, Checkbox, FormControlLabel, Grid2 as Grid } from '@mui/material';
import { ReactElement, useState } from 'react';
import {
  AllIndividualsQueryVariables,
  HouseholdChoiceDataQuery,
  IndividualMinimalFragment,
  MergedIndividualMinimalFragment,
  useAllIndividualsQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells as importedPeopleTableHeadCells } from './ImportedPeopleTableHeadCells';
import { headCells as mergedPeopleTableHeadCells } from './MergedPeopleTableHeadCells';
import { ImportedPeopleTableRow } from './ImportedPeopleTableRow';

interface ImportedPeopleTableProps {
  rdi;
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

export function ImportedPeopleTable({
  rdi,
  rdiId,
  isOnPaper = false,
  title,
  household,
  rowsPerPageOptions = [10, 15, 20],
  showCheckbox,
  businessArea,
  choicesData,
  isMerged,
}: ImportedPeopleTableProps): ReactElement {
  const [showDuplicates, setShowDuplicates] = useState(false);

  const initialVariables = {
    rdiId,
    household,
    duplicatesOnly: showDuplicates,
    businessArea,
  };

  return (
    <div data-cy="imported-individuals-table">
      {showCheckbox && (
        <Grid container justifyContent="flex-end" spacing={3}>
          <Grid>
            <Box p={3}>
              <FormControlLabel
                control={
                  <Checkbox
                    color="primary"
                    checked={showDuplicates}
                    onChange={() => setShowDuplicates(!showDuplicates)}
                  />
                }
                label="Show duplicates only"
              />
            </Box>
          </Grid>
        </Grid>
      )}
      {isMerged ? (
        <UniversalTable<
          MergedIndividualMinimalFragment,
          AllIndividualsQueryVariables
        >
          title={title}
          headCells={mergedPeopleTableHeadCells}
          query={useAllIndividualsQuery}
          queriedObjectName="allIndividuals"
          rowsPerPageOptions={rowsPerPageOptions}
          initialVariables={initialVariables}
          isOnPaper={isOnPaper}
          renderRow={(row) => (
            <ImportedPeopleTableRow
              choices={choicesData}
              key={row.id}
              individual={row}
              rdi={rdi}
            />
          )}
        />
      ) : (
        <UniversalTable<IndividualMinimalFragment, AllIndividualsQueryVariables>
          title={title}
          headCells={importedPeopleTableHeadCells}
          query={useAllIndividualsQuery}
          queriedObjectName="allIndividuals"
          rowsPerPageOptions={rowsPerPageOptions}
          initialVariables={initialVariables}
          isOnPaper={isOnPaper}
          renderRow={(row) => (
            <ImportedPeopleTableRow
              choices={choicesData}
              key={row.id}
              individual={row}
              rdi={rdi}
            />
          )}
        />
      )}
    </div>
  );
}
