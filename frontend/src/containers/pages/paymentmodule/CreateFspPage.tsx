import { Box, Paper } from '@material-ui/core';
import { Form, Formik } from 'formik';
import moment from 'moment';
import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { CreateFspHeader } from '../../../components/paymentmodule/CreateFspPlan/CreateFspHeader';
import { Fsp } from '../../../components/paymentmodule/CreateFspPlan/Fsp';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';
import { handleValidationErrors } from '../../../utils/utils';
import {
  useAllTargetPopulationsQuery,
  useCreateTpMutation,
} from '../../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../../../components/core/ContainerColumnWithBorder';

const today = new Date();
today.setHours(0, 0, 0, 0);

export const CreateFspPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const initialValues = {
    targetPopulation: '',
    startDate: '',
    endDate: '',
    currency: null,
  };
  const [mutate] = useCreateTpMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const {
    data: allTargetPopulationsData,
    loading: loadingTargetPopulations,
  } = useAllTargetPopulationsQuery({
    variables: { businessArea },
  });

  if (loadingTargetPopulations) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  const validationSchema = Yup.object().shape({
    targetPopulation: Yup.string().required(t('Target Population is required')),
    startDate: Yup.date().required(t('Start Date is required')),
    endDate: Yup.date()
      .required(t('End Date is required'))
      .min(today, t('End Date cannot be in the past'))
      .when(
        'startDate',
        (startDate, schema) =>
          startDate &&
          schema.min(
            startDate,
            `${t('End date have to be greater than')} ${moment(
              startDate,
            ).format('YYYY-MM-DD')}`,
          ),
        '',
      ),
  });

  const handleSubmit = async (values, { setFieldError }): Promise<void> => {
    try {
      const res = await mutate({
        variables: {
          input: {
            programId: values.program,
            name: values.name,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            businessAreaSlug: businessArea,
            ...getTargetingCriteriaVariables(values),
          },
        },
      });
      showMessage(t('Target Population Created'), {
        pathname: `/${businessArea}/target-population/${res.data.createTargetPopulation.targetPopulation.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      const { nonValidationErrors } = handleValidationErrors(
        'createTargetPopulation',
        e,
        setFieldError,
        showMessage,
      );
      if (nonValidationErrors.length > 0) {
        showMessage(t('Unexpected problem while creating Target Population'));
      }
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ submitForm, values }) => (
        <Form>
          <CreateFspHeader
            handleSubmit={submitForm}
            businessArea={businessArea}
            permissions={permissions}
          />
          <Box m={5}>
            <ContainerColumnWithBorder>
              <Fsp permissions={permissions} />
            </ContainerColumnWithBorder>
          </Box>
        </Form>
      )}
    </Formik>
  );
};
