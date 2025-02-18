import {
  AllIndividualsQueryVariables,
  HouseholdChoiceDataQuery,
  IndividualMinimalFragment,
  IndividualRdiMergeStatus,
  useAllIndividualsQuery,
} from '@generated/graphql';
import { Box, Checkbox, FormControlLabel, Grid2 as Grid } from '@mui/material';
import { ReactElement, useState } from 'react';
import { UniversalTable } from '../../UniversalTable';
import { headCells as importedIndividualHeadCells } from './ImportedIndividualsTableHeadCells';
import { ImportedIndividualsTableRow } from './ImportedIndividualsTableRow';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';
import { headCells as mergedIndividualHeadCells } from './MergedIndividualsTableHeadCells';
import withErrorBoundary from '@components/core/withErrorBoundary';

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

function ImportedIndividualsTable({
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
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const initialVariables = {
    rdiId,
    household,
    duplicatesOnly: showDuplicates,
    businessArea,
    rdiMergeStatus: isMerged
      ? IndividualRdiMergeStatus.Merged
      : IndividualRdiMergeStatus.Pending,
  };

  const replacements = {
    id: (_beneficiaryGroup) => `${_beneficiaryGroup?.memberLabel} ID`,
    full_name: (_beneficiaryGroup) => _beneficiaryGroup?.memberLabel,
    relationship: (_beneficiaryGroup) =>
      `Relationship to Head of ${_beneficiaryGroup?.groupLabel}`,
  };

  const adjustedMergedIndividualsHeadCells = adjustHeadCells(
    mergedIndividualHeadCells,
    beneficiaryGroup,
    replacements,
  );
  const adjustedImportedIndividualsHeadCells = adjustHeadCells(
    importedIndividualHeadCells,
    beneficiaryGroup,
    replacements,
  );
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
        <UniversalTable<IndividualMinimalFragment, AllIndividualsQueryVariables>
          title={title}
          headCells={adjustedMergedIndividualsHeadCells}
          query={useAllIndividualsQuery}
          queriedObjectName="allIndividuals"
          rowsPerPageOptions={rowsPerPageOptions}
          initialVariables={initialVariables}
          isOnPaper={isOnPaper}
          renderRow={(row) => (
            <ImportedIndividualsTableRow
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
          headCells={adjustedImportedIndividualsHeadCells}
          query={useAllIndividualsQuery}
          queriedObjectName="allIndividuals"
          rowsPerPageOptions={rowsPerPageOptions}
          initialVariables={initialVariables}
          isOnPaper={isOnPaper}
          renderRow={(row) => (
            <ImportedIndividualsTableRow
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

export default withErrorBoundary(
  ImportedIndividualsTable,
  'ImportedIndividualsTable',
);
