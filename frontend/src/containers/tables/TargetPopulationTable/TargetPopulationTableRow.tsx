import React from 'react';
import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { TargetPopulationNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';

const StatusContainer = styled.div`
  width: 120px;
`;

interface TargetPopulationTableRowProps {
  targetPopulation: TargetPopulationNode;
}

export function TargetPopulationTableRow({
  targetPopulation,
}: TargetPopulationTableRowProps) {
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
    </ClickableTableRow>
  );
}
