import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import { ProgramCyclesFilters } from '../../tables/paymentmodule/ProgramCyclesTable/ProgramCyclesFilters';
import { ProgramCyclesTable } from '../../tables/paymentmodule/ProgramCyclesTable/ProgramCyclesTable';

const initialFilter = {
  search: '',
  status: [],
  totalEntitledQuantityFrom: null,
  totalEntitledQuantityTo: null,
};

export const ProgramCyclesPage = (): React.ReactElement => {
  const { t } = useTranslation();
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
      <PageHeader title={t('Payment Module')} />
      <ProgramCyclesFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <TableWrapper>
        <ProgramCyclesTable filter={appliedFilter} />
      </TableWrapper>
    </>
  );
};
