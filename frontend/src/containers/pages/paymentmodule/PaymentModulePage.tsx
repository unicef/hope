import { Box, Button } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { PaymentPlansTable } from '../../tables/paymentmodule/PaymentPlansTable';
import { PaymentPlansFilters, FilterProps } from '../../tables/paymentmodule/PaymentPlansTable/PaymentPlansFilters';

export function PaymentModulePage(): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const [planfilter, setPlanFilter] = useState<FilterProps>({
    search: '',
    dispersionDate: '',
    status: '',
    entitlement: { min: null, max: null },
  });

  const debouncedPlanFilter = useDebounce(planfilter, 500);

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PAYMENT_MODULE_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Payment Module')}>
        {hasPermissions(PERMISSIONS.PAYMENT_MODULE_CREATE, permissions) && (
          <Button
            variant='contained'
            color='primary'
            component={Link}
            to={`/${businessArea}/payment-module/new-plan`}
          >
            {t('NEW PAYMENT PLAN')}
          </Button>
        )}
      </PageHeader>
      <PaymentPlansFilters filter={planfilter} onFilterChange={setPlanFilter} />

      <TableWrapper>
        <PaymentPlansTable
          filter={debouncedPlanFilter}
          businessArea={businessArea}
          canViewDetails={hasPermissions(
            PERMISSIONS.PAYMENT_MODULE_VIEW_DETAILS,
            permissions,
          )}
        />
      </TableWrapper>
    </>
  );
}
