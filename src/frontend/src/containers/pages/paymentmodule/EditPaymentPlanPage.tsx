import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlanParameters } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanParameters';
import { PaymentPlanTargeting } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanTargeting/PaymentPlanTargeting';
import { EditPaymentPlanHeader } from '@components/paymentmodule/EditPaymentPlan/EditPaymentPlanHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery } from '@tanstack/react-query';
import { showApiErrorMessages, today } from '@utils/utils';
import { Form, Formik } from 'formik';
import moment from 'moment';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import * as Yup from 'yup';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';

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
          programCode: programId,
        }),
    });

  const { mutateAsync: updatePaymentPlan, isPending: loadingUpdate } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id: mutationId,
        programCode,
        requestBody,
      }: {
        businessAreaSlug: string;
        id: string;
        programCode: string;
        requestBody;
      }) =>
        RestService.restBusinessAreasProgramsPaymentPlansPartialUpdate({
          businessAreaSlug,
          id: mutationId,
          programCode,
          requestBody,
        }),
    });
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();

  // TODO: Replace with real endpoint when available: GET /api/rest/business-areas/{ba}/programs/{code}/payment-plan-purposes/
  const { data: programPurposesData } = useQuery<
    Array<{ id: string; name: string }>
  >({
    queryKey: ['programPaymentPlanPurposes', businessArea, programId],
    queryFn: () =>
      (RestService as any).restBusinessAreasProgramsPaymentPlanPurposesList({
        businessAreaSlug: businessArea,
        programCode: programId,
      }),
    enabled: false,
  });
  const programPurposes = (programPurposesData || []).map((p) => ({
    value: p.id,
    name: p.name,
  }));

  const {
    data: allTargetPopulationsData,
    isLoading: loadingTargetPopulations,
  } = useQuery<PaginatedTargetPopulationListList>({
    queryKey: [
      'businessAreasProgramsTargetPopulationsList',
      businessArea,
      programId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsList({
        businessAreaSlug: businessArea,
        programCode: programId,
        status: 'DRAFT',
      });
    },
  });
  if (loadingTargetPopulations || loadingPaymentPlan)
    return <LoadingComponent />;
  if (!allTargetPopulationsData || !paymentPlan) return null;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_CREATE, permissions))
    return <PermissionDenied permission={PERMISSIONS.PM_CREATE} />;

  const initialValues = {
    paymentPlanId: paymentPlan.id,
    currency: {
      name: paymentPlan.currency,
      value: paymentPlan.currency,
    },
    dispersionStartDate: paymentPlan.dispersionStartDate,
    dispersionEndDate: paymentPlan.dispersionEndDate,
    // @ts-ignore TODO: add paymentPlanPurposes to PaymentPlanDetail type when endpoint is available
    paymentPlanPurposes: ((paymentPlan as any).paymentPlanPurposes ?? []).map((p: any) => p.id),
  };

  const validationSchema = Yup.object().shape({
    paymentPlanId: Yup.string().required(t('Target Population is required')),
    paymentPlanPurposes: Yup.array()
      .min(1, t('At least one Purpose is required'))
      .max(5, t('Maximum 5 Purposes allowed')),
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
      // @ts-ignore TODO: add paymentPlanPurposes to PaymentPlanCreateUpdate type when endpoint is available
      paymentPlanPurposes: values.paymentPlanPurposes,
    };
    try {
      const res = await updatePaymentPlan({
        businessAreaSlug: businessArea,
        id: paymentPlanId,
        programCode: programId,
        requestBody,
      });
      showMessage(t('Payment Plan Edited'));
      navigate(`/${baseUrl}/payment-module/payment-plans/${res.id}`);
    } catch (e) {
      showApiErrorMessages(e, showMessage);
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
          <PaymentPlanParameters
            paymentPlan={paymentPlan}
            values={values}
            programPurposes={programPurposes}
            disablePurposes
          />
        </Form>
      )}
    </Formik>
  );
};

export default withErrorBoundary(EditPaymentPlanPage, 'EditPaymentPlanPage');
