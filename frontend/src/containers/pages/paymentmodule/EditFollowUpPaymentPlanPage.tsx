import { Form, Formik } from 'formik';
import React from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import moment from 'moment';
import * as Yup from 'yup';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { PaymentPlanParameters } from '../../../components/paymentmodule/CreatePaymentPlan/PaymentPlanParameters';
import { PaymentPlanTargeting } from '../../../components/paymentmodule/CreatePaymentPlan/PaymentPlanTargeting/PaymentPlanTargeting';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { handleValidationErrors, today } from '../../../utils/utils';
import {
  useAllTargetPopulationsQuery,
  usePaymentPlanQuery,
  useUpdatePpMutation,
} from '../../../__generated__/graphql';
import { EditPaymentPlanHeader } from '../../../components/paymentmodule/EditPaymentPlan/EditPaymentPlanHeader';
import { AutoSubmitFormOnEnter } from '../../../components/core/AutoSubmitFormOnEnter';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

export const EditFollowUpPaymentPlanPage = (): React.ReactElement => {
  const { id } = useParams();
  const { t } = useTranslation();
  const {
    data: paymentPlanData,
    loading: loadingPaymentPlan,
  } = usePaymentPlanQuery({
    variables: {
      id,
    },
    fetchPolicy: 'cache-and-network',
  });

  const [mutate] = useUpdatePpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();

  const {
    data: allTargetPopulationsData,
    loading: loadingTargetPopulations,
  } = useAllTargetPopulationsQuery({
    variables: { businessArea, paymentPlanApplicable: false },
  });
  if (loadingTargetPopulations || loadingPaymentPlan)
    return <LoadingComponent />;
  if (!allTargetPopulationsData || !paymentPlanData) return null;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_CREATE, permissions))
    return <PermissionDenied />;

  const { paymentPlan } = paymentPlanData;

  const initialValues = {
    targetingId: paymentPlan.targetPopulation.id,
    startDate: paymentPlan.startDate,
    endDate: paymentPlan.endDate,
    currency: {
      name: paymentPlan.currencyName,
      value: paymentPlan.currency,
    },
    dispersionStartDate: paymentPlan.dispersionStartDate,
    dispersionEndDate: paymentPlan.dispersionEndDate,
  };

  const validationSchema = Yup.object().shape({
    targetingId: Yup.string().required(t('Target Population is required')),
    startDate: Yup.date().required(t('Start Date is required')),
    endDate: Yup.date()
      .required(t('End Date is required'))
      .when(
        'startDate',
        (startDate, schema) =>
          startDate &&
          schema.min(
            startDate,
            `${t('End date has to be greater than')} ${moment(startDate).format(
              'YYYY-MM-DD',
            )}`,
          ),
        '',
      ),
    dispersionStartDate: Yup.date().required(
      t('Dispersion Start Date is required'),
    ),
    dispersionEndDate: Yup.date()
      .required(t('Dispersion End Date is required'))
      .min(today, t('Dispersion End Date cannot be in the past'))
      .when(
        'dispersionStartDate',
        (dispersionStartDate, schema) =>
          dispersionStartDate &&
          schema.min(
            dispersionStartDate,
            `${t('Dispersion End Date has to be greater than')} ${moment(
              dispersionStartDate,
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
            paymentPlanId: id,
            targetingId: values.targetingId,
            startDate: values.startDate,
            endDate: values.endDate,
            dispersionStartDate: values.dispersionStartDate,
            dispersionEndDate: values.dispersionEndDate,
            currency: values.currency?.value
              ? values.currency.value
              : values.currency,
          },
        },
      });
      showMessage(t('Follow-up Payment Plan Edited'), {
        pathname: `/${baseUrl}/payment-module/followup-payment-plans/${res.data.updatePaymentPlan.paymentPlan.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      const { nonValidationErrors } = handleValidationErrors(
        'updatePaymentPlan',
        e,
        setFieldError,
        showMessage,
      );
      if (nonValidationErrors.length > 0) {
        showMessage(t('Unexpected problem while editing Payment Plan'));
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
          <AutoSubmitFormOnEnter />
          <EditPaymentPlanHeader
            paymentPlan={paymentPlan}
            handleSubmit={submitForm}
            baseUrl={baseUrl}
            permissions={permissions}
          />
          <PaymentPlanTargeting
            allTargetPopulations={allTargetPopulationsData}
            loading={loadingTargetPopulations}
            disabled
          />
          <PaymentPlanParameters paymentPlan={paymentPlan} values={values} />
        </Form>
      )}
    </Formik>
  );
};
