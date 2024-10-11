import { Box, Divider, Grid, Typography } from '@mui/material';
import { Field, FieldArray, Form, Formik } from 'formik';
import { useLocation, useNavigate } from 'react-router-dom';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import {
  useBusinessAreaDataQuery,
  useCreateTpMutation,
} from '@generated/graphql';
import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { CreateTargetPopulationHeader } from '@components/targeting/CreateTargetPopulation/CreateTargetPopulationHeader';
import { Exclusions } from '@components/targeting/CreateTargetPopulation/Exclusions';
import { PaperContainer } from '@components/targeting/PaperContainer';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '@utils/targetingUtils';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useProgramContext } from 'src/programContext';
import { AndDivider, AndDividerLabel } from '@components/targeting/AndDivider';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { TargetingCriteriaDisplay } from '@components/targeting/TargetingCriteriaDisplay/TargetingCriteriaDisplay';
import { ProgramCycleAutocompleteRest } from '@shared/autocompletes/rest/ProgramCycleAutocompleteRest';

export const CreateTargetPopulationPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();
  const { selectedProgram, isSocialDctType, isStandardDctType } =
    useProgramContext();
  const initialValues = {
    name: '',
    criterias: [],
    program: programId,
    programCycleId: {
      value: '',
      name: '',
    },
    excludedIds: '',
    exclusionReason: '',
    flagExcludeIfActiveAdjudicationTicket: false,
    flagExcludeIfOnSanctionList: false,
    householdIds: '',
    individualIds: '',
  };
  const [mutate, { loading }] = useCreateTpMutation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const navigate = useNavigate();
  const location = useLocation();
  const category = location.state?.category;

  const { data: businessAreaData } = useBusinessAreaDataQuery({
    variables: { businessAreaSlug: businessArea },
  });

  if (permissions === null) return null;
  if (!businessAreaData) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  const screenBeneficiary = businessAreaData?.businessArea?.screenBeneficiary;
  const individualFiltersAvailable =
    selectedProgram?.dataCollectingType?.individualFiltersAvailable;
  const householdFiltersAvailable =
    selectedProgram?.dataCollectingType?.householdFiltersAvailable;

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
      .required(t('Targeting Name is required'))
      .min(3, t('Targeting Name should have at least 3 characters.'))
      .max(255, t('Targeting Name should have at most 255 characters.')),
    excludedIds: idValidation,
    householdIds: idValidation,
    individualIds: idValidation,
    exclusionReason: Yup.string().max(500, t('Too long')),
    programCycleId: Yup.object().shape({
      value: Yup.string().required('Program Cycle is required'),
    }),
  });

  const handleSubmit = async (values): Promise<void> => {
    try {
      const res = await mutate({
        variables: {
          input: {
            programId: values.program,
            programCycleId: values.programCycleId.value,
            name: values.name,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            businessAreaSlug: businessArea,
            ...getTargetingCriteriaVariables(values),
          },
        },
      });
      showMessage(t('Target Population Created'));
      navigate(
        `/${baseUrl}/target-population/${res.data.createTargetPopulation.targetPopulation.id}`,
      );
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ submitForm, values, setFieldValue, errors }) => (
        <Form>
          <AutoSubmitFormOnEnter />
          <CreateTargetPopulationHeader
            handleSubmit={submitForm}
            loading={loading}
            values={values}
            baseUrl={baseUrl}
            permissions={permissions}
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
                />
              </Grid>
            </Grid>
            <Box pt={6} pb={6}>
              <Divider />
            </Box>
            {values.program && category === 'filters' ? (
              <FieldArray
                name="criterias"
                render={(arrayHelpers) => (
                  <TargetingCriteriaDisplay
                    helpers={arrayHelpers}
                    rules={values.criterias}
                    screenBeneficiary={screenBeneficiary}
                    isStandardDctType={isStandardDctType}
                    isSocialDctType={isSocialDctType}
                    category={category}
                    isEdit
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
                    {screenBeneficiary && isSocialDctType && (
                      <Grid item xs={6}>
                        <Field
                          name="flagExcludeIfOnSanctionList"
                          label={t(
                            'Exclude People with an Active Sanction Screen Flag',
                          )}
                          color="primary"
                          component={FormikCheckboxField}
                          data-cy="input-active-people-sanction-flag"
                        />
                      </Grid>
                    )}
                    {screenBeneficiary && isStandardDctType && (
                      <Grid item xs={6}>
                        <Field
                          name="flagExcludeIfOnSanctionList"
                          label={t(
                            'Exclude Households with an Active Sanction Screen Flag',
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
          {category === 'filters' && <Exclusions />}
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
