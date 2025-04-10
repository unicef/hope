import { Form, Formik } from 'formik';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import moment from 'moment';
import * as Yup from 'yup';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { PaymentPlanParameters } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanParameters';
import { PaymentPlanTargeting } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanTargeting/PaymentPlanTargeting';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { today } from '@utils/utils';
import { useAllTargetPopulationsQuery } from '@generated/graphql';
import { EditPaymentPlanHeader } from '@components/paymentmodule/EditPaymentPlan/EditPaymentPlanHeader';
import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery } from '@tanstack/react-query';

const EditPaymentPlanPage = (): ReactElement => {
  const navigate = useNavigate();
  const { paymentPlanId } = useParams();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { t } = useTranslation();
  const { data: paymentPlan, isLoading: loadingPaymentPlan } =
    useQuery<PaymentPlanDetail>({
      queryKey: ['paymentPlan', businessArea, paymentPlanId, programId],
      queryFn: () =>
        RestService.restBusinessAreasProgramsPaymentPlansRetrieve({
          businessAreaSlug: businessArea,
          id: paymentPlanId,
          programSlug: programId,
        }),
    });

  const { mutateAsync: updatePaymentPlan, isPending: loadingUpdate } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id: mutationId,
        programSlug,
        requestBody,
      }: {
        businessAreaSlug: string;
        id: string;
        programSlug: string;
        requestBody;
      }) =>
        RestService.restBusinessAreasProgramsPaymentPlansPartialUpdate({
          businessAreaSlug,
          id: mutationId,
          programSlug,
          requestBody,
        }),
    });
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();

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
    dispersionStartDate: paymentPlan.dispersionStartDate,
    dispersionEndDate: paymentPlan.dispersionEndDate,
  };

  const validationSchema = Yup.object().shape({
    paymentPlanId: Yup.string().required(t('Target Population is required')),
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
                dispersionStartDate as Date,
                `${t('Dispersion End Date has to be greater than')} ${moment(
                  dispersionStartDate,
                ).format('YYYY-MM-DD')}`,
              )
            : schema,
      ),
  });

  const handleSubmit = async (values): Promise<void> => {
    const requestBody = {
      dispersionStartDate: values.dispersionStartDate,
      dispersionEndDate: values.dispersionEndDate,
      currency: values.currency?.value
        ? values.currency.value
        : values.currency,
    };
    try {
      const res = await updatePaymentPlan({
        businessAreaSlug: businessArea,
        id: paymentPlanId,
        programSlug: programId,
        requestBody,
      });
      showMessage(t('Payment Plan Edited'));
      navigate(`/${baseUrl}/payment-module/payment-plans/${res.id}`);
    } catch (e) {
      showMessage(e);
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
            loadingUpdate={loadingUpdate}
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

export default withErrorBoundary(EditPaymentPlanPage, 'EditPaymentPlanPage');
