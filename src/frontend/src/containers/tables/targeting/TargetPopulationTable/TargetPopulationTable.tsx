import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { createApiParams } from '@utils/apiUtils';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { headCells } from './TargetPopulationTableHeadCells';
import { TargetPopulationTableRow } from './TargetPopulationTableRow';

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

export function TargetPopulationTable({
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
      name: filter.name,
      status: filter.status,
      totalHouseholdsCountGte: filter.totalHouseholdsCountGte,
      totalHouseholdsCountLte: filter.totalHouseholdsCountLte,
      createdAtGte: filter.createdAtGte,
      createdAtLte: filter.createdAtLte,
    }),
    [
      filter.name,
      filter.status,
      filter.totalHouseholdsCountGte,
      filter.totalHouseholdsCountLte,
      filter.createdAtGte,
      filter.createdAtLte,
    ],
  );

  // Controlled pagination state
  const [page, setPage] = useState(0);

  // Persisted count state
  const [persistedCount, setPersistedCount] = useState<number | undefined>(
    undefined,
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  // Count query (enabled only on page 0)
  const { data: countData } = useQuery({
    queryKey: [
      'businessAreasProgramsTargetPopulationsCount',
      businessArea,
      programId,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsCountRetrieve(
        createApiParams(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
          },
          queryVariables,
        ),
      ),
    enabled: page === 0,
  });

  // Persist count on page 0
  useEffect(() => {
    if (page === 0 && countData?.count !== undefined) {
      setPersistedCount(countData.count);
    }
  }, [page, countData]);

  // Main data query
  const {
    data: targetPopulationsData,
    isLoading,
    error,
  } = useQuery<PaginatedTargetPopulationListList>({
    queryKey: [
      'businessAreasProgramsTargetPopulationsList',
      businessArea,
      programId,
      queryVariables,
      page,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsList(
        createApiParams(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
          },
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

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
        error={error}
        renderRow={(row: TargetPopulationList) => (
          <TargetPopulationTableRow
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
