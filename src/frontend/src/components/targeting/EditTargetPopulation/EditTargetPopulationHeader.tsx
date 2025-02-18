import { Box, Button } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { PaymentPlanQuery } from '@generated/graphql';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { LoadingButton } from '@core/LoadingButton';
import { PageHeader } from '@core/PageHeader';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface EditTargetPopulationProps {
  handleSubmit: () => Promise<void>;
  values;
  baseUrl: string;
  targetPopulation: PaymentPlanQuery['paymentPlan'];
  loading: boolean;
}

const EditTargetPopulationHeader = ({
  handleSubmit,
  values,
  baseUrl,
  targetPopulation,
  loading,
}: EditTargetPopulationProps): ReactElement => {
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

  const { id } = useParams();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Targeting'),
      to: `/${baseUrl}/target-population/${id}`,
    },
  ];

  return (
    <PageHeader
      title={t('Edit Target Population')}
      breadCrumbs={breadCrumbsItems}
      hasInputComponent
    >
      <>
        <Box m={2}>
          <Button
            variant="outlined"
            color="primary"
            component={Link}
            data-cy="button-cancel"
            to={`/${baseUrl}/target-population/${targetPopulation.id}`}
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
            data-cy="button-save"
          >
            {t('Save')}
          </LoadingButton>
        </Box>
      </>
    </PageHeader>
  );
};

export default withErrorBoundary(
  EditTargetPopulationHeader,
  'EditTargetPopulationHeader',
);
