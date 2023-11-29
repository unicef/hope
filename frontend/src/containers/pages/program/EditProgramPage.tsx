import { Box, Button, Step, StepButton, Stepper } from '@material-ui/core';
import { Formik } from 'formik';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import {
  useAllAreasTreeQuery,
  useProgramQuery,
  useUpdateProgramMutation,
  useUserPartnerChoicesQuery,
} from '../../../__generated__/graphql';
import { ALL_LOG_ENTRIES_QUERY } from '../../../apollo/queries/core/AllLogEntries';
import { PROGRAM_QUERY } from '../../../apollo/queries/program/Program';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { DetailsStep } from '../../../components/programs/CreateProgram/DetailsStep';
import { PartnersStep } from '../../../components/programs/CreateProgram/PartnersStep';
import { programValidationSchema } from '../../../components/programs/CreateProgram/programValidationSchema';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { decodeIdString } from '../../../utils/utils';

export const EditProgramPage = (): ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();

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

  const [mutate] = useUpdateProgramMutation({
    refetchQueries: [
      {
        query: ALL_LOG_ENTRIES_QUERY,
        variables: {
          objectId: decodeIdString(id),
          count: 5,
          businessArea,
        },
      },
    ],
    update(cache, { data: { updateProgram } }) {
      cache.writeQuery({
        query: PROGRAM_QUERY,
        variables: { id },
        data: { program: updateProgram.program },
      });
    },
  });

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
    version,
    partners,
  } = data.program;

  const handleSubmit = async (values): Promise<void> => {
    try {
      const response = await mutate({
        variables: {
          programData: {
            id,
            ...values,
            budget: parseFloat(values.budget).toFixed(2),
          },
          version,
        },
      });
      showMessage(t('Programme edited.'), {
        pathname: `/${baseUrl}/details/${response.data.updateProgram.program.id}`,
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const initialValues = {
    name,
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
    partners: partners.map((partner) => ({
      id: partner.id,
      adminAreas: partner.adminAreas,
      areaAccess: partner.areaAccess,
    })),
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
            <PageHeader title={`${t('Edit Programme')}: (${name})`}>
              <Box display='flex' alignItems='center'>
                <Button
                  component={Link}
                  data-cy='button-cancel'
                  to={`/${baseUrl}/details/${id}`}
                >
                  {t('Cancel')}
                </Button>
                <Button
                  variant='contained'
                  color='primary'
                  onClick={submitForm}
                  data-cy='button-save'
                >
                  {t('Save')}
                </Button>
              </Box>
            </PageHeader>
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
          </>
        );
      }}
    </Formik>
  );
};
