import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import {
  TargetPopulationQuery,
  TargetPopulationStatus,
  useUpdateTpMutation,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Divider, Grid, Typography } from '@mui/material';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import {
  getTargetingCriteriaVariables,
  HhIdValidation,
  HhIndIdValidation,
  IndIdValidation,
} from '@utils/targetingUtils';
import { Field, FieldArray, Form, Formik } from 'formik';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import * as Yup from 'yup';
import { AndDivider, AndDividerLabel } from '../AndDivider';
import { Exclusions } from '../CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../PaperContainer';
import { EditTargetPopulationHeader } from './EditTargetPopulationHeader';
import { AddFilterTargetingCriteriaDisplay } from '../TargetingCriteriaDisplay/AddFilterTargetingCriteriaDisplay';
import { ProgramCycleAutocompleteRest } from '@shared/autocompletes/rest/ProgramCycleAutocompleteRest';
import { ReactElement } from 'react';
import { CreateAndEditTPCheckboxes } from '@containers/pages/targeting/CreateAndEditTPCheckboxes';

interface EditTargetPopulationProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  screenBeneficiary: boolean;
}

export const EditTargetPopulation = ({
  targetPopulation,
  screenBeneficiary,
}: EditTargetPopulationProps): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const initialValues = {
    id: targetPopulation.id,
    name: targetPopulation.name || '',
    program: targetPopulation.program?.id || '',
    targetingCriteria: targetPopulation.targetingCriteria.rules || [],
    excludedIds: targetPopulation.excludedIds || '',
    exclusionReason: targetPopulation.exclusionReason || '',
    flagExcludeIfActiveAdjudicationTicket:
      targetPopulation.targetingCriteria
        .flagExcludeIfActiveAdjudicationTicket || false,
    flagExcludeIfOnSanctionList:
      targetPopulation.targetingCriteria.flagExcludeIfOnSanctionList || false,
    programCycleId: {
      value: targetPopulation.programCycle.id,
      name: targetPopulation.programCycle.title,
    },
  };
  const [mutate, { loading }] = useUpdateTpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl } = useBaseUrl();
  const { selectedProgram, isSocialDctType, isStandardDctType } =
    useProgramContext();

  const category =
    targetPopulation.targetingCriteria?.rules.length !== 0 ? 'filters' : 'ids';

  const individualFiltersAvailable =
    selectedProgram?.dataCollectingType?.individualFiltersAvailable;
  const householdFiltersAvailable =
    selectedProgram?.dataCollectingType?.householdFiltersAvailable;

  const handleValidate = (values): { targetingCriteria?: string } => {
    const { targetingCriteria } = values;
    const errors: { targetingCriteria?: string } = {};
    if (!targetingCriteria.length && category === 'filters') {
      errors.targetingCriteria = t(
        'You need to select at least one targeting criteria',
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
          input: {
            id: values.id,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            programCycleId: values.programCycleId.value,
            ...(targetPopulation.status === TargetPopulationStatus.Open && {
              name: values.name,
            }),
            ...getTargetingCriteriaVariables({
              flagExcludeIfActiveAdjudicationTicket:
                values.flagExcludeIfActiveAdjudicationTicket,
              flagExcludeIfOnSanctionList: values.flagExcludeIfOnSanctionList,
              criterias: values.targetingCriteria,
            }),
          },
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
        <Form>
          <AutoSubmitFormOnEnter />
          <EditTargetPopulationHeader
            handleSubmit={submitForm}
            values={values}
            loading={loading}
            baseUrl={baseUrl}
            targetPopulation={targetPopulation}
            category={category}
          />
          <PaperContainer>
            <Box pt={3} pb={3}>
              <Typography variant="h6">{t('Targeting Criteria')}</Typography>
            </Box>
            <Grid container mb={5}>
              <Grid item xs={6}>
                <ProgramCycleAutocompleteRest
                  value={values.programCycleId}
                  onChange={async (e) => {
                    await setFieldValue('programCycleId', e);
                  }}
                  required
                  // @ts-ignore
                  error={errors.programCycleId?.value}
                />
              </Grid>
            </Grid>
            <Grid container>
              <Grid item xs={6}>
                <Field
                  name="name"
                  label={t('Target Population Name')}
                  type="text"
                  fullWidth
                  required
                  component={FormikTextField}
                  variant="outlined"
                  data-cy="input-name"
                  disabled={targetPopulation.status === 'LOCKED'}
                />
              </Grid>
            </Grid>
            <Box pt={6} pb={6}>
              <Divider />
            </Box>
            {category === 'filters' ? (
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
                  />
                )}
              />
            ) : null}
            {category === 'ids' ? (
              <>
                <Grid container spacing={3}>
                  {householdFiltersAvailable && (
                    <Grid item xs={12}>
                      <Field
                        data-cy="input-included-household-ids"
                        name="householdIds"
                        fullWidth
                        variant="outlined"
                        label={t('Household IDs')}
                        component={FormikTextField}
                      />
                    </Grid>
                  )}
                  {householdFiltersAvailable && individualFiltersAvailable && (
                    <Grid item xs={12}>
                      <AndDivider>
                        <AndDividerLabel>OR</AndDividerLabel>
                      </AndDivider>
                    </Grid>
                  )}
                  {individualFiltersAvailable && (
                    <Grid item xs={12}>
                      <Box pb={3}>
                        <Field
                          data-cy="input-included-individual-ids"
                          name="individualIds"
                          fullWidth
                          variant="outlined"
                          label={t('Individual IDs')}
                          component={FormikTextField}
                        />
                      </Box>
                    </Grid>
                  )}
                </Grid>
                <CreateAndEditTPCheckboxes
                  isStandardDctType={isStandardDctType}
                  isSocialDctType={isSocialDctType}
                  screenBeneficiary={screenBeneficiary}
                />
              </>
            ) : null}
          </PaperContainer>
          {category === 'filters' && (
            <Exclusions initialOpen={Boolean(values.excludedIds)} />
          )}
          <Box
            pt={3}
            pb={3}
            display="flex"
            flexDirection="column"
            alignItems="center"
          >
            <Typography style={{ color: '#b1b1b5' }} variant="h6">
              {t('Save to see the list of households')}
            </Typography>
            <Typography style={{ color: '#b1b1b5' }} variant="subtitle1">
              {t('List of households will be available after saving')}
            </Typography>
          </Box>
        </Form>
      )}
    </Formik>
  );
};
