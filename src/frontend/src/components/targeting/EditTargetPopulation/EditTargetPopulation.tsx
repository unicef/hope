import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  Divider,
  Grid,
  TextField,
  Typography,
} from '@mui/material';
import { CreatePaymentPlanModal } from '@components/paymentmodule/CreatePaymentPlanModal';
import { ProgramCycleAutocompleteRest } from '@shared/autocompletes/rest/ProgramCycleAutocompleteRest';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { FormikChipAutocomplete } from '@shared/Formik/FormikChipAutocomplete/FormikChipAutocomplete';
import {
  getTargetingCriteriaVariables,
  HhIdValidation,
  HhIndIdValidation,
  IndIdValidation,
} from '@utils/targetingUtils';
import { Field, FieldArray, Form, Formik } from 'formik';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { responsiveGridSize } from 'src/responsive';
import * as Yup from 'yup';
import Exclusions from '../CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../PaperContainer';
import AddFilterTargetingCriteriaDisplay from '../TargetingCriteriaDisplay/AddFilterTargetingCriteriaDisplay';
import withErrorBoundary from '@components/core/withErrorBoundary';
import EditTargetPopulationHeader from './EditTargetPopulationHeader';
import type { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import type { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { PatchedTargetPopulationCreate } from '@restgenerated/models/PatchedTargetPopulationCreate';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';

interface EditTargetPopulationProps {
  paymentList: TargetPopulationDetail;
  screenBeneficiary: boolean;
}

const EditTargetPopulation = ({
  paymentList,
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
  const permissions = usePermissions();
  // Without the list permission the cycle stays fixed to the target population's own.
  const canListCycles = hasPermissions(
    PERMISSIONS.PM_PROGRAMME_CYCLE_VIEW_LIST,
    permissions,
  );
  const [createPaymentPlanModalOpen, setCreatePaymentPlanModalOpen] =
    useState(false);
  const [modalCycle, setModalCycle] = useState<{ value: string; name: string }>(
    {
      value: paymentList.programCycle.id,
      name: paymentList.programCycle.title,
    },
  );

  const targetingCriteriaCopy =
    paymentList.rules.map((rule) => ({
      ...rule,
      deliveryMechanism: undefined,
    })) || [];

  if (targetingCriteriaCopy.length > 0) {
    targetingCriteriaCopy[0].deliveryMechanism =
      paymentList.deliveryMechanism?.code;
  }

  const initialValues = {
    id: paymentList.id,
    name: paymentList.name || '',
    program: paymentList.program?.id || '',
    targetingCriteria: targetingCriteriaCopy || [],
    excludedIds: paymentList.excludedIds || '',
    exclusionReason: paymentList.exclusionReason || '',
    flagExcludeIfActiveAdjudicationTicket:
      paymentList.flagExcludeIfActiveAdjudicationTicket || false,
    flagExcludeIfOnSanctionList:
      paymentList.flagExcludeIfOnSanctionList || false,
    programCycleId: {
      value: paymentList.programCycle.id,
      name: paymentList.programCycle.title,
    },
    paymentPlanId: {
      value: paymentList.paymentPlan?.id ?? '',
      name: paymentList.paymentPlan?.name ?? '',
    },
    alternativeCollectorsIds:
      paymentList.rules?.[0]?.alternativeCollectorsIds || '',
    paymentPlanPurposes:
      paymentList.paymentPlanPurposes?.map((p) => p.id) ?? [],
  };

  const { data: programData } = useQuery<ProgramDetail>({
    queryKey: restQueryKey(RestService.restBusinessAreasProgramsRetrieve, {
      businessAreaSlug: businessArea,
      code: programCode,
    }),
    queryFn: () =>
      RestService.restBusinessAreasProgramsRetrieve({
        businessAreaSlug: businessArea,
        code: programCode,
      }),
    enabled: paymentList.isPurposesEditable,
  });
  const programPurposes = (programData?.paymentPlanPurposes ?? []).map((p) => ({
    value: p.id,
    name: p.name,
  }));
  const lockedPurposeIds = (programData?.paymentPlanPurposes ?? [])
    .filter((p) => p.isUsedInPp)
    .map((p) => p.id);

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
        queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsTargetPopulationsRetrieve,
          ),
        });
        queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsTargetPopulationsList,
          ),
        });
      },
    });

  const handleValidate = (
    values,
  ): { targetingCriteria?: string; paymentPlanId?: { value: string } } => {
    const {
      targetingCriteria,
      householdIds,
      individualIds,
      alternativeCollectorsIds,
    } = values;
    const errors: {
      targetingCriteria?: string;
      paymentPlanId?: { value: string };
    } = {};
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
    if (
      values.programCycleId.value !== paymentList.programCycle.id &&
      !values.paymentPlanId?.value
    ) {
      errors.paymentPlanId = { value: 'Payment Plan is required' };
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
  });

  const handleSubmit = async (values): Promise<void> => {
    try {
      const requestBody: PatchedTargetPopulationCreate = {
        excludedIds: values.excludedIds,
        exclusionReason: values.exclusionReason,
        deliveryMechanismCode: values.targetingCriteria[0]?.deliveryMechanism,
        ...((values.programCycleId.value !== paymentList.programCycle.id ||
          (values.paymentPlanId?.value &&
            values.paymentPlanId.value !==
              (paymentList.paymentPlan?.id ?? ''))) && {
          programCycleId: values.programCycleId.value,
          paymentPlanId: values.paymentPlanId.value,
        }),
        ...(paymentList.status === PaymentListStatusEnum.TP_OPEN && {
          name: values.name,
        }),
        ...getTargetingCriteriaVariables({
          flagExcludeIfActiveAdjudicationTicket:
            values.flagExcludeIfActiveAdjudicationTicket,
          flagExcludeIfOnSanctionList: values.flagExcludeIfOnSanctionList,
          criterias: values.targetingCriteria,
        }),
        ...(paymentList.isPurposesEditable && {
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
            targetPopulation={paymentList}
            data-cy="edit-target-population-header"
          />
          <PaperContainer data-cy="paper-container">
            <Box
              sx={{
                pt: 3,
                pb: 3,
              }}
            >
              <Typography variant="h6">{t('Targeting Criteria')}</Typography>
            </Box>
            <Grid
              container
              spacing={3}
              sx={{
                mb: 5,
              }}
            >
              <Grid size={responsiveGridSize('half')}>
                <ProgramCycleAutocompleteRest
                  value={values.programCycleId}
                  onChange={async (e) => {
                    await setFieldValue(
                      'programCycleId',
                      e ?? { value: '', name: '' },
                    );
                    if (e?.value && e.value !== paymentList.programCycle.id) {
                      await setFieldValue('paymentPlanId', {
                        value: '',
                        name: '',
                      });
                      setModalCycle(e);
                      setCreatePaymentPlanModalOpen(true);
                    }
                  }}
                  required
                  // @ts-ignore
                  error={errors.programCycleId?.value}
                  data-cy="program-cycle-autocomplete"
                  enabled={canListCycles}
                  disabled={!canListCycles}
                />
              </Grid>
              <Grid size={responsiveGridSize('half')}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                  }}
                >
                  <TextField
                    label={t('Payment Plan')}
                    value={values.paymentPlanId?.name || ''}
                    disabled
                    fullWidth
                    variant="outlined"
                    size="small"
                  />
                  {paymentList.status === PaymentListStatusEnum.TP_OPEN &&
                    hasPermissions(
                      PERMISSIONS.PM_PAYMENT_PLAN_CREATE,
                      permissions,
                    ) && (
                      <Button
                        variant="outlined"
                        color="primary"
                        onClick={() => {
                          setModalCycle(values.programCycleId);
                          setCreatePaymentPlanModalOpen(true);
                        }}
                        data-cy="button-change-group"
                        sx={{ whiteSpace: 'nowrap', flexShrink: 0 }}
                      >
                        {t('Change Payment Plan')}
                      </Button>
                    )}
                </Box>
              </Grid>
            </Grid>
            <CreatePaymentPlanModal
              open={createPaymentPlanModalOpen}
              onClose={() => setCreatePaymentPlanModalOpen(false)}
              cycleId={modalCycle.value}
              cycleTitle={modalCycle.name}
              onSuccess={(paymentPlan) => {
                setFieldValue('paymentPlanId', {
                  value: paymentPlan.id,
                  name: paymentPlan.name,
                });
                setCreatePaymentPlanModalOpen(false);
              }}
            />
            <Grid container spacing={3}>
              <Grid size={responsiveGridSize('half')}>
                <Field
                  name="name"
                  label={t('Target Population Name')}
                  type="text"
                  fullWidth
                  required
                  component={FormikTextField}
                  variant="outlined"
                  disabled={paymentList.status === 'LOCKED'}
                />
              </Grid>
              {paymentList.isPurposesEditable && (
                <Grid size={responsiveGridSize('half')}>
                  <Field
                    name="paymentPlanPurposes"
                    label={t('Payment Plan Purposes')}
                    choices={programPurposes}
                    lockedValues={lockedPurposeIds}
                    component={FormikChipAutocomplete}
                    data-cy="input-payment-plan-purposes"
                  />
                </Grid>
              )}
            </Grid>
            <Box
              sx={{
                pt: 6,
                pb: 6,
              }}
            >
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
                  targetPopulation={paymentList}
                  paymentPlanId={values.paymentPlanId?.value}
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
            data-cy="save-message-box"
            sx={{
              pt: 3,
              pb: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
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
