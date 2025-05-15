import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import {
  HouseholdChoiceDataQuery,
  IndividualRdiMergeStatus,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { IndividualList } from '@restgenerated/models/IndividualList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { adjustHeadCells, dateToIsoString } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useProgramContext } from 'src/programContext';
import { headCells } from './IndividualsListTableHeadCells';
import { IndividualsListTableRow } from './IndividualsListTableRow';
import { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';

interface IndividualsListTableProps {
  filter;
  businessArea: string;
  canViewDetails: boolean;
  choicesData: HouseholdChoiceDataQuery;
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

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programSlug: programId,
      age: JSON.stringify({ min: filter.ageMin, max: filter.ageMax }),
      sex: [filter.sex],
      search: filter.search.trim(),
      documentType: filter.documentType,
      documentNumber: filter.documentNumber.trim(),
      admin2: filter.admin2,
      flags: filter.flags,
      status: filter.status,
      lastRegistrationDate: JSON.stringify({
        min: dateToIsoString(filter.lastRegistrationDateMin, 'startOfDay'),
        max: dateToIsoString(filter.lastRegistrationDateMax, 'endOfDay'),
      }),
      rdiMergeStatus: IndividualRdiMergeStatus.Merged,
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
      programId,
      businessArea,
    ],
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
    <TableWrapper>
      <UniversalRestTable
        title={beneficiaryGroup?.memberLabelPlural}
        headCells={adjustedHeadCells}
        rowsPerPageOptions={[10, 15, 20]}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        data={data}
        error={error}
        isLoading={isLoading}
        allowSort={false}
        filterOrderBy={filter.orderBy}
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
