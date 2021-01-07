import React from 'react';
import styled from 'styled-components';
import {
  ReportChoiceDataQuery,
  ReportNode,
  AllReportsQueryVariables,
  useAllReportsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './ReportingHeadCells';
import { ReportingTableRow } from './ReportingTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;
interface ReportingTableProps {
  businessArea: string;
  filter;
  choicesData: ReportChoiceDataQuery;
}
export const ReportingTable = ({
  businessArea,
  filter,
  choicesData,
}: ReportingTableProps): React.ReactElement => {
  const initialVariables = {
    businessArea,
    createdFrom: filter.createdFrom,
    createdTo: filter.createdTo,
    reportType: filter.type,
    status: filter.status,
  };
  return (
    <TableWrapper>
      <UniversalTable<ReportNode, AllReportsQueryVariables>
        // title='Repor'
        headCells={headCells}
        query={useAllReportsQuery}
        queriedObjectName='allReports'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <ReportingTableRow
            key={row.id}
            report={row}
            // choicesData={choicesData}
          />
        )}
      />
    </TableWrapper>
  );
};
