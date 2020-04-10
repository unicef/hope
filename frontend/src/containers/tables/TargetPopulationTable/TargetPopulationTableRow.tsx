import React from 'react';
import styled from 'styled-components';
import Moment from 'react-moment';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { TargetPopulationNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../components/StatusBox';
import { targetPopulationStatusToColor } from '../../../utils/utils';

const StatusContainer = styled.div`
  width: 120px;
`;

interface TargetPopulationTableRowProps {
  targetPopulation: TargetPopulationNode;
}

export function TargetPopulationTableRow({ targetPopulation }) {
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
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>{targetPopulation.candidateListTotalHouseholds}</TableCell>
      <TableCell align='left'>{targetPopulation.finalListTotalHouseholds}</TableCell>
      <TableCell align='left'>
        <Moment format='MM/DD/YYYY'>{targetPopulation.createdAt}</Moment>
      </TableCell>
      <TableCell align='left'>
        <Moment format='MM/DD/YYYY'>{targetPopulation.lastEditedAt}</Moment>
      </TableCell>
      <TableCell align='left'>
        {targetPopulation.createdBy.firstName}{' '}
        {targetPopulation.createdBy.lastName}
      </TableCell>
    </ClickableTableRow>
  );
}
