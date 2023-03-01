import { Box } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { LoadingButton } from '../../core/LoadingButton';
import { PageHeader } from '../../core/PageHeader';

interface CreateTargetPopulationHeaderProps {
  handleSubmit: () => Promise<void>;
  values;
  businessArea: string;
  permissions: string[];
  loading: boolean;
}

export function CreateTargetPopulationHeader({
  handleSubmit,
  values,
  businessArea,
  permissions,
  loading,
}: CreateTargetPopulationHeaderProps): React.ReactElement {
  const { t } = useTranslation();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Targeting'),
      to: `/${businessArea}/target-population/`,
    },
  ];

  return (
    <PageHeader
      title={
        <Field
          name='name'
          label={t('Enter Target Population Name')}
          type='text'
          fullWidth
          required
          component={FormikTextField}
          data-cy='input-name'
        />
      }
      breadCrumbs={
        hasPermissions(PERMISSIONS.TARGETING_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
      hasInputComponent
    >
      <>
        <Box m={2}>
          <LoadingButton
            variant='contained'
            color='primary'
            onClick={handleSubmit}
            disabled={values.criterias?.length === 0 || !values.name || loading}
            loading={loading}
            data-cy='button-target-population-create'
          >
            {t('Save')}
          </LoadingButton>
        </Box>
      </>
    </PageHeader>
  );
}
