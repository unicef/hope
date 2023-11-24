import { Box, Button, Step, StepLabel, Stepper } from '@material-ui/core';
import React, { ReactElement, useState } from 'react';
import AddIcon from '@material-ui/icons/Add';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import * as Yup from 'yup';

import {
  AllProgramsForChoicesDocument,
  useCreateProgramMutation,
} from '../../../__generated__/graphql';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { BaseSection } from '../../../components/core/BaseSection';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { PageHeader } from '../../../components/core/PageHeader';
import { ProgramPartnerCard } from '../../../components/programs/CreateProgram/ProgramPartnerCard';
import { ProgramPartnersSection } from '../../../components/programs/CreateProgram/ProgramPartnersSection';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { ProgramForm } from '../../forms/ProgramForm';
import { FieldArray, Formik } from 'formik';
import moment from 'moment';
import { today } from '../../../utils/utils';

export const CreateProgramPage = (): ReactElement => {
  const { t } = useTranslation();
  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .required(t('Programme name is required'))
      .min(2, t('Too short'))
      .max(150, t('Too long')),
    startDate: Yup.date().required(t('Start Date is required')),
    endDate: Yup.date()
      .required(t('End Date is required'))
      .min(today, t('End Date cannot be in the past'))
      .when(
        'startDate',
        (startDate, schema) =>
          startDate &&
          schema.min(
            startDate,
            `${t('End date have to be greater than')} ${moment(
              startDate,
            ).format('YYYY-MM-DD')}`,
          ),
        '',
      ),
    sector: Yup.string().required(t('Sector is required')),
    dataCollectingTypeCode: Yup.string().required(
      t('Data Collecting Type is required'),
    ),
    description: Yup.string()
      .min(2, t('Too short'))
      .max(255, t('Too long')),
    budget: Yup.number()
      .min(0)
      .max(99999999, t('Number is too big')),
    administrativeAreasOfImplementation: Yup.string()
      .min(2, t('Too short'))
      .max(255, t('Too long')),
    populationGoal: Yup.number()
      .min(0)
      .max(99999999, t('Number is too big')),
  });

  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const [mutate, { loading }] = useCreateProgramMutation({
    refetchQueries: () => [
      { query: ALL_PROGRAMS_QUERY, variables: { businessArea } },
    ],
  });

  const handleSubmit = async (values): Promise<void> => {
    try {
      const response = await mutate({
        variables: {
          programData: {
            ...values,
            startDate: values.startDate,
            endDate: values.endDate,
            businessAreaSlug: businessArea,
          },
        },
        refetchQueries: () => [
          {
            query: AllProgramsForChoicesDocument,
            variables: { businessArea, first: 100 },
          },
        ],
      });
      showMessage('Programme created.', {
        pathname: `/${baseUrl}/details/${response.data.createProgram.program.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const detailsDescription = t(
    'To create a new Programme, please complete all required fields on the form below and save.',
  );

  const partnersDescription = t(
    'Provide info about Programme Partner and set Area Access',
  );

  //TODO: remove this
  const partners = [{ id: uuidv4() }, { id: uuidv4() }, { id: uuidv4() }];

  const initialValues = {
    name: '',
    startDate: '',
    endDate: '',
    sector: '',
    dataCollectingTypeCode: '',
    description: '',
    budget: '0.00',
    administrativeAreasOfImplementation: '',
    populationGoal: null,
    cashPlus: false,
    frequencyOfPayments: 'REGULAR',
    partners,
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values, { setValues }) => {
        const newValues = { ...values };
        newValues.budget = Number(values.budget).toFixed(2);
        setValues(newValues);
        handleSubmit(values);
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm, values }) => {
        return (
          <>
            <PageHeader title={t('Create Programme')}>
              <Box display='flex' alignItems='center'>
                <Button component={Link} to={`${baseUrl}/list`}>
                  {t('Cancel')}
                </Button>
                <Button
                  variant='contained'
                  color='primary'
                  onClick={submitForm}
                >
                  {t('Save')}
                </Button>
              </Box>
            </PageHeader>
            <Stepper activeStep={step}>
              <Step>
                <StepLabel>{t('Details')}</StepLabel>
              </Step>
              <Step>
                <StepLabel>{t('Programme Partners')}</StepLabel>
              </Step>
            </Stepper>
            {step === 0 && (
              <BaseSection
                title={t('Details')}
                description={detailsDescription}
              >
                <>
                  <ProgramForm values={values} />
                  <Box display='flex' justifyContent='flex-end'>
                    <Box mr={2}>
                      <Button
                        variant='outlined'
                        onClick={() => setStep(step - 1)}
                        disabled={step === 0}
                      >
                        {t('Back')}
                      </Button>
                    </Box>
                    <Button
                      variant='contained'
                      color='primary'
                      onClick={() => setStep(step + 1)}
                    >
                      {t('Next')}
                    </Button>
                  </Box>
                </>
              </BaseSection>
            )}
            {step === 1 && (
              <BaseSection
                title={t('Programme Partners')}
                description={partnersDescription}
              >
                <FieldArray
                  name='partners'
                  render={(arrayHelpers) => (
                    <>
                      {values.partners.map((partner, index) => (
                        <ProgramPartnerCard
                          key={partner.id}
                          partner={partner}
                          index={index}
                          values={values}
                          arrayHelpers={arrayHelpers}
                        />
                      ))}
                      <Button
                        onClick={() => arrayHelpers.push({ id: uuidv4() })}
                        variant='outlined'
                        color='primary'
                        endIcon={<AddIcon />}
                      >
                        {t('Add Partner')}
                      </Button>
                    </>
                  )}
                />
              </BaseSection>
            )}
          </>
        );
      }}
    </Formik>
  );
};
