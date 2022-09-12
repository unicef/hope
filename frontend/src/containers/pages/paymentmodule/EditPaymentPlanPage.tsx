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
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { handleValidationErrors } from '../../../utils/utils';
import {
  useAllTargetPopulationsQuery,
  useCurrencyChoicesQuery,
  usePaymentPlanQuery,
  useUpdatePpMutation,
} from '../../../__generated__/graphql';
import { EditPaymentPlanHeader } from '../../../components/paymentmodule/EditPaymentPlan/EditPaymentPlanHeader';

const today = new Date();
today.setHours(0, 0, 0, 0);

export const EditPaymentPlanPage = (): React.ReactElement => {
  const { id } = useParams();
  const { t } = useTranslation();
  const {
    data: paymentPlanData,
    loading: loadingPaymentPlan,
  } = usePaymentPlanQuery({
    variables: {
      paymentPlanId: id,
      fspChoices: [],
    },
    fetchPolicy: 'cache-and-network',
  });

  const [mutate] = useUpdatePpMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const {
    data: allTargetPopulationsData,
    loading: loadingTargetPopulations,
  } = useAllTargetPopulationsQuery({
    variables: { businessArea, paymentPlanApplicable: true },
  });

  const {
    data: currencyChoicesData,
    loading: loadingCurrencyChoices,
  } = useCurrencyChoicesQuery();

  if (loadingTargetPopulations || loadingCurrencyChoices || loadingPaymentPlan)
    return <LoadingComponent />;
  if (!allTargetPopulationsData || !currencyChoicesData || !paymentPlanData)
    return null;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  const initialValues = {
    targetingId: paymentPlanData.paymentPlan.targetPopulation.id,
    startDate: paymentPlanData.paymentPlan.startDate,
    endDate: paymentPlanData.paymentPlan.endDate,
    currency: paymentPlanData.paymentPlan.currency,
    dispersionStartDate: paymentPlanData.paymentPlan.dispersionStartDate,
    dispersionEndDate: paymentPlanData.paymentPlan.dispersionEndDate,
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
            currency: values.currency,
          },
        },
      });
      showMessage(t('Payment Plan Edited'), {
        pathname: `/${businessArea}/payment-module/payment-plans/${res.data.updatePaymentPlan.paymentPlan.id}`,
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
          <EditPaymentPlanHeader
            paymentPlan={paymentPlanData.paymentPlan}
            handleSubmit={submitForm}
            businessArea={businessArea}
            permissions={permissions}
          />
          <PaymentPlanTargeting
            allTargetPopulations={allTargetPopulationsData}
            loading={loadingTargetPopulations}
          />
          <PaymentPlanParameters
            currencyChoicesData={currencyChoicesData.currencyChoices}
            values={values}
          />
        </Form>
      )}
    </Formik>
  );
};
