import { Form, Formik } from 'formik';
import moment from 'moment';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import * as Yup from 'yup';
import {
  useAllTargetPopulationsQuery,
  useUpdatePpMutation,
} from '@generated/graphql';
import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { PaymentPlanParameters } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanParameters';
import { PaymentPlanTargeting } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanTargeting/PaymentPlanTargeting';
import { EditPaymentPlanHeader } from '@components/paymentmodule/EditPaymentPlan/EditPaymentPlanHeader';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { today } from '@utils/utils';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';

const EditFollowUpPaymentPlanPage = (): ReactElement => {
  const navigate = useNavigate();
  const { paymentPlanId } = useParams();
  const { t } = useTranslation();
  const [mutate] = useUpdatePpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();

  const { data: paymentPlan, isLoading: loadingPaymentPlan } = useQuery({
    queryKey: ['paymentPlan', businessArea, paymentPlanId, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansRetrieve({
        businessAreaSlug: businessArea,
        id: paymentPlanId,
        programSlug: programId,
      }),
  });

  const { data: allTargetPopulationsData, loading: loadingTargetPopulations } =
    useAllTargetPopulationsQuery({
      variables: {
        businessArea,
        status: 'DRAFT',
        program: programId,
      },
    });
  if (loadingTargetPopulations || loadingPaymentPlan)
    return <LoadingComponent />;
  if (!allTargetPopulationsData || !paymentPlan) return null;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_CREATE, permissions))
    return <PermissionDenied />;

  const initialValues = {
    paymentPlanId: paymentPlan.id,
    currency: {
      name: paymentPlan.currency,
      value: paymentPlan.currency,
    },
    dispersionStartDate: paymentPlan.dispersion_start_date,
    dispersionEndDate: paymentPlan.dispersion_end_date,
  };

  const validationSchema = Yup.object().shape({
    paymentPlanId: Yup.string().required(t('Target Population is required')),
    currency: Yup.string().nullable().required(t('Currency is required')),
    dispersionStartDate: Yup.date().required(
      t('Dispersion Start Date is required'),
    ),
    dispersionEndDate: Yup.date()
      .required(t('Dispersion End Date is required'))
      .min(today, t('Dispersion End Date cannot be in the past'))
      .when(
        'dispersionStartDate',
        (dispersionStartDate: any, schema: Yup.DateSchema) =>
          dispersionStartDate
            ? schema.min(
                dispersionStartDate,
                `${t('Dispersion End Date has to be greater than')} ${moment(
                  dispersionStartDate,
                ).format('YYYY-MM-DD')}`,
              )
            : schema,
      ),
  });

  const handleSubmit = async (values): Promise<void> => {
    try {
      const res = await mutate({
        variables: {
          paymentPlanId,
          dispersionStartDate: values.dispersionStartDate,
          dispersionEndDate: values.dispersionEndDate,
          currency: values.currency?.value
            ? values.currency.value
            : values.currency,
        },
      });
      showMessage(t('Follow-up Payment Plan Edited'));
      navigate(
        `/${baseUrl}/payment-module/followup-payment-plans/${res.data.updatePaymentPlan.paymentPlan.id}`,
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
export default withErrorBoundary(
  EditFollowUpPaymentPlanPage,
  'EditFollowUpPaymentPlanPage',
);
