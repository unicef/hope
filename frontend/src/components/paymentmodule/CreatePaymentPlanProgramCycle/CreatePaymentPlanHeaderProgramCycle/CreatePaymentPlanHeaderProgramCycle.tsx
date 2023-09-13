import { Box, Button } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ProgramCycleQuery } from '../../../../__generated__/graphql';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { LoadingButton } from '../../../core/LoadingButton';
import { PageHeader } from '../../../core/PageHeader';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';

interface CreatePaymentPlanHeaderProgramCycleProps {
  handleSubmit: () => Promise<void>;
  baseUrl: string;
  permissions: string[];
  loadingCreate: boolean;
  programCycle: ProgramCycleQuery['programCycle'];
}

export const CreatePaymentPlanHeaderProgramCycle = ({
  handleSubmit,
  baseUrl,
  permissions,
  loadingCreate,
  programCycle,
}: CreatePaymentPlanHeaderProgramCycleProps): React.ReactElement => {
  const { t } = useTranslation();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/program-cycles/`,
    },
    {
      title: `${programCycle.name} (ID: ${programCycle.unicefId})`,
      to: `/${baseUrl}/payment-module/program-cycles/${programCycle.id}`,
    },
  ];

  return (
    <PageHeader
      title={
        <Field
          name='name'
          label={t('Payment Plan Title')}
          fullWidth
          required
          component={FormikTextField}
        />
      }
      hasInputComponent
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_PROGRAMME_CYCLE_VIEW_DETAILS, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <Box display='flex' mt={2} mb={2}>
        <Box mr={3}>
          <Button
            component={Link}
            to={`/${baseUrl}/payment-module/program-cycles/${programCycle.id}`}
            data-cy='button-cancel-payment-plan'
          >
            {t('Cancel')}
          </Button>
        </Box>
        <LoadingButton
          loading={loadingCreate}
          variant='contained'
          color='primary'
          onClick={handleSubmit}
          data-cy='button-save-payment-plan'
        >
          {t('Save')}
        </LoadingButton>
      </Box>
    </PageHeader>
  );
};
