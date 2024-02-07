import * as React from 'react';
import { TableWrapper } from '@components/core/TableWrapper';
import { choicesToDict, dateToIsoString } from '@utils/utils';
import {
  AllReportsQueryVariables,
  MeQuery,
  ReportChoiceDataQuery,
  ReportNode,
  useAllReportsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './ReportingHeadCells';
import { ReportingTableRow } from './ReportingTableRow';

interface ReportingTableProps {
  businessArea: string;
  filter;
  choicesData: ReportChoiceDataQuery;
  meData: MeQuery;
}
export function ReportingTable({
  businessArea,
  filter,
  choicesData,
  meData,
}: ReportingTableProps): React.ReactElement {
  const initialVariables = {
    businessArea,
    createdFrom: dateToIsoString(filter.createdFrom, 'startOfDay'),
    createdTo: dateToIsoString(filter.createdTo, 'endOfDay'),
    reportType: filter.type,
    status: filter.status,
    createdBy: filter.onlyMy ? meData.me.id : null,
  };
  const typeChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.reportTypesChoices);
  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.reportStatusChoices);

  return (
    <TableWrapper>
      <UniversalTable<ReportNode, AllReportsQueryVariables>
        headCells={headCells}
        query={useAllReportsQuery}
        queriedObjectName="allReports"
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
}
