import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import { PaymentPlansTable } from '../../tables/paymentmodule/PaymentPlansTable';
import { PaymentPlansFilters } from '../../tables/paymentmodule/PaymentPlansTable/PaymentPlansFilters';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import {ProgramStatus, useProgramQuery} from "../../../__generated__/graphql";
import {LoadingComponent} from "../../../components/core/LoadingComponent";
import { ButtonTooltip } from '../../../components/core/ButtonTooltip';

const initialFilter = {
  search: '',
  dispersionStartDate: '',
  dispersionEndDate: '',
  status: [],
  totalEntitledQuantityFrom: '',
  totalEntitledQuantityTo: '',
  isFollowUp: null,
  program: null,
};

export const PaymentModulePage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl, programId } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const { data, loading: programLoading } = useProgramQuery({
    variables: { id: programId },
    fetchPolicy: 'cache-and-network',
  });

  if (permissions === null || !data) return null
  if (programLoading) {
    return <LoadingComponent/>
  }

  if (!hasPermissions(PERMISSIONS.PM_VIEW_LIST, permissions))
    return <PermissionDenied />;

  const isImportDisabled = data?.program?.status !== ProgramStatus.Active

  return (
    <>
      <PageHeader title={t('Payment Module')}>
        {hasPermissions(PERMISSIONS.PM_CREATE, permissions) && (
            <ButtonTooltip
              title={t('Program must be ACTIVE to create Payment Plan')}
              variant='contained'
              color='primary'
              component={Link}
              to={`/${baseUrl}/payment-module/new-plan`}
              data-cy='button-new-payment-plan'
              disabled={isImportDisabled}
            >
              {t('NEW PAYMENT PLAN')}
            </ButtonTooltip>
        )}
      </PageHeader>
      <PaymentPlansFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <TableWrapper>
        <PaymentPlansTable
          filter={appliedFilter}
          canViewDetails={hasPermissions(
            PERMISSIONS.PM_VIEW_DETAILS,
            permissions,
          )}
        />
      </TableWrapper>
    </>
  );
};
