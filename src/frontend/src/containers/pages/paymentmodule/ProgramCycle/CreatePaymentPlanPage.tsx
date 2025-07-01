import withErrorBoundary from '@components/core/withErrorBoundary';
import { CreatePaymentPlanHeader } from '@components/paymentmodule/CreatePaymentPlan/CreatePaymentPlanHeader/CreatePaymentPlanHeader';
import { PaymentPlanParameters } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanParameters';
import { PaymentPlanTargeting } from '@components/paymentmodule/CreatePaymentPlan/PaymentPlanTargeting/PaymentPlanTargeting';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { LoadingComponent } from '@core/LoadingComponent';
import { PermissionDenied } from '@core/PermissionDenied';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery } from '@tanstack/react-query';
import { format, parseISO } from 'date-fns';
import { Form, Formik } from 'formik';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import * as Yup from 'yup';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';

export const CreatePaymentPlanPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const { programCycleId } = useParams();

  const { mutateAsync: createPaymentPlan, isPending: loadingCreate } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        programSlug,
        requestBody,
      }: {
        businessAreaSlug: string;
        programSlug: string;
        requestBody;
      }) =>
        RestService.restBusinessAreasProgramsPaymentPlansCreate({
          businessAreaSlug,
          programSlug,
          requestBody,
        }),
    });

  const {
    data: allTargetPopulationsData,
    isLoading: loadingTargetPopulations,
  } = useQuery<PaginatedTargetPopulationListList>({
    queryKey: [
      'businessAreasProgramsTargetPopulationsList',
      businessArea,
      programId,
      programCycleId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsList({
        businessAreaSlug: businessArea,
        programSlug: programId,
        status: 'DRAFT',
        programCycle: programCycleId,
      });
    },
  });

  if (loadingTargetPopulations) return <LoadingComponent />;
  if (!allTargetPopulationsData) return null;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_CREATE, permissions))
    return <PermissionDenied />;

  const validationSchema = Yup.object().shape({
    paymentPlanId: Yup.string().required(t('Target Population is required')),
    currency: Yup.string().nullable().required(t('Currency is required')),
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

      const requestBody = {
        dispersionStartDate,
        dispersionEndDate,
        currency: values.currency,
      };

      const res = await createPaymentPlan({
        businessAreaSlug: businessArea,
        programSlug: programId,
        requestBody,
      });

      showMessage(t('Payment Plan Created'));
      navigate(`../${res.id}`);
    } catch (e) {
      showMessage(e);
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
  CreatePaymentPlanPage,
  'CreatePaymentPlanPage',
);
