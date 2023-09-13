import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import { FollowUpPaymentPlansTable } from '../../tables/paymentmodule/FollowUpPaymentPlansTable';
import { FollowUpPaymentPlansFilters } from '../../tables/paymentmodule/FollowUpPaymentPlansTable/FollowUpPaymentPlansFilters';

const initialFilter = {
  search: '',
  dispersionStartDate: undefined,
  dispersionEndDate: undefined,
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
};

export const FollowUpPaymentPlansPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Payment Module')}>
        {hasPermissions(PERMISSIONS.PM_CREATE, permissions) && (
          <Button
            variant='contained'
            color='primary'
            component={Link}
            to={`/${baseUrl}/payment-module/new-plan`}
            data-cy='button-new-payment-plan'
          >
            {t('NEW PAYMENT PLAN')}
          </Button>
        )}
      </PageHeader>
      <FollowUpPaymentPlansFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <TableWrapper>
        <FollowUpPaymentPlansTable
          filter={appliedFilter}
          title={t('Follow-up Payment Plans')}
          canViewDetails={hasPermissions(
            PERMISSIONS.PM_VIEW_DETAILS,
            permissions,
          )}
        />
      </TableWrapper>
    </>
  );
};
