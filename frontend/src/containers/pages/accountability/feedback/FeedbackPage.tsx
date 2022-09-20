import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { hasPermissionInModule } from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { useDebounce } from '../../../../hooks/useDebounce';
import { usePermissions } from '../../../../hooks/usePermissions';
import { useGrievancesChoiceDataQuery } from '../../../../__generated__/graphql';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { FeedbackFilters } from '../../../../components/accountability/Feedback/FeedbackTable/FeedbackFilters';
import { FeedbackTable } from '../../../tables/Feedback/FeedbackTable';

export const FeedbackPage = (): React.ReactElement => {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { t } = useTranslation();

  const [filter, setFilter] = useState({
    search: '',
    status: '',
    createdBy: '',
    createdAtRange: '',
  });

  const debouncedFilter = useDebounce(filter, 500);
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  if (choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissionInModule('GRIEVANCES_VIEW_LIST', permissions))
    return <PermissionDenied />;
  if (!choicesData) return null;

  return (
    <>
      <PageHeader title={t('Feedback')}>
        <Button
          variant='contained'
          color='primary'
          component={Link}
          to={`/${businessArea}/accountability/feedback/create`}
          data-cy='button-submit-new-feedback'
        >
          {t('Submit New Feedback')}
        </Button>
      </PageHeader>
      <FeedbackFilters filter={filter} onFilterChange={setFilter} />
      <FeedbackTable filter={debouncedFilter} businessArea={businessArea} />
    </>
  );
};
