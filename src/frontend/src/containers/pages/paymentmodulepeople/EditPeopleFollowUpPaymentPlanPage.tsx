import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlanParameters } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanParameters';
import { PaymentPlanTargeting } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanTargeting/PaymentPlanTargeting';
import { EditPaymentPlanHeader } from '@components/paymentmodule/EditPaymentPlan/EditPaymentPlanHeader';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { PaymentPlanBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanBackgroundActionStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
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
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';

const EditPeopleFollowUpPaymentPlanPage = (): ReactElement => {
  const navigate = useNavigate();
  const { paymentPlanId } = useParams();
  const { t } = useTranslation();
  const { baseUrl, businessArea, programId } = useBaseUrl();

  const { data: paymentPlan, isLoading: loadingPaymentPlan } =
    useQuery<PaymentPlanDetail>({
      queryKey: ['paymentPlan', businessArea, paymentPlanId, programId],
      queryFn: () =>
        RestService.restBusinessAreasProgramsPaymentPlansRetrieve({
          businessAreaSlug: businessArea,
          id: paymentPlanId,
          programSlug: programId,
        }),
      refetchInterval: () => {
        const { status, backgroundActionStatus } = paymentPlan;
        if (
          status === PaymentPlanStatusEnum.PREPARING ||
          (backgroundActionStatus !== null &&
            backgroundActionStatus !==
              PaymentPlanBackgroundActionStatusEnum.EXCLUDE_BENEFICIARIES_ERROR)
        ) {
          return 3000;
        }

        return false;
      },
      refetchIntervalInBackground: true,
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
        programSlug: programId,
        status: 'DRAFT',
      });
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
    targetingId: Yup.string().required(t('Target Population is required')),
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
      showMessage(t('Follow-up Payment Plan Edited'));
      navigate(`/${baseUrl}/payment-module/followup-payment-plans/${res.id}`);
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
          <PaymentPlanParameters paymentPlan={paymentPlan} values={values} />
        </Form>
      )}
    </Formik>
  );
};

export default withErrorBoundary(
  EditPeopleFollowUpPaymentPlanPage,
  'EditPeopleFollowUpPaymentPlanPage',
);
