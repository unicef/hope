import { Box, Button, Step, StepButton, Stepper } from '@material-ui/core';
import { Formik } from 'formik';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import {
  AllProgramsForChoicesDocument,
  useAllAreasTreeQuery,
  useCopyProgramMutation,
  useProgramQuery,
  useUserPartnerChoicesQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { DetailsStep } from '../../../components/programs/CreateProgram/DetailsStep';
import { PartnersStep } from '../../../components/programs/CreateProgram/PartnersStep';
import { programValidationSchema } from '../../../components/programs/CreateProgram/programValidationSchema';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';

export const DuplicateProgramPage = (): ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const [mutate] = useCopyProgramMutation();
  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();

  const { data: treeData, loading: treeLoading } = useAllAreasTreeQuery({
    variables: { businessArea },
  });
  const { data, loading: loadingProgram } = useProgramQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: userPartnerChoicesData,
    loading: userPartnerChoicesLoading,
  } = useUserPartnerChoicesQuery();

  const handleSubmit = async (values): Promise<void> => {
    try {
      const response = await mutate({
        variables: {
          programData: {
            ...values,
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
        pathname: `/${baseUrl}/details/${response.data.copyProgram.program.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  if (loadingProgram || treeLoading || userPartnerChoicesLoading)
    return <LoadingComponent />;
  if (!data || !treeData || !userPartnerChoicesData) return null;

  const {
    name,
    startDate,
    endDate,
    sector,
    dataCollectingType,
    description,
    budget = '0.00',
    administrativeAreasOfImplementation,
    populationGoal = 0,
    cashPlus = false,
    frequencyOfPayments = 'REGULAR',
    partners,
  } = data.program;

  const initialValues = {
    name: `Copy of Programme: (${name})`,
    startDate,
    endDate,
    sector,
    dataCollectingTypeCode: dataCollectingType?.code,
    description,
    budget,
    administrativeAreasOfImplementation,
    populationGoal,
    cashPlus,
    frequencyOfPayments,
    partners,
  };

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
            <PageHeader title={`${t('Copy of Programme')}: (${name})`}>
              <Box display='flex' alignItems='center'>
                <Button component={Link} to={`/${baseUrl}/details/${id}`}>
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
              <PartnersStep
                values={values}
                allAreasTree={allAreasTree}
                partnerChoices={userPartnerChoices}
              />
            )}
          </>
        );
      }}
    </Formik>
  );
};
