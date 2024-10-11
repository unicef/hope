import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useMeQuery, useReportChoiceDataQuery } from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { NewReportForm } from '@components/reporting/NewReportForm';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReportingFilters } from '../../tables/ReportingTable/ReportingFilters';
import { ReportingTable } from '../../tables/ReportingTable/ReportingTable';
import { useBaseUrl } from '@hooks/useBaseUrl';

const initialFilter = {
  type: '',
  createdFrom: '',
  createdTo: '',
  status: '',
  onlyMy: false,
};

export function ReportingPage(): React.ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();

  const { data: choicesData, loading: choicesLoading } =
    useReportChoiceDataQuery();

  const { data: meData, loading: meLoading } = useMeQuery({
    fetchPolicy: 'cache-first',
  });

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  if (choicesLoading || meLoading) return <LoadingComponent />;

  if (!choicesData || !meData || permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.REPORTING_EXPORT, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Reporting')}>
        <NewReportForm />
      </PageHeader>
      <ReportingFilters
        filter={filter}
        choicesData={choicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <ReportingTable
        filter={appliedFilter}
        businessArea={businessArea}
        choicesData={choicesData}
        meData={meData}
      />
    </>
  );
}
