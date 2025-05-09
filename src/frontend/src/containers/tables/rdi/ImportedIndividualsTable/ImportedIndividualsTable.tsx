import {
  AllIndividualsQueryVariables,
  IndividualMinimalFragment,
  IndividualRdiMergeStatus,
} from '@generated/graphql';
import { Box, Checkbox, FormControlLabel, Grid2 as Grid } from '@mui/material';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { headCells as importedIndividualHeadCells } from './ImportedIndividualsTableHeadCells';
import { ImportedIndividualsTableRow } from './ImportedIndividualsTableRow';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';
import { headCells as mergedIndividualHeadCells } from './MergedIndividualsTableHeadCells';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestQueryTable } from '@components/rest/UniversalRestQueryTable/UniversalRestQueryTable';
import { RestService } from '@restgenerated/services/RestService';

interface ImportedIndividualsTableProps {
  rdi;
  rdiId: string;
  household?: string;
  title?: string;
  showCheckbox?: boolean;
  rowsPerPageOptions?: number[];
  isOnPaper?: boolean;
  businessArea: string;
  isMerged: boolean;
}

function ImportedIndividualsTable({
  rdi,
  rdiId,
  title,
  household,
  showCheckbox,
  businessArea,
  isMerged,
}: ImportedIndividualsTableProps): ReactElement {
  const [showDuplicates, setShowDuplicates] = useState(false);
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const initialVariables = useMemo(
    () => ({
      rdiId,
      household,
      duplicatesOnly: showDuplicates,
      businessArea,
      rdiMergeStatus: isMerged
        ? IndividualRdiMergeStatus.Merged
        : IndividualRdiMergeStatus.Pending,
    }),
    [rdiId, household, showDuplicates, businessArea, isMerged],
  );

  const [queryVariables, setQueryVariables] = useState(initialVariables);

  useEffect(() => {
    setQueryVariables(initialVariables);
  }, [initialVariables]);

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
        <UniversalRestQueryTable<
          IndividualMinimalFragment,
          AllIndividualsQueryVariables
        >
          title={title}
          headCells={adjustedMergedIndividualsHeadCells}
          query={RestService.restBusinessAreasProgramsIndividualsList}
          queryVariables={queryVariables}
          setQueryVariables={setQueryVariables}
          renderRow={(row) => (
            <ImportedIndividualsTableRow
              key={row.id}
              individual={row}
              rdi={rdi}
            />
          )}
        />
      ) : (
        <UniversalRestQueryTable
          queryVariables={queryVariables}
          setQueryVariables={setQueryVariables}
          query={RestService.restBusinessAreasProgramsIndividualsList}
          title={title}
          headCells={adjustedImportedIndividualsHeadCells}
          renderRow={(row) => (
            <ImportedIndividualsTableRow
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
