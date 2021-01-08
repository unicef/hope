import styled from 'styled-components';
import { TableCell } from '@material-ui/core';
import { useHistory } from 'react-router-dom';
import React from 'react';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { StatusBox } from '../../../components/StatusBox';
import { Missing } from '../../../components/Missing';
import { UniversalMoment } from '../../../components/UniversalMoment';
import { reportStatusToColor } from '../../../utils/utils';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
const UnderlinedTableCell = styled(TableCell)`
  text-decoration: underline;
`;
export const ReportingTableRow = ({ report, typeChoices, statusChoices }) => {
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
      <UnderlinedTableCell align='left'>
        {typeChoices[report.reportType]}
      </UnderlinedTableCell>
      <TableCell align='left'>
        <UniversalMoment>{report.dateFrom}</UniversalMoment> -{' '}
        <UniversalMoment>{report.dateTo}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={statusChoices[report.status]}
            statusToColor={reportStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{report.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        {report.createdBy.firstName} {report.createdBy.lastName}
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
    </ClickableTableRow>
  );
};
