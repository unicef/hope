import styled from 'styled-components';
import {TableCell, TableRow} from '@material-ui/core';
import {GetApp} from '@material-ui/icons';
import {useHistory} from 'react-router-dom';
import React from 'react';
import {useBusinessArea} from '../../../hooks/useBusinessArea';
import {StatusBox} from '../../../components/StatusBox';
import {UniversalMoment} from '../../../components/UniversalMoment';
import {formatNumber, reportStatusToColor} from '../../../utils/utils';
import {ReportNode} from '../../../__generated__/graphql';
import {Pointer} from '../../../components/Pointer';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
const UnderlinedTableCell = styled(TableCell)`
  text-decoration: underline;
`;
const DownloadTableCell = styled(TableCell)`
  span {
    color: #9f9f9f;
    font-weight: 500;
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
    <TableRow hover role='checkbox' key={report.id}>
      <UnderlinedTableCell onClick={handleClick} align='left'>
        <Pointer>{typeChoices[report.reportType]}</Pointer>
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
      <TableCell align='right'>
        {formatNumber(report.numberOfRecords)}
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
          <Pointer>
            <GetApp />
            DOWNLOAD
          </Pointer>
        )}
      </DownloadTableCell>
    </TableRow>
  );
};
