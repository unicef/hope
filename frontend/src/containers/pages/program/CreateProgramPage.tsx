import { Box, Button, Step, StepButton, Stepper } from '@material-ui/core';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import * as Yup from 'yup';
import { Formik } from 'formik';
import moment from 'moment';
import {
  AllProgramsForChoicesDocument,
  useAllAreasTreeQuery,
  useCreateProgramMutation,
} from '../../../__generated__/graphql';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { DetailsStep } from '../../../components/programs/CreateProgram/DetailsStep';
import { PartnersStep } from '../../../components/programs/CreateProgram/PartnersStep';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
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
  const { data: treeData, loading: treeLoading } = useAllAreasTreeQuery({
    variables: { businessArea },
  });

  const [mutate] = useCreateProgramMutation({
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
    populationGoal: 0,
    cashPlus: false,
    frequencyOfPayments: 'REGULAR',
    partners,
  };

  if (treeLoading) return <LoadingComponent />;
  if (!treeData) return null;

  const { allAreasTree } = treeData;

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
                <StepButton onClick={() => setStep(0)}>
                  {t('Details')}
                </StepButton>
              </Step>
              <Step>
                <StepButton onClick={() => setStep(1)}>
                  {t('Programme Partners')}
                </StepButton>
              </Step>
            </Stepper>
            {step === 0 && (
              <DetailsStep values={values} step={step} setStep={setStep} />
            )}
            {step === 1 && (
              <PartnersStep values={values} allAreasTree={allAreasTree} />
            )}
          </>
        );
      }}
    </Formik>
  );
};
