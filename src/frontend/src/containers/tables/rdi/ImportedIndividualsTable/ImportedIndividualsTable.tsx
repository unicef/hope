import {
  AllIndividualsQueryVariables,
  HouseholdChoiceDataQuery,
  IndividualMinimalFragment,
  IndividualRdiMergeStatus,
  useAllIndividualsQuery,
} from '@generated/graphql';
import { Box, Checkbox, FormControlLabel, Grid } from '@mui/material';
import { ReactElement, useState } from 'react';
import { UniversalTable } from '../../UniversalTable';
import { headCells as importedIndividualHeadCells } from './ImportedIndividualsTableHeadCells';
import { ImportedIndividualsTableRow } from './ImportedIndividualsTableRow';
import { headCells as mergedIndividualHeadCells } from './MergedIndividualsTableHeadCells';

interface ImportedIndividualsTableProps {
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

export function ImportedIndividualsTable({
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
}: ImportedIndividualsTableProps): ReactElement {
  const [showDuplicates, setShowDuplicates] = useState(false);

  const initialVariables = {
    rdiId,
    household,
    duplicatesOnly: showDuplicates,
    businessArea,
    rdiMergeStatus: isMerged
      ? IndividualRdiMergeStatus.Merged
      : IndividualRdiMergeStatus.Pending,
  };

  return (
    <div data-cy="imported-individuals-table">
      {showCheckbox && (
        <Grid container justifyContent="flex-end" spacing={3}>
          <Grid item>
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
        <UniversalTable<IndividualMinimalFragment, AllIndividualsQueryVariables>
          title={title}
          headCells={mergedIndividualHeadCells}
          query={useAllIndividualsQuery}
          queriedObjectName="allIndividuals"
          rowsPerPageOptions={rowsPerPageOptions}
          initialVariables={initialVariables}
          isOnPaper={isOnPaper}
          renderRow={(row) => (
            <ImportedIndividualsTableRow
              choices={choicesData}
              key={row.id}
              isMerged={isMerged}
              individual={row}
              rdi={rdi}
            />
          )}
        />
      ) : (
        <UniversalTable<IndividualMinimalFragment, AllIndividualsQueryVariables>
          title={title}
          headCells={importedIndividualHeadCells}
          query={useAllIndividualsQuery}
          queriedObjectName="allIndividuals"
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
      )}
    </div>
  );
}
