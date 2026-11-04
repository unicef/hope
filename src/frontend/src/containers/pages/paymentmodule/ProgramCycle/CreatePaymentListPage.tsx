import withErrorBoundary from '@components/core/withErrorBoundary';
import { CreatePaymentListHeader } from '@components/paymentmodule/CreatePaymentList/CreatePaymentListHeader/CreatePaymentListHeader';
import { PaymentListParameters } from '@components/paymentmodule/CreatePaymentList/PaymentListParameters';
import { PaymentListTargeting } from '@components/paymentmodule/CreatePaymentList/PaymentListTargeting/PaymentListTargeting';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '@core/LoadingComponent';
import { PermissionDenied } from '@core/PermissionDenied';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import type { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { Form, Formik } from 'formik';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import * as Yup from 'yup';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { showApiErrorMessages } from '@utils/utils';

export const CreatePaymentListPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const { programCycleId } = useParams();
  const queryClient = useQueryClient();

  const { mutateAsync: createPaymentList, isPending: loadingCreate } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        programCode,
        requestBody,
      }: {
        businessAreaSlug: string;
        programCode: string;
        requestBody;
      }) =>
        RestService.restBusinessAreasProgramsPaymentListsCreate({
          businessAreaSlug,
          programCode,
          requestBody,
        }),
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsPaymentListsList,
          ),
        });
      },
    });

  const {
    data: allTargetPopulationsData,
    isLoading: loadingTargetPopulations,
  } = useQuery<PaginatedTargetPopulationListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsTargetPopulationsList,
      {
        businessAreaSlug: businessArea,
        programCode: programId,
        status: 'DRAFT',
        programCycle: programCycleId,
      },
    ),
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsList({
        businessAreaSlug: businessArea,
        programCode: programId,
        status: 'DRAFT',
        programCycle: programCycleId,
      });
    },
  });

  if (loadingTargetPopulations) return <LoadingComponent />;
  if (!allTargetPopulationsData) return null;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_CREATE, permissions))
    return <PermissionDenied permission={PERMISSIONS.PM_CREATE} />;

  const validationSchema = Yup.object().shape({
    paymentListId: Yup.string().required(t('Target Population is required')),
  });

  const initialValues = {
    paymentListId: '',
  };

  const handleSubmit = async (values: typeof initialValues): Promise<void> => {
    try {
      const requestBody = { targetPopulationId: values.paymentListId };

      const res = await createPaymentList({
        businessAreaSlug: businessArea,
        programCode: programId,
        requestBody,
      });

      showMessage(t('Payment List Created'));
      navigate(`../${res.id}`);
    } catch (e) {
      showApiErrorMessages(e, showMessage);
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
          <CreatePaymentListHeader
            handleSubmit={submitForm}
            permissions={permissions}
            loadingCreate={loadingCreate}
          />
          <PaymentListTargeting
            targetPopulations={allTargetPopulationsData.results}
            loading={loadingTargetPopulations}
          />
          <PaymentListParameters
            paymentPlanId={
              allTargetPopulationsData.results.find(
                (tp) => tp.id === values.paymentListId,
              )?.paymentPlan?.id
            }
          />
        </Form>
      )}
    </Formik>
  );
};

export default withErrorBoundary(
  CreatePaymentListPage,
  'CreatePaymentListPage',
);
