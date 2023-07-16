import React from 'react';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '../../../../components/core/TableWrapper';
import {
  RecipientNode,
  RecipientsQueryVariables,
  useRecipientsQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './RecipientsTableHeadCells';
import { RecipientsTableRow } from './RecipientsTableRow';

interface RecipientsTableProps {
  id: string;
  canViewDetails: boolean;
}

export const RecipientsTable = ({
  id,
  canViewDetails,
}: RecipientsTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const initialVariables: RecipientsQueryVariables = {
    survey: id,
  };

  return (
    <TableWrapper>
      <UniversalTable<RecipientNode, RecipientsQueryVariables>
        title={t('Recipients')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useRecipientsQuery}
        queriedObjectName='recipients'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <RecipientsTableRow
            key={row.id}
            household={row.headOfHousehold.household}
            headOfHousehold={row.headOfHousehold}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
