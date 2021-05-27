import React from 'react';
import styled from 'styled-components';
import {reduceChoices} from '../../../utils/utils';
import {
  AllReportsQueryVariables,
  ReportChoiceDataQuery,
  ReportNode,
  useAllReportsQuery,
  useMeQuery,
} from '../../../__generated__/graphql';
import {UniversalTable} from '../UniversalTable';
import {headCells} from './ReportingHeadCells';
import {ReportingTableRow} from './ReportingTableRow';

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
  const { data: meData, loading: meLoading } = useMeQuery({
    fetchPolicy: 'cache-first',
  });
  if (meLoading) return null;
  const initialVariables = {
    businessArea,
    createdFrom: filter.createdFrom,
    createdTo: filter.createdTo,
    reportType: filter.type,
    status: filter.status,
    createdBy: filter.onlyMy ? meData.me.id : null,
  };
  const typeChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.reportTypesChoices);
  const statusChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.reportStatusChoices);

  return (
    <TableWrapper>
      <UniversalTable<ReportNode, AllReportsQueryVariables>
        headCells={headCells}
        query={useAllReportsQuery}
        queriedObjectName='allReports'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <ReportingTableRow
            key={row.id}
            report={row}
            typeChoices={typeChoices}
            statusChoices={statusChoices}
          />
        )}
      />
    </TableWrapper>
  );
};
