import { Form, Formik } from 'formik';
import * as React from 'react';
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
  useCreatePpMutation,
} from '@generated/graphql';
import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useNavigate } from 'react-router-dom';

export const CreatePaymentPlanPage = (): React.ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [mutate, { loading: loadingCreate }] = useCreatePpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();

  const { data: allTargetPopulationsData, loading: loadingTargetPopulations } =
    useAllTargetPopulationsQuery({
      variables: {
        businessArea,
        paymentPlanApplicable: true,
        program: [programId],
      },
      fetchPolicy: 'network-only',
    });

  if (loadingTargetPopulations) return <LoadingComponent />;
  if (!allTargetPopulationsData) return null;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_CREATE, permissions))
    return <PermissionDenied />;

  const validationSchema = Yup.object().shape({
    currency: Yup.string(),
    targetingId: Yup.string().required(t('Target Population is required')),
    startDate: Yup.date().required(t('Start Date is required')),
    endDate: Yup.date()
      .required(t('End Date is required'))
      .when('startDate', (startDate: any, schema: Yup.DateSchema) =>
        startDate && typeof startDate === 'string'
          ? schema.min(
              parseISO(startDate),
              `${t('End date has to be greater than')} ${format(parseISO(startDate), 'yyyy-MM-dd')}`,
            )
          : schema,
      ),
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
    targetingId: '',
    startDate: null,
    endDate: null,
    currency: null,
    dispersionStartDate: null,
    dispersionEndDate: null,
  };

  const handleSubmit = async (values: FormValues): Promise<void> => {
    try {
      const startDate = values.startDate
        ? format(new Date(values.startDate), 'yyyy-MM-dd')
        : null;
      const endDate = values.endDate
        ? format(new Date(values.endDate), 'yyyy-MM-dd')
        : null;
      const dispersionStartDate = values.dispersionStartDate
        ? format(new Date(values.dispersionStartDate), 'yyyy-MM-dd')
        : null;
      const dispersionEndDate = values.dispersionEndDate
        ? format(new Date(values.dispersionEndDate), 'yyyy-MM-dd')
        : null;

      const res = await mutate({
        variables: {
          //@ts-ignore
          input: {
            businessAreaSlug: businessArea,
            ...values,
            startDate,
            endDate,
            dispersionStartDate,
            dispersionEndDate,
            //TODO: remove this when the backend is updated
            name: 'Payment Plan',
          },
        },
      });
      showMessage(t('Payment Plan Created'));
      navigate(
        `/${baseUrl}/payment-module/payment-plans/${res.data.createPaymentPlan.paymentPlan.id}`,
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
        <Form placeholder="Form">
          <AutoSubmitFormOnEnter />
          <CreatePaymentPlanHeader
            handleSubmit={submitForm}
            baseUrl={baseUrl}
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
