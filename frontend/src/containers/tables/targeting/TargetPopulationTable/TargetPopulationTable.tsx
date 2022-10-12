import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TableWrapper } from '../../../../components/core/TableWrapper';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { decodeIdString } from '../../../../utils/utils';
import {
  AllTargetPopulationsQueryVariables,
  TargetPopulationNode,
  useAllTargetPopulationsQuery,
} from '../../../../__generated__/graphql';
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
}

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

export const TargetPopulationTable = ({
  filter,
  canViewDetails,
  enableRadioButton,
  selectedTargetPopulation,
  handleChange,
  noTableStyling,
}: TargetPopulationProps): ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const initialVariables: AllTargetPopulationsQueryVariables = {
    name: filter.name,
    numberOfHouseholdsMin: filter.numIndividuals.min,
    numberOfHouseholdsMax: filter.numIndividuals.max,
    status: filter.status,
    businessArea,
  };

  const handleRadioChange = (id: string): void => {
    handleChange(id);
  };

  if (filter.program) {
    if (Array.isArray(filter.program)) {
      initialVariables.program = filter.program.map((programId) =>
        decodeIdString(programId),
      );
    } else {
      initialVariables.program = [decodeIdString(filter.program)];
    }
  }

  const renderTable = (): React.ReactElement => {
    return (
      <TableWrapper>
        <UniversalTable<
          TargetPopulationNode,
          AllTargetPopulationsQueryVariables
        >
          title={t('Target Populations')}
          headCells={enableRadioButton ? headCells : headCells.slice(1)}
          rowsPerPageOptions={[10, 15, 20]}
          query={useAllTargetPopulationsQuery}
          queriedObjectName='allTargetPopulation'
          defaultOrderBy='createdAt'
          defaultOrderDirection='desc'
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
  };
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    <TableWrapper>{renderTable()}</TableWrapper>
  );
};
