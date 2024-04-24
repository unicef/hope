import { Box, Button } from '@mui/material';
import { Field } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { TargetPopulationQuery } from '@generated/graphql';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { LoadingButton } from '@core/LoadingButton';
import { PageHeader } from '@core/PageHeader';

interface EditTargetPopulationProps {
  handleSubmit: () => Promise<void>;
  values;
  baseUrl: string;
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  loading: boolean;
  category: string;
}

export const EditTargetPopulationHeader = ({
  handleSubmit,
  values,
  baseUrl,
  targetPopulation,
  loading,
  category,
}: EditTargetPopulationProps): React.ReactElement => {
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
            disabled={isSubmitDisabled()}
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
