import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Checkbox, FormControlLabel, Grid2 as Grid } from '@mui/material';
import { IndividualList } from '@restgenerated/models/IndividualList';
import { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { headCells as importedPeopleTableHeadCells } from './ImportedPeopleTableHeadCells';
import { ImportedPeopleTableRow } from './ImportedPeopleTableRow';
import { headCells as mergedPeopleTableHeadCells } from './MergedPeopleTableHeadCells';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';

interface ImportedPeopleTableProps {
  rdi;
  rdiId: string;
  household?: string;
  title?: string;
  showCheckbox?: boolean;
  rowsPerPageOptions?: number[];
  isOnPaper?: boolean;
  businessArea: string;
  choicesData: HouseholdChoices;
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
  const { programId } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      rdiId,
      household,
      duplicatesOnly: showDuplicates,
      businessAreaSlug: businessArea,
      programSlug: programId,
    }),
    [rdiId, household, showDuplicates, businessArea, programId],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const { data, isLoading, error } = useQuery<PaginatedIndividualListList>({
    queryKey: [
      'businessAreasProgramsIndividualsList',
      queryVariables,
      businessArea,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      ),
  });

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
        <UniversalRestTable
          title={title}
          headCells={mergedPeopleTableHeadCells}
          queryVariables={queryVariables}
          setQueryVariables={setQueryVariables}
          data={data}
          error={error}
          isLoading={isLoading}
          rowsPerPageOptions={rowsPerPageOptions}
          isOnPaper={isOnPaper}
          renderRow={(row: IndividualList) => (
            <ImportedPeopleTableRow
              choices={choicesData}
              key={row.id}
              individual={row}
              rdi={rdi}
            />
          )}
        />
      ) : (
        <UniversalRestTable
          title={title}
          headCells={importedPeopleTableHeadCells}
          queryVariables={queryVariables}
          setQueryVariables={setQueryVariables}
          rowsPerPageOptions={rowsPerPageOptions}
          isOnPaper={isOnPaper}
          data={data}
          error={error}
          isLoading={isLoading}
          renderRow={(row: IndividualList) => (
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
