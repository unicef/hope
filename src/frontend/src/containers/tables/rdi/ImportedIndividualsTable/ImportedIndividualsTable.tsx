import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestQueryTable } from '@components/rest/UniversalRestQueryTable/UniversalRestQueryTable';
import Box from '@mui/material/Box';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import Grid from '@mui/material/Grid';
import { RestService } from '@restgenerated/services/RestService';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useProgramContext } from 'src/programContext';
import { headCells as importedIndividualHeadCells } from './ImportedIndividualsTableHeadCells';
import { ImportedIndividualsTableRow } from './ImportedIndividualsTableRow';
import { headCells as mergedIndividualHeadCells } from './MergedIndividualsTableHeadCells';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RegistrationDataImportStatusEnum } from '@restgenerated/models/RegistrationDataImportStatusEnum';

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
  const { programId } = useBaseUrl();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const [page, setPage] = useState(0);
  const notAllowedRdiShowPreviewStatuses = [
    RegistrationDataImportStatusEnum.LOADING,
    RegistrationDataImportStatusEnum.IMPORTING,
    RegistrationDataImportStatusEnum.IMPORT_SCHEDULED,
    RegistrationDataImportStatusEnum.IMPORT_ERROR,
  ];
  const initialVariables = useMemo(
    () => ({
      rdiId,
      household,
      duplicatesOnly: showDuplicates,
      businessArea,
      rdiMergeStatus: isMerged ? 'MERGED' : 'PENDING',
    }),
    [rdiId, household, showDuplicates, businessArea, isMerged],
  );

  const [queryVariables, setQueryVariables] = useState(initialVariables);

  useEffect(() => {
    setQueryVariables(initialVariables);
  }, [initialVariables]);

  const replacements = {
    unicefId: (_beneficiaryGroup) => `${_beneficiaryGroup?.memberLabel} ID`,
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

  const { data: countData } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsHouseholdsCount',
      programId,
      businessArea,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsCountRetrieve(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
        ),
      ),
    enabled: page === 0 && !notAllowedRdiShowPreviewStatuses.includes(rdi.status),
  });

  const itemsCount = usePersistedCount(page, countData);

  return (
    <div data-cy="imported-individuals-table">
      {showCheckbox && (
        <Grid container spacing={3} sx={{ justifyContent: 'flex-end' }}>
          <Grid>
            <Box sx={{ p: 3 }}>
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
      <UniversalRestQueryTable
        title={title}
        isOnPaper={false}
        headCells={isMerged ? adjustedMergedIndividualsHeadCells : adjustedImportedIndividualsHeadCells}
        query={RestService.restBusinessAreasProgramsIndividualsList}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        itemsCount={itemsCount}
        page={page}
        setPage={setPage}
        renderRow={(row) => (
          <ImportedIndividualsTableRow
            key={row.id}
            individual={row}
            rdi={rdi}
          />
        )}
        customEnabled={!notAllowedRdiShowPreviewStatuses.includes(rdi.status)}
      />
    </div>
  );
}

export default withErrorBoundary(
  ImportedIndividualsTable,
  'ImportedIndividualsTable',
);
