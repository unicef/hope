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
import { adjustHeadCells, dateToIsoString } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useProgramContext } from 'src/programContext';
import { headCells } from './IndividualsListTableHeadCells';
import { IndividualsListTableRow } from './IndividualsListTableRow';

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
      age: JSON.stringify({ min: filter.ageMin, max: filter.ageMax }),
      businessArea,
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
      program: programId,
      rdiMergeStatus: IndividualRdiMergeStatus.Merged,
    }),
    [businessArea, filter, programId],
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

  const { data, isLoading, error } = useQuery({
    queryKey: [
      'businessAreasProgramsHouseholdsList',
      queryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsList({
        businessAreaSlug: businessArea,
        programSlug: programId,
        ...queryVariables,
      }),
    enabled: !!businessArea && !!programId,
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
