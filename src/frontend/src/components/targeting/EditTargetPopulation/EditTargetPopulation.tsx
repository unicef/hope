import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Divider, Grid, Typography } from '@mui/material';
import { PaymentPlanGroupAutocompleteRest } from '@shared/autocompletes/rest/PaymentPlanGroupAutocompleteRest';
import { ProgramCycleAutocompleteRest } from '@shared/autocompletes/rest/ProgramCycleAutocompleteRest';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { FormikChipSelectField } from '@shared/Formik/FormikChipSelectField/FormikChipSelectField';
import {
  getTargetingCriteriaVariables,
  HhIdValidation,
  HhIndIdValidation,
  IndIdValidation,
} from '@utils/targetingUtils';
import { Field, FieldArray, Form, Formik } from 'formik';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import * as Yup from 'yup';
import Exclusions from '../CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../PaperContainer';
import AddFilterTargetingCriteriaDisplay from '../TargetingCriteriaDisplay/AddFilterTargetingCriteriaDisplay';
import withErrorBoundary from '@components/core/withErrorBoundary';
import EditTargetPopulationHeader from './EditTargetPopulationHeader';
import { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { PatchedTargetPopulationCreate } from '@restgenerated/models/PatchedTargetPopulationCreate';
import { RestService } from '@restgenerated/services/RestService';
import { showApiErrorMessages } from '@utils/utils';

interface EditTargetPopulationProps {
  paymentPlan: TargetPopulationDetail;
  screenBeneficiary: boolean;
}

const EditTargetPopulation = ({
  paymentPlan,
  screenBeneficiary,
}: EditTargetPopulationProps): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { id } = useParams();
  const { baseUrl, programCode, businessArea } = useBaseUrl();
  const { selectedProgram, isSocialDctType, isStandardDctType } =
    useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const targetingCriteriaCopy =
    paymentPlan.rules.map((rule) => ({
      ...rule,
      fsp: undefined,
      deliveryMechanism: undefined,
    })) || [];

  if (targetingCriteriaCopy.length > 0) {
    targetingCriteriaCopy[0].deliveryMechanism =
      paymentPlan.deliveryMechanism?.code;
    targetingCriteriaCopy[0].fsp = paymentPlan.financialServiceProvider?.id;
  }

  const initialValues = {
    id: paymentPlan.id,
    name: paymentPlan.name || '',
    program: paymentPlan.program?.id || '',
    targetingCriteria: targetingCriteriaCopy || [],
    excludedIds: paymentPlan.excludedIds || '',
    exclusionReason: paymentPlan.exclusionReason || '',
    flagExcludeIfActiveAdjudicationTicket:
      paymentPlan.flagExcludeIfActiveAdjudicationTicket || false,
    flagExcludeIfOnSanctionList:
      paymentPlan.flagExcludeIfOnSanctionList || false,
    programCycleId: {
      value: paymentPlan.programCycle.id,
      name: paymentPlan.programCycle.title,
    },
    paymentPlanGroupId: {
      value: paymentPlan.paymentPlanGroup?.id ?? '',
      name: paymentPlan.paymentPlanGroup?.name ?? '',
    },
    alternativeCollectorsIds:
      paymentPlan.rules?.[0]?.alternativeCollectorsIds || '',
    paymentPlanPurposes: paymentPlan.paymentPlanPurposes?.map((p) => p.id) ?? [],
  };

  const { data: programData } = useQuery<ProgramDetail>({
    queryKey: ['programDetail', businessArea, programCode],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRetrieve({
        businessAreaSlug: businessArea,
        code: programCode,
      }),
    enabled: paymentPlan.isPurposesEditable,
  });
  const programPurposes = (programData?.paymentPlanPurposes ?? []).map((p) => ({
    value: p.id,
    name: p.name,
  }));

  const queryClient = useQueryClient();
  const { mutateAsync: updateTargetPopulation, isPending: loadingUpdate } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        tpId,
        code,
        requestBody,
      }: {
        businessAreaSlug: string;
        tpId: string;
        code: string;
        requestBody?: PatchedTargetPopulationCreate;
      }) =>
        RestService.restBusinessAreasProgramsTargetPopulationsPartialUpdate({
          businessAreaSlug,
          id: tpId,
          programCode: code,
          requestBody,
        }),
      onSuccess: () => {
        // Invalidate and refetch the grievance ticket details
        queryClient.invalidateQueries({
          queryKey: ['targetPopulation', businessArea, id, programCode],
        });
      },
    });

  const handleValidate = (values): { targetingCriteria?: string } => {
    const {
      targetingCriteria,
      householdIds,
      individualIds,
      alternativeCollectorsIds,
    } = values;
    const errors: { targetingCriteria?: string } = {};
    if (
      !targetingCriteria.length &&
      !householdIds &&
      !individualIds &&
      !alternativeCollectorsIds
    ) {
      errors.targetingCriteria = t(
        `You need to select at least one targeting criteria or ${beneficiaryGroup?.memberLabel} ID or ${beneficiaryGroup?.groupLabel} ID`,
      );
    }
    return errors;
  };

  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .min(3, 'Targeting name should have at least 3 characters.')
      .max(255, 'Targeting name should have at most 255 characters.'),
    excludedIds: HhIndIdValidation,
    householdIds: HhIdValidation,
    individualIds: IndIdValidation,
    alternativeCollectorsIds: HhIndIdValidation,
    exclusionReason: Yup.string().max(500, t('Too long')),
    programCycleId: Yup.object().shape({
      value: Yup.string().required('Program Cycle is required'),
    }),
    paymentPlanGroupId: Yup.object().when('programCycleId', {
      is: (val) => val?.value !== paymentPlan.programCycle.id,
      then: (schema) =>
        schema.shape({
          value: Yup.string().required('Payment Plan Group is required'),
        }),
      otherwise: (schema) => schema,
    }),
  });

  const handleSubmit = async (values): Promise<void> => {
    try {
      const requestBody: PatchedTargetPopulationCreate = {
        excludedIds: values.excludedIds,
        exclusionReason: values.exclusionReason,
        fspId: values.targetingCriteria[0]?.fsp || null,
        deliveryMechanismCode: values.targetingCriteria[0]?.deliveryMechanism,
        programCycleId: values.programCycleId.value,
        ...(values.programCycleId.value !== paymentPlan.programCycle.id && {
          paymentPlanGroupId: values.paymentPlanGroupId.value,
        }),
        ...(paymentPlan.status === PaymentPlanStatusEnum.TP_OPEN && {
          name: values.name,
        }),
        ...getTargetingCriteriaVariables({
          flagExcludeIfActiveAdjudicationTicket:
            values.flagExcludeIfActiveAdjudicationTicket,
          flagExcludeIfOnSanctionList: values.flagExcludeIfOnSanctionList,
          criterias: values.targetingCriteria,
        }),
        ...(paymentPlan.isPurposesEditable && {
          paymentPlanPurposes: values.paymentPlanPurposes,
        }),
      };
      await updateTargetPopulation(
        {
          businessAreaSlug: businessArea,
          tpId: id,
          code: programCode,
          requestBody,
        },
        {
          onSuccess: () => {
            showMessage(t('Target Population Updated'));
            navigate(`/${baseUrl}/target-population/${values.id}`);
          },
        },
      );
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validate={handleValidate}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ values, submitForm, errors, setFieldValue }) => (
        <Form data-cy="edit-target-population-form">
          <AutoSubmitFormOnEnter />
          <EditTargetPopulationHeader
            handleSubmit={submitForm}
            values={values}
            loading={loadingUpdate}
            baseUrl={baseUrl}
            targetPopulation={paymentPlan}
            data-cy="edit-target-population-header"
          />
          <PaperContainer data-cy="paper-container">
            <Box pt={3} pb={3}>
              <Typography variant="h6">{t('Targeting Criteria')}</Typography>
            </Box>
            <Grid container mb={5} spacing={3}>
              <Grid size={6}>
                <ProgramCycleAutocompleteRest
                  value={values.programCycleId}
                  onChange={async (e) => {
                    await setFieldValue('programCycleId', e);
                    await setFieldValue('paymentPlanGroupId', {
                      value: '',
                      name: '',
                    });
                  }}
                  required
                  // @ts-ignore
                  error={errors.programCycleId?.value}
                  data-cy="program-cycle-autocomplete"
                />
              </Grid>
              {values.programCycleId.value !== paymentPlan.programCycle.id && (
                <Grid size={6}>
                  <PaymentPlanGroupAutocompleteRest
                    value={values.paymentPlanGroupId}
                    onChange={async (e) => {
                      await setFieldValue('paymentPlanGroupId', e);
                    }}
                    cycleId={values.programCycleId.value}
                    required
                    // @ts-ignore
                    error={errors.paymentPlanGroupId?.value}
                  />
                </Grid>
              )}
            </Grid>
            <Grid container spacing={3}>
              <Grid size={6}>
                <Field
                  name="name"
                  label={t('Target Population Name')}
                  type="text"
                  fullWidth
                  required
                  component={FormikTextField}
                  variant="outlined"
                  disabled={paymentPlan.status === 'LOCKED'}
                />
              </Grid>
              {paymentPlan.isPurposesEditable && (
                <Grid size={6}>
                  <Field
                    name="paymentPlanPurposes"
                    label={t('Purposes')}
                    choices={programPurposes}
                    component={FormikChipSelectField}
                    data-cy="input-payment-plan-purposes"
                  />
                </Grid>
              )}
            </Grid>
            <Box pt={6} pb={6}>
              <Divider />
            </Box>
            <FieldArray
              name="targetingCriteria"
              render={(arrayHelpers) => (
                <AddFilterTargetingCriteriaDisplay
                  helpers={arrayHelpers}
                  rules={values.targetingCriteria}
                  isEdit
                  screenBeneficiary={screenBeneficiary}
                  isStandardDctType={isStandardDctType}
                  isSocialDctType={isSocialDctType}
                  targetPopulation={paymentPlan}
                  data-cy="add-filter-targeting-criteria-display"
                />
              )}
            />
          </PaperContainer>
          <Exclusions
            initialOpen={Boolean(values.excludedIds)}
            data-cy="exclusions"
          />
          <Box
            pt={3}
            pb={3}
            display="flex"
            flexDirection="column"
            alignItems="center"
            data-cy="save-message-box"
          >
            <Typography style={{ color: '#b1b1b5' }} variant="h6">
              {t(
                `Save to see the list of ${beneficiaryGroup?.groupLabelPlural}`,
              )}
            </Typography>
            <Typography style={{ color: '#b1b1b5' }} variant="subtitle1">
              {t(
                `List of ${beneficiaryGroup?.groupLabelPlural} will be available after saving`,
              )}{' '}
            </Typography>
          </Box>
        </Form>
      )}
    </Formik>
  );
};

export default withErrorBoundary(EditTargetPopulation, 'EditTargetPopulation');
