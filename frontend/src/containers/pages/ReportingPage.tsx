import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingComponent } from '../../components/LoadingComponent';
import { PageHeader } from '../../components/PageHeader';
import { PermissionDenied } from '../../components/PermissionDenied';
import { NewReportForm } from '../../components/Reporting/NewReportForm';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { usePermissions } from '../../hooks/usePermissions';
import { useReportChoiceDataQuery } from '../../__generated__/graphql';
import { ReportingFilters } from '../tables/ReportingTable/ReportingFilters';
import { ReportingTable } from '../tables/ReportingTable/ReportingTable';

export const ReportingPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useReportChoiceDataQuery();

  const [filter, setFilter] = useState({
    type: '',
    createdFrom: undefined,
    createdTo: undefined,
    status: '',
    onlyMy: false,
  });
  const debouncedFilter = useDebounce(filter, 500);
  if (choicesLoading) return <LoadingComponent />;

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.REPORTING_EXPORT, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Reporting')}>
        <NewReportForm />
      </PageHeader>
      <ReportingFilters
        filter={filter}
        onFilterChange={setFilter}
        choicesData={choicesData}
      />
      <ReportingTable
        filter={debouncedFilter}
        businessArea={businessArea}
        choicesData={choicesData}
      />
    </>
  );
};
