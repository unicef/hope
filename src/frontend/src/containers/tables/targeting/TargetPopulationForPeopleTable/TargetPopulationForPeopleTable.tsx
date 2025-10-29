import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { createApiParams } from '@utils/apiUtils';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells, dateToIsoString } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { headCells } from './TargetPopulationForPeopleTableHeadCells';
import { TargetPopulationForPeopleTableRow } from './TargetPopulationForPeopleTableRow';
import { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';
import { usePersistedCount } from '@hooks/usePersistedCount';

interface TargetPopulationProps {
  filter;
  canViewDetails: boolean;
  enableRadioButton?: boolean;
  selectedTargetPopulation?;
  handleChange?;
  noTableStyling?;
  noTitle?;
}

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

export function TargetPopulationForPeopleTable({
  filter,
  canViewDetails,
  enableRadioButton,
  selectedTargetPopulation,
  handleChange,
  noTableStyling,
  noTitle,
}: TargetPopulationProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const { businessArea, programId } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programSlug: programId,
      name: filter.name,
      totalHouseholdsCountMin: filter.totalHouseholdsCountMin || null,
      totalHouseholdsCountMax: filter.totalHouseholdsCountMax || null,
      status: filter.status,
      businessArea,
      program: programId,
      createdAtRange: JSON.stringify({
        min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
        max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
      }),
    }),
    [
      businessArea,
      programId,
      filter.name,
      filter.totalHouseholdsCountMin,
      filter.totalHouseholdsCountMax,
      filter.status,
      filter.createdAtRangeMin,
      filter.createdAtRangeMax,
    ],
  );

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  // Controlled pagination state
  const [page, setPage] = useState(0);

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  // Count query (enabled only on page 0)
  const { data: countData } = useQuery({
    queryKey: [
      'businessAreasProgramsTargetPopulationsCount',
      queryVariables,
      businessArea,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsCountRetrieve(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
        ),
      ),
    enabled: page === 0,
  });

  const persistedCount = usePersistedCount(page, countData);

  // Main data query
  const {
    data: targetPopulationsData,
    isLoading,
    error: targetPopulationsError,
  } = useQuery<PaginatedTargetPopulationListList>({
    queryKey: [
      'businessAreasProgramsTargetPopulationsList',
      queryVariables,
      businessArea,
      programId,
      page,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          { ...queryVariables, offset: page * 10 },
          { withPagination: true },
        ),
      );
    },
  });

  const replacements = {
    total_households_count: (_beneficiaryGroup) =>
      `Num. of ${_beneficiaryGroup?.groupLabelPlural}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  const renderTable = (): ReactElement => (
    <TableWrapper>
      <UniversalRestTable
        title={noTitle ? null : t('Target Populations')}
        headCells={
          enableRadioButton ? adjustedHeadCells : adjustedHeadCells.slice(1)
        }
        rowsPerPageOptions={[10, 15, 20]}
        defaultOrderBy="createdAt"
        defaultOrderDirection="desc"
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        data={targetPopulationsData}
        isLoading={isLoading}
        error={targetPopulationsError}
        renderRow={(row: TargetPopulationList) => (
          <TargetPopulationForPeopleTableRow
            radioChangeHandler={enableRadioButton && handleRadioChange}
            selectedTargetPopulation={selectedTargetPopulation}
            key={row.id}
            targetPopulation={row}
            canViewDetails={canViewDetails}
          />
        )}
        page={page}
        setPage={setPage}
        itemsCount={persistedCount}
      />
    </TableWrapper>
  );
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    renderTable()
  );
}
