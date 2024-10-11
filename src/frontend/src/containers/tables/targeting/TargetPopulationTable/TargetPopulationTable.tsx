import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllTargetPopulationsQueryVariables,
  TargetPopulationNode,
  useAllTargetPopulationsQuery,
} from '@generated/graphql';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { dateToIsoString } from '@utils/utils';
import { UniversalTable } from '../../UniversalTable';
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
  const { businessArea, programId } = useBaseUrl();
  const initialVariables: AllTargetPopulationsQueryVariables = {
    name: filter.name,
    totalHouseholdsCountMin: filter.totalHouseholdsCountMin || null,
    totalHouseholdsCountMax: filter.totalHouseholdsCountMax || null,
    status: filter.status,
    businessArea,
    program: [programId],
    createdAtRange: JSON.stringify({
      min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
      max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
    }),
  };
  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  const renderTable = (): React.ReactElement => (
    <TableWrapper>
      <UniversalTable<TargetPopulationNode, AllTargetPopulationsQueryVariables>
        title={noTitle ? null : t('Target Populations')}
        headCells={enableRadioButton ? headCells : headCells.slice(1)}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllTargetPopulationsQuery}
        queriedObjectName="allTargetPopulation"
        defaultOrderBy="createdAt"
        defaultOrderDirection="desc"
        initialVariables={initialVariables}
        renderRow={(row) => (
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
