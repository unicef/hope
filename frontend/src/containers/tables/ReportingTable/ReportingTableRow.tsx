import styled from 'styled-components';
import { TableCell } from '@material-ui/core';
import { GetApp } from '@material-ui/icons';
import { useHistory } from 'react-router-dom';
import React from 'react';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { StatusBox } from '../../../components/StatusBox';
import { UniversalMoment } from '../../../components/UniversalMoment';
import { reportStatusToColor } from '../../../utils/utils';
import { ReportNode } from '../../../__generated__/graphql';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
const UnderlinedTableCell = styled(TableCell)`
  text-decoration: underline;
`;
const DownloadTableCell = styled(TableCell)`
  span {
    display: flex;
    justify-content: center;
  }
`;
interface ReportingTableRowProps {
  report: ReportNode;
  statusChoices: { [id: number]: string };
  typeChoices: { [id: number]: string };
}
export const ReportingTableRow = ({
  report,
  typeChoices,
  statusChoices,
}: ReportingTableRowProps): React.ReactElement => {
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
      <DownloadTableCell
        align='left'
        onClick={report.fileUrl ? () => window.open(report.fileUrl) : undefined}
      >
        {report.fileUrl && (
          <span>
            <GetApp />
            DOWNLOAD
          </span>
        )}
      </DownloadTableCell>
    </ClickableTableRow>
  );
};
