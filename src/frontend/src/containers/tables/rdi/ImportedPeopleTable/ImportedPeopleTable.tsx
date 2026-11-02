import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Checkbox, FormControlLabel, Grid } from '@mui/material';
import type { IndividualList } from '@restgenerated/models/IndividualList';
import type { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import type { ReactElement } from 'react';
import { useMemo, useState } from 'react';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTableState } from '@hooks/useTableState';
import { headCells as importedPeopleTableHeadCells } from './ImportedPeopleTableHeadCells';
import { ImportedPeopleTableRow } from './ImportedPeopleTableRow';
import { headCells as mergedPeopleTableHeadCells } from './MergedPeopleTableHeadCells';
import type { IndividualChoices } from '@restgenerated/models/IndividualChoices';

interface ImportedPeopleTableProps {
  rdi;
  rdiId: string;
  household?: string;
  title?: string;
  showCheckbox?: boolean;
  rowsPerPageOptions?: number[];
  isOnPaper?: boolean;
  businessArea: string;
  choicesData: IndividualChoices;
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

  const filterVariables = useMemo(
    () => ({
      rdiId,
      household,
      duplicatesOnly: showDuplicates,
      businessAreaSlug: businessArea,
      programCode: programId,
    }),
    [rdiId, household, showDuplicates, businessArea, programId],
  );

  const table = useTableState({
    rowsPerPageOptions,
    resetPageOn: filterVariables,
  });
  const { page } = table;
  const listVariables = useMemo(
    () => ({ ...filterVariables, ...table.paginationParams }),
    [filterVariables, table.paginationParams],
  );

  const individualsListParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    listVariables,
  );
  const { data, isLoading, isFetching, error } =
    useQuery<PaginatedIndividualListList>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasProgramsIndividualsList,
        individualsListParams,
      ),
      queryFn: () =>
        RestService.restBusinessAreasProgramsIndividualsList(
          individualsListParams,
        ),
      placeholderData: keepPreviousData,
    });

  const individualsCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    filterVariables,
  );
  const { data: countData } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsIndividualsCountRetrieve,
      individualsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsCountRetrieve(
        individualsCountParams,
      ),
    enabled: page === 0,
  });

  const itemsCount = usePersistedCount(page, countData);

  return (
    <div data-cy="imported-individuals-table">
      {showCheckbox && (
        <Grid
          container
          spacing={3}
          sx={{
            justifyContent: 'flex-end',
          }}
        >
          <Grid>
            <Box
              sx={{
                p: 3,
              }}
            >
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
          tableState={table}
          data={data}
          error={error}
          isLoading={isLoading}
          isFetching={isFetching}
          isOnPaper={isOnPaper}
          itemsCount={itemsCount}
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
          tableState={table}
          isOnPaper={isOnPaper}
          data={data}
          error={error}
          isLoading={isLoading}
          isFetching={isFetching}
          itemsCount={itemsCount}
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
