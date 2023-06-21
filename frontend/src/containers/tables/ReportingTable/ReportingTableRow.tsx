import { TableCell, TableRow } from '@material-ui/core';
import { GetApp } from '@material-ui/icons';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { Pointer } from '../../../components/core/Pointer';
import { StatusBox } from '../../../components/core/StatusBox';
import { UniversalMoment } from '../../../components/core/UniversalMoment';
import { formatNumber, reportStatusToColor } from '../../../utils/utils';
import { ReportNode } from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

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
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const history = useHistory();
  const handleClick = (): void => {
    const path = `/${baseUrl}/reporting/${report.id}`;
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
        <StatusBox
          status={statusChoices[report.status]}
          statusToColor={reportStatusToColor}
        />
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
            {t('DOWNLOAD')}
          </Pointer>
        )}
      </DownloadTableCell>
    </TableRow>
  );
};
