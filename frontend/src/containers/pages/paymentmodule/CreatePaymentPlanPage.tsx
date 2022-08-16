import { Form, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import moment from 'moment';
import * as Yup from 'yup';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { CreatePaymentPlanHeader } from '../../../components/paymentmodule/CreatePaymentPlan/CreatePaymentPlanHeader/CreatePaymentPlanHeader';
import { PaymentPlanParameters } from '../../../components/paymentmodule/CreatePaymentPlan/PaymentPlanParameters';
import { PaymentPlanTargeting } from '../../../components/paymentmodule/CreatePaymentPlan/PaymentPlanTargeting/PaymentPlanTargeting';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  useAllTargetPopulationsQuery,
  useCreatePpMutation,
  useCurrencyChoicesQuery,
} from '../../../__generated__/graphql';

const today = new Date();
today.setHours(0, 0, 0, 0);

export const CreatePaymentPlanPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const initialValues = {
    targetingId: '',
    startDate: '',
    endDate: '',
    currency: null,
    dispersionStartDate: '',
    dispersionEndDate: '',
  };
  const [mutate, { loading: loadingCreate }] = useCreatePpMutation();
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

  if (loadingTargetPopulations || loadingCurrencyChoices)
    return <LoadingComponent />;
  if (!allTargetPopulationsData || !currencyChoicesData) return null;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

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

  const handleSubmit = async (values): Promise<void> => {
    try {
      const res = await mutate({
        variables: {
          input: {
            businessAreaSlug: businessArea,
            targetingId: values.targetingId,
            startDate: values.startDate,
            endDate: values.endDate,
            dispersionStartDate: values.dispersionStartDate,
            dispersionEndDate: values.dispersionEndDate,
            currency: values.currency,
          },
        },
      });
      showMessage(t('Payment Plan Created'), {
        pathname: `/${businessArea}/payment-module/payment-plans/${res.data.createPaymentPlan.paymentPlan.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
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
          <CreatePaymentPlanHeader
            handleSubmit={submitForm}
            businessArea={businessArea}
            permissions={permissions}
            loadingCreate={loadingCreate}
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
