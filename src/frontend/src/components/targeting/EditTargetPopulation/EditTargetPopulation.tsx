import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import {
  PaymentPlanQuery,
  PaymentPlanStatus,
  useUpdatePpMutation,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Divider, Grid2 as Grid, Typography } from '@mui/material';
import { ProgramCycleAutocompleteRest } from '@shared/autocompletes/rest/ProgramCycleAutocompleteRest';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import {
  getTargetingCriteriaVariables,
  HhIdValidation,
  HhIndIdValidation,
  IndIdValidation,
} from '@utils/targetingUtils';
import { Field, FieldArray, Form, Formik } from 'formik';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import * as Yup from 'yup';
import Exclusions from '../CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../PaperContainer';
import AddFilterTargetingCriteriaDisplay from '../TargetingCriteriaDisplay/AddFilterTargetingCriteriaDisplay';
import withErrorBoundary from '@components/core/withErrorBoundary';
import EditTargetPopulationHeader from './EditTargetPopulationHeader';

interface EditTargetPopulationProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  screenBeneficiary: boolean;
}

type TargetingCriteriaRuleNodeExtended = {
  __typename: 'TargetingCriteriaRuleNode';
  id: any;
  householdIds: string;
  individualIds: string;
  individualsFiltersBlocks?: {
    __typename: 'TargetingIndividualRuleFilterBlockNode';
    individualBlockFilters?: {
      // Define the properties of individualBlockFilters here
    }[];
  }[];
  collectorsFiltersBlocks: {
    // Define the properties of collectorsFiltersBlocks here
  }[];
  householdsFiltersBlocks?: {
    // Define the properties of householdsFiltersBlocks here
  }[];
  deliveryMechanism?: string;
  fsp?: string;
};

const EditTargetPopulation = ({
  paymentPlan,
  screenBeneficiary,
}: EditTargetPopulationProps): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const targetingCriteriaCopy: TargetingCriteriaRuleNodeExtended[] =
    paymentPlan.targetingCriteria?.rules.map((rule) => ({ ...rule })) || [];

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
      paymentPlan.targetingCriteria.flagExcludeIfActiveAdjudicationTicket ||
      false,
    flagExcludeIfOnSanctionList:
      paymentPlan.targetingCriteria.flagExcludeIfOnSanctionList || false,
    programCycleId: {
      value: paymentPlan.programCycle.id,
      name: paymentPlan.programCycle.title,
    },
  };

  const [mutate, { loading }] = useUpdatePpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl } = useBaseUrl();
  const { selectedProgram, isSocialDctType, isStandardDctType } =
    useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const handleValidate = (values): { targetingCriteria?: string } => {
    const { targetingCriteria, householdIds, individualIds } = values;
    const errors: { targetingCriteria?: string } = {};
    if (!targetingCriteria.length && !householdIds && !individualIds) {
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
    exclusionReason: Yup.string().max(500, t('Too long')),
    programCycleId: Yup.object().shape({
      value: Yup.string().required('Program Cycle is required'),
    }),
  });

  const handleSubmit = async (values): Promise<void> => {
    try {
      await mutate({
        variables: {
          paymentPlanId: values.id,
          fspId: values.targetingCriteria[0]?.fsp,
          deliveryMechanismCode: values.targetingCriteria[0]?.deliveryMechanism,
          excludedIds: values.excludedIds,
          exclusionReason: values.exclusionReason,
          programCycleId: values.programCycleId.value,
          ...(paymentPlan.status === PaymentPlanStatus.TpOpen && {
            name: values.name,
          }),
          ...getTargetingCriteriaVariables({
            flagExcludeIfActiveAdjudicationTicket:
              values.flagExcludeIfActiveAdjudicationTicket,
            flagExcludeIfOnSanctionList: values.flagExcludeIfOnSanctionList,
            criterias: values.targetingCriteria,
          }),
        },
      });
      showMessage(t('Target Population Updated'));
      navigate(`/${baseUrl}/target-population/${values.id}`);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
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
            loading={loading}
            baseUrl={baseUrl}
            targetPopulation={paymentPlan}
            data-cy="edit-target-population-header"
          />
          <PaperContainer data-cy="paper-container">
            <Box pt={3} pb={3}>
              <Typography variant="h6">{t('Targeting Criteria')}</Typography>
            </Box>
            <Grid container mb={5}>
              <Grid size={{ xs: 6 }}>
                <ProgramCycleAutocompleteRest
                  value={values.programCycleId}
                  onChange={async (e) => {
                    await setFieldValue('programCycleId', e);
                  }}
                  required
                  // @ts-ignore
                  error={errors.programCycleId?.value}
                  data-cy="program-cycle-autocomplete"
                />
              </Grid>
            </Grid>
            <Grid container>
              <Grid size={{ xs: 6 }}>
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
