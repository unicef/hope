import { Box, Grid } from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, FieldArray, Form, Formik } from 'formik';
import moment from 'moment';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import * as Yup from 'yup';
import {
  useAllSteficonRulesQuery,
  useCreatePpMutation,
  useProgramCycleIdNameQuery,
} from '../../../__generated__/graphql';
import { AutoSubmitFormOnEnter } from '../../../components/core/AutoSubmitFormOnEnter';
import { BaseSection } from '../../../components/core/BaseSection';
import { DividerLine } from '../../../components/core/DividerLine';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { UniversalCriteriaPlainComponent } from '../../../components/core/UniversalCriteriaComponent/UniversalCriteriaPlainComponent';
import { CreatePaymentPlanHeaderProgramCycle } from '../../../components/paymentmodule/CreatePaymentPlanProgramCycle/CreatePaymentPlanHeaderProgramCycle/CreatePaymentPlanHeaderProgramCycle';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useCachedImportedIndividualFieldsQuery } from '../../../hooks/useCachedImportedIndividualFields';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { FormikDateField } from '../../../shared/Formik/FormikDateField';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { FormikCurrencyAutocomplete } from '../../../shared/FormikCurrencyAutocomplete';
import { associatedWith, isNot, today, tomorrow } from '../../../utils/utils';

export const CreatePaymentPlanPageProgramCycle = (): React.ReactElement => {
  const { t } = useTranslation();
  const [mutate, { loading: loadingCreate }] = useCreatePpMutation();
  const { showMessage } = useSnackbar();
  const { id } = useParams();
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const [individualData, setIndividualData] = useState(null);
  const [householdData, setHouseholdData] = useState(null);

  const {
    data: importedIndividualFieldsData,
    loading: importedIndividualFieldsDataLoading,
  } = useCachedImportedIndividualFieldsQuery(businessArea);

  useEffect(() => {
    if (importedIndividualFieldsDataLoading) return;
    const filteredIndividualData = {
      allFieldsAttributes: importedIndividualFieldsData?.allFieldsAttributes
        ?.filter(associatedWith('Individual'))
        .filter(isNot('IMAGE')),
    };
    setIndividualData(filteredIndividualData);

    const filteredHouseholdData = {
      allFieldsAttributes: importedIndividualFieldsData?.allFieldsAttributes?.filter(
        associatedWith('Household'),
      ),
    };
    setHouseholdData(filteredHouseholdData);
  }, [importedIndividualFieldsData, importedIndividualFieldsDataLoading]);

  const {
    data: programCycleData,
    loading: programCycleLoading,
  } = useProgramCycleIdNameQuery({
    variables: {
      id,
    },
  });
  const {
    data: steficonRulesData,
    loading: steficonRulesLoading,
  } = useAllSteficonRulesQuery({
    variables: { enabled: true, deprecated: false, type: 'PAYMENT_PLAN' },
  });

  if (
    !importedIndividualFieldsData ||
    !programCycleData ||
    !steficonRulesData ||
    permissions === null
  )
    return null;
  if (programCycleLoading || steficonRulesLoading) return <LoadingComponent />;

  if (!hasPermissions(PERMISSIONS.PM_CREATE, permissions))
    return <PermissionDenied />;

  const mappedFormulaChoices = steficonRulesData.allSteficonRules.edges.map(
    (el) => ({
      name: el.node.name,
      value: el.node.id,
    }),
  );

  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .required(t('Payment Plan Title is required'))
      .min(2, t('Too short'))
      .max(150, t('Too long')),
    description: Yup.string()
      .min(2, t('Too short'))
      .max(255, t('Too long')),
    dispersionStartDate: Yup.date().required(
      t('Dispersion Start Date is required'),
    ),
    dispersionEndDate: Yup.date()
      .required(t('Dispersion End Date is required'))
      .min(today, t('Dispersion End Date cannot be in the past'))
      .when(
        'dispersionStartDate',
        (dispersionStartDate, schema) =>
          dispersionStartDate &&
          schema.min(
            dispersionStartDate,
            `${t('Dispersion End Date has to be greater than')} ${moment(
              dispersionStartDate,
            ).format('YYYY-MM-DD')}`,
          ),
        '',
      ),
    currency: Yup.string().required(t('Currency is required')),
  });

  type FormValues = Yup.InferType<typeof validationSchema>;
  const initialValues: FormValues = {
    name: '',
    description: '',
    criteria: [],
    formula: '',
    dispersionStartDate: '',
    dispersionEndDate: '',
    currency: '',
  };

  const handleSubmit = async (values: FormValues): Promise<void> => {
    try {
      const res = await mutate({
        variables: {
          input: {
            businessAreaSlug: businessArea,
            ...values,
          },
        },
      });
      showMessage(t('Payment Plan Created'), {
        pathname: `/${baseUrl}/payment-module/payment-plans/${res.data.createPaymentPlan.paymentPlan.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
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
          <CreatePaymentPlanHeaderProgramCycle
            handleSubmit={submitForm}
            baseUrl={baseUrl}
            permissions={permissions}
            loadingCreate={loadingCreate}
            programCycle={programCycleData.programCycle}
          />
          <BaseSection title={t('Description')}>
            <Field
              name='description'
              multiline
              fullWidth
              variant='outlined'
              label={t('Description')}
              component={FormikTextField}
            />
          </BaseSection>
          <BaseSection title={t('Payment Plan Criteria')}>
            <Box display='flex' flexDirection='column'>
              <Box mb={3} mt={3}>
                <FieldArray
                  name='criteria'
                  render={(arrayHelpers) => (
                    <UniversalCriteriaPlainComponent
                      isEdit
                      arrayHelpers={arrayHelpers}
                      rules={values.criteria}
                      householdFieldsChoices={
                        householdData?.allFieldsAttributes || []
                      }
                      individualFieldsChoices={
                        individualData?.allFieldsAttributes || []
                      }
                    />
                  )}
                />
              </Box>
              <DividerLine />
              <Field
                name='formula'
                variant='outlined'
                label={t('Apply Additional Formula')}
                component={FormikSelectField}
                choices={mappedFormulaChoices}
              />
            </Box>
          </BaseSection>
          <BaseSection title={t('Parameters')}>
            <Grid container spacing={3}>
              <Grid item xs={3}>
                <Field
                  name='dispersionStartDate'
                  label={t('Dispersion Start Date')}
                  component={FormikDateField}
                  required
                  fullWidth
                  decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
                  tooltip={t(
                    'The first day from which payments could be delivered.',
                  )}
                />
              </Grid>
              <Grid item xs={3}>
                <Field
                  name='dispersionEndDate'
                  label={t('Dispersion End Date')}
                  component={FormikDateField}
                  required
                  minDate={tomorrow}
                  disabled={!values.dispersionStartDate}
                  initialFocusedDate={values.dispersionStartDate}
                  fullWidth
                  decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
                  tooltip={t(
                    'The last day on which payments could be delivered.',
                  )}
                />
              </Grid>
              <Grid item xs={3}>
                <Field
                  name='currency'
                  component={FormikCurrencyAutocomplete}
                  required
                />
              </Grid>
            </Grid>
          </BaseSection>
        </Form>
      )}
    </Formik>
  );
};
