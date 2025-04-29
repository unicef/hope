import { Form, Formik } from 'formik';
import { useTranslation } from 'react-i18next';
import { format, parseISO } from 'date-fns';
import * as Yup from 'yup';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { CreatePaymentPlanHeader } from '@components/paymentmodule/CreatePaymentPlan/CreatePaymentPlanHeader/CreatePaymentPlanHeader';
import { PaymentPlanParameters } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanParameters';
import { PaymentPlanTargeting } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanTargeting/PaymentPlanTargeting';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  useAllTargetPopulationsQuery,
  useUpdatePpMutation,
} from '@generated/graphql';
import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useNavigate, useParams } from 'react-router-dom';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

export const CreatePeoplePaymentPlanPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [mutate, { loading: loadingCreate }] = useUpdatePpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();
  const { programCycleId } = useParams();

  const { data: allTargetPopulationsData, loading: loadingTargetPopulations } =
    useAllTargetPopulationsQuery({
      variables: {
        businessArea,
        status: 'DRAFT',
        program: programId,
        programCycle: programCycleId,
      },
      fetchPolicy: 'network-only',
    });

  if (loadingTargetPopulations) return <LoadingComponent />;
  if (!allTargetPopulationsData) return null;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_CREATE, permissions))
    return <PermissionDenied />;

  const validationSchema = Yup.object().shape({
    paymentPlanId: Yup.string().required(t('Target Population is required')),
    currency: Yup.string().required(t('Currency is required')),
    dispersionStartDate: Yup.date().required(
      t('Dispersion Start Date is required'),
    ),
    dispersionEndDate: Yup.date()
      .required(t('Dispersion End Date is required'))
      .min(new Date(), t('Dispersion End Date cannot be in the past'))
      .when(
        'dispersionStartDate',
        (dispersionStartDate: any, schema: Yup.DateSchema) =>
          dispersionStartDate && typeof dispersionStartDate === 'string'
            ? schema.min(
                parseISO(dispersionStartDate),
                `${t('Dispersion End Date has to be greater than')} ${format(parseISO(dispersionStartDate), 'yyyy-MM-dd')}`,
              )
            : schema,
      ),
  });

  type FormValues = Yup.InferType<typeof validationSchema>;
  const initialValues: FormValues = {
    paymentPlanId: '',
    currency: null,
    dispersionStartDate: null,
    dispersionEndDate: null,
  };

  const handleSubmit = async (values: FormValues): Promise<void> => {
    try {
      const dispersionStartDate = values.dispersionStartDate
        ? format(new Date(values.dispersionStartDate), 'yyyy-MM-dd')
        : null;
      const dispersionEndDate = values.dispersionEndDate
        ? format(new Date(values.dispersionEndDate), 'yyyy-MM-dd')
        : null;
      const { currency, paymentPlanId } = values;

      const res = await mutate({
        variables: {
          currency,
          paymentPlanId,
          dispersionStartDate,
          dispersionEndDate,
        },
      });
      showMessage(t('Payment Plan Created'));
      navigate(
        `/${baseUrl}/payment-module/payment-plans/${res.data.updatePaymentPlan.paymentPlan.id}`,
      );
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
      validateOnChange
      validateOnBlur
    >
      {({ submitForm, values }) => (
        <Form>
          <AutoSubmitFormOnEnter />
          <CreatePaymentPlanHeader
            handleSubmit={submitForm}
            permissions={permissions}
            loadingCreate={loadingCreate}
          />
          <PaymentPlanTargeting
            allTargetPopulations={allTargetPopulationsData}
            loading={loadingTargetPopulations}
          />
          <PaymentPlanParameters values={values} />
        </Form>
      )}
    </Formik>
  );
};

export default withErrorBoundary(
  CreatePeoplePaymentPlanPage,
  'CreatePeoplePaymentPlanPage',
);
