import React from 'react';
import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { TargetPopulationNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../components/StatusBox';
import {
  targetPopulationStatusToColor,
  targetPopulationStatusMapping,
} from '../../../utils/utils';
import { UniversalMoment } from '../../../components/UniversalMoment';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface TargetPopulationTableRowProps {
  targetPopulation: TargetPopulationNode;
}

export function TargetPopulationTableRow({
  targetPopulation,
}): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/target-population/${targetPopulation.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={targetPopulation.id}
    >
      <TableCell align='left'>{targetPopulation.name}</TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={targetPopulation.status}
            statusToColor={targetPopulationStatusToColor}
            statusNameMapping={targetPopulationStatusMapping}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>
        {targetPopulation.program?.name || '-'}
      </TableCell>
      <TableCell align='left'>
        {targetPopulation.finalListTotalHouseholds || '-'}
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{targetPopulation.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{targetPopulation.lastEditedAt}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        {targetPopulation.createdBy.firstName}{' '}
        {targetPopulation.createdBy.lastName}
      </TableCell>
    </ClickableTableRow>
  );
}
