import styled from 'styled-components';
import { TableCell } from '@material-ui/core';
import { useHistory } from 'react-router-dom';
import React from 'react';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { StatusBox } from '../../../components/StatusBox';
import { Missing } from '../../../components/Missing';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
export const ReportingTableRow = ({ report }) => {
  const businessArea = useBusinessArea();
  const history = useHistory();
  const handleClick = (): void => {
    const path = `/${businessArea}/reporting/${report.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={report.id}
    >
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
        {/* <StatusContainer>
          <StatusBox
            status={paymentRecord.status}
            statusToColor={paymentRecordStatusToColor}
          />
        </StatusContainer> */}
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
    </ClickableTableRow>
  );
};
