import { Box, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { LoadingButton } from '@core/LoadingButton';
import { PageHeader } from '@core/PageHeader';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface CreateTargetPopulationHeaderProps {
  handleSubmit: () => Promise<void>;
  values;
  baseUrl: string;
  permissions: string[];
  loading: boolean;
}

const CreateTargetPopulationHeader = ({
  handleSubmit,
  values,
  baseUrl,
  permissions,
  loading,
}: CreateTargetPopulationHeaderProps): ReactElement => {
  const { t } = useTranslation();

  const isSubmitDisabled = (criterias) => {
    return criterias?.some((criteria) => {
      const householdsFiltersBlocks = criteria.householdsFiltersBlocks || [];
      const individualsFiltersBlocks = criteria.individualsFiltersBlocks || [];
      const collectorsFiltersBlocks = criteria.collectorsFiltersBlocks || [];
      const individualIds = criteria.individualIds || [];
      const householdIds = criteria.householdIds || [];

      return (
        householdsFiltersBlocks.length === 0 &&
        individualsFiltersBlocks.length === 0 &&
        collectorsFiltersBlocks.length === 0 &&
        individualIds.length === 0 &&
        householdIds.length === 0
      );
    });
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
          <Button
            data-cy="button-cancel"
            component={Link}
            to={`/${baseUrl}/target-population`}
          >
            {t('Cancel')}
          </Button>
        </Box>
        <Box m={2}>
          <LoadingButton
            variant="contained"
            color="primary"
            onClick={handleSubmit}
            disabled={isSubmitDisabled(values.criterias)}
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

export default withErrorBoundary(
  CreateTargetPopulationHeader,
  'CreateTargetPopulationHeader',
);
