import { Box, Button } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { TargetPopulationQuery } from '../../../__generated__/graphql';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { LoadingButton } from '../../core/LoadingButton';
import { PageHeader } from '../../core/PageHeader';

interface EditTargetPopulationProps {
  handleSubmit: () => Promise<void>;
  values;
  baseUrl: string;
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  loading: boolean;
}

export const EditTargetPopulationHeader = ({
  handleSubmit,
  values,
  baseUrl,
  targetPopulation,
  loading,
}: EditTargetPopulationProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Targeting'),
      to: `/${baseUrl}/target-population/${id}`,
    },
  ];

  const isTitleEditable = (): boolean => targetPopulation.status !== 'LOCKED';

  return (
    <PageHeader
      title={
        isTitleEditable() ? (
          <Field
            name='name'
            label={t('Enter Target Population Name')}
            type='text'
            fullWidth
            required
            component={FormikTextField}
            data-cy='target-population-name'
          />
        ) : (
          values.name
        )
      }
      breadCrumbs={breadCrumbsItems}
      hasInputComponent
    >
      <>
        {values.name && (
          <Box m={2}>
            <Button
              variant='outlined'
              color='primary'
              component={Link}
              data-cy='button-cancel'
              to={`/${baseUrl}/target-population/${targetPopulation.id}`}
            >
              {t('Cancel')}
            </Button>
          </Box>
        )}
        <Box m={2}>
          <LoadingButton
            variant='contained'
            color='primary'
            onClick={handleSubmit}
            loading={loading}
            data-cy='button-save'
            disabled={
              values.targetingCriteria?.length === 0 || !values.name || loading
            }
          >
            {t('Save')}
          </LoadingButton>
        </Box>
      </>
    </PageHeader>
  );
};
