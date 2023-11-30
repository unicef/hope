import { Box, Button, Step, StepButton, Stepper } from '@material-ui/core';
import { Formik } from 'formik';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import {
  AllProgramsForChoicesDocument,
  useAllAreasTreeQuery,
  useCreateProgramMutation,
  useUserPartnerChoicesQuery,
} from '../../../__generated__/graphql';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { DetailsStep } from '../../../components/programs/CreateProgram/DetailsStep';
import { PartnersStep } from '../../../components/programs/CreateProgram/PartnersStep';
import { programValidationSchema } from '../../../components/programs/CreateProgram/programValidationSchema';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';

export const CreateProgramPage = (): ReactElement => {
  const { t } = useTranslation();

  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data: treeData, loading: treeLoading } = useAllAreasTreeQuery({
    variables: { businessArea },
  });
  const {
    data: userPartnerChoicesData,
    loading: userPartnerChoicesLoading,
  } = useUserPartnerChoicesQuery();

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
            budget: parseFloat(values.budget).toFixed(2),
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
    partners: [],
  };

  if (treeLoading || userPartnerChoicesLoading) return <LoadingComponent />;
  if (!treeData || !userPartnerChoicesData) return null;

  const { allAreasTree } = treeData;
  const { userPartnerChoices } = userPartnerChoicesData;

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        handleSubmit(values);
      }}
      validationSchema={programValidationSchema(t)}
    >
      {({ submitForm, values }) => {
        return (
          <>
            <PageHeader title={t('Create Programme')}>
              <Box display='flex' alignItems='center'>
                <Button
                  data-cy='button-cancel'
                  component={Link}
                  to={`/${baseUrl}/list`}
                >
                  {t('Cancel')}
                </Button>
                <Button
                  data-cy='button-save'
                  variant='contained'
                  color='primary'
                  onClick={submitForm}
                >
                  {t('Save')}
                </Button>
              </Box>
            </PageHeader>
            <Box p={6}>
              <Stepper activeStep={step}>
                <Step>
                  <StepButton
                    data-cy='step-button-details'
                    onClick={() => setStep(0)}
                  >
                    {t('Details')}
                  </StepButton>
                </Step>
                <Step>
                  <StepButton
                    data-cy='step-button-partners'
                    onClick={() => setStep(1)}
                  >
                    {t('Programme Partners')}
                  </StepButton>
                </Step>
              </Stepper>
              {step === 0 && (
                <DetailsStep values={values} step={step} setStep={setStep} />
              )}
              {step === 1 && (
                <PartnersStep
                  values={values}
                  allAreasTreeData={allAreasTree}
                  partnerChoices={userPartnerChoices}
                  step={step}
                  setStep={setStep}
                />
              )}
            </Box>
          </>
        );
      }}
    </Formik>
  );
};
