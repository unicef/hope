import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './TargetPopulationPeopleHeadCells';
import { TargetPopulationPeopleTableRow } from './TargetPopulationPeopleRow';
import { useAllPaymentsForTableQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface TargetPopulationHouseholdProps {
  id?: string;
  variables?;
  canViewDetails?: boolean;
}

export function TargetPopulationPeopleTable({
  id,
  variables,
  canViewDetails,
}: TargetPopulationHouseholdProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const initialVariables = {
    businessArea,
    ...(id && { paymentPlanId: id }),
    ...variables,
  };
  return (
    <TableWrapper>
      <UniversalTable
        title={t('People')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllPaymentsForTableQuery}
        queriedObjectName="allPayments"
        initialVariables={initialVariables}
        renderRow={(row) => (
          <TargetPopulationPeopleTableRow
            key={row.id}
            payment={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}
