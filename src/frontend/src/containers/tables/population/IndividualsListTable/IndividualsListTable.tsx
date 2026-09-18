import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { IndividualList } from '@restgenerated/models/IndividualList';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { adjustHeadCells } from '@utils/utils';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTableState } from '@hooks/useTableState';
import { useProgramContext } from 'src/programContext';
import { headCells } from './IndividualsListTableHeadCells';
import { IndividualsListTableRow } from './IndividualsListTableRow';
import type { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';
import type { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import type { CountResponse } from '@restgenerated/models/CountResponse';

interface IndividualsListTableProps {
  filter;
  businessArea: string;
  canViewDetails: boolean;
  choicesData: IndividualChoices;
}

export function IndividualsListTable({
  businessArea,
  filter,
  canViewDetails,
  choicesData,
}: IndividualsListTableProps): ReactElement {
  const { programId } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const filterVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programCode: programId,
      ageMax: filter.ageMax,
      ageMin: filter.ageMin,
      sex: [filter.sex],
      search: filter.search.trim(),
      documentType: filter.documentType,
      documentNumber: filter.documentNumber.trim(),
      admin2: filter.admin2,
      flags: filter.flags,
      status: filter.status,
      lastRegistrationDateBefore: filter.lastRegistrationDateMin,
      lastRegistrationDateAfter: filter.lastRegistrationDateMax,
      rdiMergeStatus: 'MERGED',
      orderBy: filter.orderBy,
      rdiId: filter.rdiId,
    }),
    [
      filter.ageMin,
      filter.ageMax,
      filter.sex,
      filter.search,
      filter.documentType,
      filter.documentNumber,
      filter.admin2,
      filter.flags,
      filter.status,
      filter.lastRegistrationDateMin,
      filter.lastRegistrationDateMax,
      filter.orderBy,
      programId,
      businessArea,
      filter.rdiId,
    ],
  );
  const table = useTableState({
    rowsPerPageOptions: [10, 15, 20],
    resetPageOn: filterVariables,
  });
  const { page } = table;
  const listVariables = useMemo(
    () => ({ ...filterVariables, ...table.paginationParams }),
    [filterVariables, table.paginationParams],
  );
  const replacements = {
    unicefId: (_beneficiaryGroup) => `${_beneficiaryGroup?.memberLabel} ID`,
    fullName: (_beneficiaryGroup) => _beneficiaryGroup?.memberLabel,
    household__unicef_id: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} ID`,
    relationship: (_beneficiaryGroup) =>
      `Relationship to Head of ${_beneficiaryGroup?.groupLabel}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
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

  // Count should depend only on filters (not pagination). Keep fetching only on page 0.
  const individualsCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    {
      ageMax: filter.ageMax,
      ageMin: filter.ageMin,
      sex: [filter.sex],
      search: filter.search?.trim(),
      documentType: filter.documentType,
      documentNumber: filter.documentNumber?.trim(),
      admin2: filter.admin2,
      flags: filter.flags,
      status: filter.status,
      lastRegistrationDateBefore: filter.lastRegistrationDateMin,
      lastRegistrationDateAfter: filter.lastRegistrationDateMax,
      rdiMergeStatus: 'MERGED',
      orderBy: filter.orderBy,
    },
  );
  const { data: countData } = useQuery<CountResponse>({
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
    <TableWrapper>
      <UniversalRestTable
        title={beneficiaryGroup?.memberLabelPlural}
        headCells={adjustedHeadCells}
        tableState={table}
        data={data}
        error={error}
        isLoading={isLoading}
        isFetching={isFetching}
        allowSort={false}
        itemsCount={itemsCount}
        renderRow={(row: IndividualList) => (
          <IndividualsListTableRow
            key={row.id}
            individual={row}
            canViewDetails={canViewDetails}
            choicesData={choicesData}
          />
        )}
      />
    </TableWrapper>
  );
}
