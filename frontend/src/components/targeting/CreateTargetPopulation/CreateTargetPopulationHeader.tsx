import { Box, Button } from '@mui/material';
import * as React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { LoadingButton } from '@core/LoadingButton';
import { PageHeader } from '@core/PageHeader';

interface CreateTargetPopulationHeaderProps {
  handleSubmit: () => Promise<void>;
  values;
  baseUrl: string;
  permissions: string[];
  loading: boolean;
  category: string;
}

export const CreateTargetPopulationHeader = ({
  handleSubmit,
  values,
  baseUrl,
  permissions,
  loading,
  category,
}: CreateTargetPopulationHeaderProps): React.ReactElement => {
  const { t } = useTranslation();

  const isSubmitDisabled = () => {
    if (category === 'filters') {
      return values.criterias?.length === 0 || !values.name || loading;
    }
    if (category === 'ids') {
      return (
        !(values.individualIds || values.householdIds) ||
        !values.name ||
        loading
      );
    }
    return true;
  };

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Targeting'),
      to: `/${baseUrl}/target-population/`,
    },
  ];

  return (
    <PageHeader
      title={t('New Target Population')}
      breadCrumbs={
        hasPermissions(PERMISSIONS.TARGETING_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <>
        <Box m={2}>
          <Button component={Link} to={`/${baseUrl}/target-population`}>
            {t('Cancel')}
          </Button>
        </Box>
        <Box m={2}>
          <LoadingButton
            variant="contained"
            color="primary"
            onClick={handleSubmit}
            disabled={isSubmitDisabled()}
            loading={loading}
            data-cy="button-target-population-create"
          >
            {t('Save')}
          </LoadingButton>
        </Box>
      </>
    </PageHeader>
  );
};
