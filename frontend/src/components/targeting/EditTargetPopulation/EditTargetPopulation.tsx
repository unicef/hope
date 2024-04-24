import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import {
  TargetPopulationQuery,
  TargetPopulationStatus,
  useUpdateTpMutation,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Divider, Grid, Typography } from '@mui/material';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { getTargetingCriteriaVariables } from '@utils/targetingUtils';
import { Field, FieldArray, Form, Formik } from 'formik';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import * as Yup from 'yup';
import { AndDivider, AndDividerLabel } from '../AndDivider';
import { Exclusions } from '../CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../PaperContainer';
import { TargetingCriteria } from '../TargetingCriteria';
import { EditTargetPopulationHeader } from './EditTargetPopulationHeader';

interface EditTargetPopulationProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  screenBeneficiary: boolean;
}

export const EditTargetPopulation = ({
  targetPopulation,
  screenBeneficiary,
}: EditTargetPopulationProps): React.ReactElement => {
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
    householdIds: targetPopulation.targetingCriteria.householdIds,
    individualIds: targetPopulation.targetingCriteria.individualIds,
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

  const idValidation = Yup.string().test(
    'testName',
    'ID is not in the correct format',
    (ids) => {
      if (!ids?.length) {
        return true;
      }
      const idsArr = ids.split(',');
      return idsArr.every((el) =>
        /^\s*(IND|HH)-\d{2}-\d{4}\.\d{4}\s*$/.test(el),
      );
    },
  );

  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .min(3, 'Targeting name should have at least 3 characters.')
      .max(255, 'Targeting name should have at most 255 characters.'),
    excludedIds: idValidation,
    householdIds: idValidation,
    individualIds: idValidation,
    exclusionReason: Yup.string().max(500, t('Too long')),
  });

  const handleSubmit = async (values): Promise<void> => {
    try {
      await mutate({
        variables: {
          input: {
            id: values.id,
            programId: values.program,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            ...(targetPopulation.status === TargetPopulationStatus.Open && {
              name: values.name,
            }),
            ...getTargetingCriteriaVariables({
              flagExcludeIfActiveAdjudicationTicket:
                values.flagExcludeIfActiveAdjudicationTicket,
              flagExcludeIfOnSanctionList: values.flagExcludeIfOnSanctionList,
              criterias: values.targetingCriteria,
              householdIds: values.householdIds,
              individualIds: values.individualIds,
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
      {({ values, submitForm }) => (
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
                  <TargetingCriteria
                    helpers={arrayHelpers}
                    rules={values.targetingCriteria}
                    isEdit
                    screenBeneficiary={screenBeneficiary}
                    isStandardDctType={isStandardDctType}
                    isSocialDctType={isSocialDctType}
                    category={category}
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
                <Box mt={3} p={3}>
                  <Grid container spacing={3}>
                    {isStandardDctType && (
                      <Grid item xs={6}>
                        <Field
                          name="flagExcludeIfActiveAdjudicationTicket"
                          label={t(
                            'Exclude Households with Active Adjudication Ticket',
                          )}
                          color="primary"
                          component={FormikCheckboxField}
                          data-cy="input-active-households-adjudication-ticket"
                        />
                      </Grid>
                    )}
                    {isSocialDctType && (
                      <Grid item xs={6}>
                        <Field
                          name="flagExcludeIfActiveAdjudicationTicket"
                          label={t(
                            'Exclude People with Active Adjudication Ticket',
                          )}
                          color="primary"
                          component={FormikCheckboxField}
                          data-cy="input-active-people-adjudication-ticket"
                        />
                      </Grid>
                    )}
                    {screenBeneficiary && (
                      <Grid item xs={6}>
                        <Field
                          name="flagExcludeIfOnSanctionList"
                          label={t(
                            'Exclude Households with an active sanction screen flag',
                          )}
                          color="primary"
                          component={FormikCheckboxField}
                          data-cy="input-active-sanction-flag"
                        />
                      </Grid>
                    )}
                  </Grid>
                </Box>
              </>
            ) : null}
          </PaperContainer>
          {category === 'filters' && (
            <Exclusions initialOpen={Boolean(values.excludedIds)} />
          )}
          ,
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
