import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  hasPermissionInModule,
  PERMISSIONS,
} from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { useDebounce } from '../../../../hooks/useDebounce';
import { usePermissions } from '../../../../hooks/usePermissions';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { SurveysFilters } from '../../../../components/accountability/Surveys/SurveysTable/SurveysFilters';
import { SurveysTable } from '../../../tables/Surveys/SurveysTable/SurveysTable';

export const SurveysPage = (): React.ReactElement => {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { t } = useTranslation();

  const [filter, setFilter] = useState({
    surveyId: '',
    program: '',
    targetPopulation: '',
    createdBy: '',
    createdAtRange: '',
  });

  const debouncedFilter = useDebounce(filter, 500);

  if (permissions === null) return null;
  //TODO: ADD CORRECT PERMISSIONS
  // if (
  //   !hasPermissionInModule(
  //     PERMISSIONS.ACCOUNTABILITY_SURVEYS_VIEW_LIST,
  //     permissions,
  //   )
  // )
  if (
    !hasPermissionInModule(
      PERMISSIONS.ACCOUNTABILITY_FEEDBACK_VIEW_LIST,
      permissions,
    )
  )
    return <PermissionDenied />;
  //TODO: ADD CORRECT PERMISSIONS
  // const canViewDetails = hasPermissionInModule(
  //   PERMISSIONS.ACCOUNTABILITY_SURVEYS_VIEW_DETAILS,
  //   permissions,
  // );
  const canViewDetails = hasPermissionInModule(
    PERMISSIONS.ACCOUNTABILITY_FEEDBACK_VIEW_DETAILS,
    permissions,
  );

  return (
    <>
      <PageHeader title={t('Surveys')}>
        <Button
          variant='contained'
          color='primary'
          component={Link}
          to={`/${businessArea}/accountability/surveys/create`}
          data-cy='button-create-new-survey'
        >
          {t('New Survey')}
        </Button>
      </PageHeader>
      <SurveysFilters filter={filter} onFilterChange={setFilter} />
      <SurveysTable
        filter={debouncedFilter}
        businessArea={businessArea}
        canViewDetails={canViewDetails}
      />
    </>
  );
};
