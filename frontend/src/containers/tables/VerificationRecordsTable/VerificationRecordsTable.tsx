import React, { ReactElement } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './VerificationRecordsHeadCells';
import { VerificationRecordsTableRow } from './VerificationRecordsTableRow';
import {
  useCashPlanQuery,
  CashPlanNode,
  CashPlanQueryVariables,
} from '../../../__generated__/graphql';

// interface VerificationRecordsTableProps {
//   filter;
// }
export function VerificationRecordsTable(): ReactElement {
  const { id } = useParams();

  const initialVariables: CashPlanQueryVariables = {
    id,
  };
  return (
    <UniversalTable<CashPlanNode, CashPlanQueryVariables>
      title='List Of Cash Plans'
      headCells={headCells}
      query={useCashPlanQuery}
      queriedObjectName='cashPlan.'
      initialVariables={initialVariables}
      renderRow={(row) => <VerificationRecordsTableRow key={row.id} />}
    />
  );
}
