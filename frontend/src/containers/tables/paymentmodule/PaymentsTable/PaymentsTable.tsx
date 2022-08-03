import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UniversalTable } from '../../UniversalTable';
import {
  AllPaymentsQuery,
  AllPaymentsQueryVariables,
  useAllPaymentsQuery,
} from '../../../../__generated__/graphql';

import { headCells } from './PaymentsTableHeadCells';
import { PaymentsTableRow } from './PaymentsTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface PaymentsTableProps {
  businessArea: string;
  filter: {
    paymentPlanId: string;
  };
  canViewDetails?: boolean;
}

export const PaymentsTable = ({
  businessArea,
  filter,
  canViewDetails = false,
}: PaymentsTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const initialVariables: AllPaymentsQueryVariables = {
    businessArea,
    paymentPlanId: filter.paymentPlanId,
  };

  return (
    <TableWrapper>
      <UniversalTable<
        AllPaymentsQuery['allPayments']['edges'][number]['node'],
        AllPaymentsQueryVariables
      >
        title={t('Payments List')}
        headCells={headCells}
        query={useAllPaymentsQuery}
        queriedObjectName='allPayments'
        initialVariables={initialVariables}
        defaultOrderBy='created_at'
        defaultOrderDirection='desc'
        renderRow={(row) => (
          <PaymentsTableRow
            key={row.id}
            payment={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
