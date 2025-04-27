import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells, dateToIsoString } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
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
  const initialQueryVariables = {
    name: filter.name,
    totalHouseholdsCountMin: filter.totalHouseholdsCountMin || null,
    totalHouseholdsCountMax: filter.totalHouseholdsCountMax || null,
    status: filter.status,
    createdAtRange: JSON.stringify({
      min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
      max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
    }),
    businessAreaSlug: businessArea,
    programSlug: programId,
  };

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: targetPopulationsData,
    isLoading,
    error,
  } = useQuery<PaginatedTargetPopulationListList>({
    queryKey: ['businessAreasProgramsTargetPopulationsList', queryVariables],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsList(
        queryVariables,
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
      />
    </TableWrapper>
  );
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    renderTable()
  );
}
