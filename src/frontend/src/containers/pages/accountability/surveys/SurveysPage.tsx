import { CreateSurveyMenu } from '@components/accountability/Surveys/CreateSurveyMenu';
import { SurveysFilters } from '@components/accountability/Surveys/SurveysTable/SurveysFilters';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState } from 'react';
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
      RestService.restBusinessAreasProgramsSurveysCategoryChoicesRetrieve({
        businessAreaSlug,
        programSlug: programId,
      }),
    enabled: !!businessAreaSlug && !!programId,
  });

  // Since we've migrated to REST, we can directly use the categoryChoicesData
  // without adapting it to match the GraphQL format
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
        setAppliedFilter={setAppliedFilter}
      />
      <SurveysTable
        filter={appliedFilter}
        canViewDetails={canViewDetails}
        choicesData={choicesData}
      />
    </>
  );
}
export default withErrorBoundary(SurveysPage, 'SurveysPage');
