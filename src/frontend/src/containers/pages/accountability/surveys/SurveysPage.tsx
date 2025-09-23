import { CreateSurveyMenu } from '@components/accountability/Surveys/CreateSurveyMenu';
import { SurveysFilters } from '@components/accountability/Surveys/SurveysTable/SurveysFilters';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState, useRef } from 'react';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import {
  hasPermissionInModule,
  PERMISSIONS,
} from '../../../../config/permissions';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { SurveysTable } from '@containers/tables/Surveys/SurveysTable';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { LoadingComponent } from '@components/core/LoadingComponent';

function SurveysPage(): ReactElement {
  const permissions = usePermissions();
  const location = useLocation();
  const { t } = useTranslation();
  const { baseUrl, programId } = useBaseUrl();
  const businessAreaSlug = baseUrl.split('/')[0];

  const { data: categoryChoicesData } = useQuery({
    queryKey: ['surveyCategoryChoices', businessAreaSlug, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsSurveysCategoryChoicesList({
        businessAreaSlug,
        programSlug: programId,
      }),
    enabled: !!businessAreaSlug && !!programId,
  });

  const choicesData = categoryChoicesData || null;

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
  if (
    !hasPermissionInModule(
      PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_LIST,
      permissions,
    )
  )
    return <PermissionDenied />;

  if (!choicesData) {
    return <LoadingComponent />;
  }
  const canViewDetails = hasPermissionInModule(
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
        <SurveysTable
          filter={appliedFilter}
          canViewDetails={canViewDetails}
          choicesData={choicesData}
        />
      </div>
    </>
  );
}
export default withErrorBoundary(SurveysPage, 'SurveysPage');
