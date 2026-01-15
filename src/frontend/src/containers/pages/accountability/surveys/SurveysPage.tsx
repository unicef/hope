import { CreateSurveyMenu } from '@components/accountability/Surveys/CreateSurveyMenu';
import { SurveysFilters } from '@components/accountability/Surveys/SurveysTable/SurveysFilters';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { SurveysTable } from '@containers/tables/Surveys/SurveysTable';
import { usePermissions } from '@hooks/usePermissions';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';

function SurveysPage(): ReactElement {
  const permissions = usePermissions();
  const location = useLocation();
  const { t } = useTranslation();

  const initialFilter = {
    search: '',
    targetPopulation: '',
    createdBy: '',
    createdAtRangeMin: '',
    createdAtRangeMax: '',
  };

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [shouldScroll, setShouldScroll] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  useScrollToRefOnChange(tableRef, shouldScroll, appliedFilter, () =>
    setShouldScroll(false),
  );

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_LIST, permissions))
    return (
      <PermissionDenied
        permission={PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_LIST}
      />
    );

  const canViewDetails = hasPermissions(
    PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_DETAILS,
    permissions,
  );

  return (
    <>
      <PageHeader title={t('Surveys')}>
        <CreateSurveyMenu />
      </PageHeader>
      <SurveysFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={(f) => {
          setAppliedFilter(f);
          setShouldScroll(true);
        }}
      />
      <div ref={tableRef}>
        <SurveysTable filter={appliedFilter} canViewDetails={canViewDetails} />
      </div>
    </>
  );
}
export default withErrorBoundary(SurveysPage, 'SurveysPage');
