import { Box } from '@mui/material';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllProgramsForChoicesDocument,
  ProgramPartnerAccess,
  useAllAreasTreeQuery,
  useCreateProgramMutation,
  useUserPartnerChoicesQuery,
} from '@generated/graphql';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { DetailsStep } from '@components/programs/CreateProgram/DetailsStep';
import { PartnersStep } from '@components/programs/CreateProgram/PartnersStep';
import { programValidationSchema } from '@components/programs/CreateProgram/programValidationSchema';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { hasPermissionInModule } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { useNavigate } from 'react-router-dom';
import { BaseSection } from '@components/core/BaseSection';
import { ProgramFieldSeriesStep } from '@components/programs/CreateProgram/ProgramFieldSeriesStep';
import {
  handleNext,
  ProgramStepper,
} from '@components/programs/CreateProgram/ProgramStepper';

export const CreateProgramPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const permissions = usePermissions();
  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();

  const { data: treeData, loading: treeLoading } = useAllAreasTreeQuery({
    variables: { businessArea },
  });
  const { data: userPartnerChoicesData, loading: userPartnerChoicesLoading } =
    useUserPartnerChoicesQuery();

  const [mutate] = useCreateProgramMutation({
    refetchQueries: () => [
      { query: ALL_PROGRAMS_QUERY, variables: { businessArea } },
    ],
  });

  const handleSubmit = async (values): Promise<void> => {
    const budgetValue = parseFloat(values.budget) ?? 0;
    const budgetToFixed = !Number.isNaN(budgetValue)
      ? budgetValue.toFixed(2)
      : 0;
    const populationGoalValue = parseInt(values.populationGoal, 10) ?? 0;
    const populationGoalParsed = !Number.isNaN(populationGoalValue)
      ? populationGoalValue
      : 0;
    const partnersToSet =
      values.partnerAccess === ProgramPartnerAccess.SelectedPartnersAccess
        ? values.partners.map(({ id, areas, areaAccess }) => ({
            partner: id,
            areas: areaAccess === 'ADMIN_AREA' ? areas : [],
            areaAccess,
          }))
        : [];
    const { editMode, ...requestValues } = values;
    const pduFieldsToSend =
      values.pduFields.length > 0 ? values.pduFields : null;

    try {
      const response = await mutate({
        variables: {
          programData: {
            ...requestValues,
            budget: budgetToFixed,
            populationGoal: populationGoalParsed,
            businessAreaSlug: businessArea,
            partners: partnersToSet,
            pduFields: pduFieldsToSend,
          },
        },
        refetchQueries: () => [
          {
            query: AllProgramsForChoicesDocument,
            variables: { businessArea, first: 100 },
          },
        ],
      });
      showMessage('Programme created.');
      navigate(`/${baseUrl}/details/${response.data.createProgram.program.id}`);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const initialValues = {
    editMode: false,
    name: '',
    programmeCode: '',
    startDate: '',
    endDate: '',
    sector: '',
    dataCollectingTypeCode: '',
    description: '',
    budget: '',
    administrativeAreasOfImplementation: '',
    populationGoal: '',
    cashPlus: false,
    frequencyOfPayments: 'REGULAR',
    partners: [],
    partnerAccess: ProgramPartnerAccess.AllPartnersAccess,
    pduFields: [
      {
        name: '',
        pduData: {
          subtype: '',
          numberOfRounds: null,
          roundsNames: [],
        },
      },
    ],
  };

  const stepFields = [
    [
      'name',
      'programmeCode',
      'startDate',
      'endDate',
      'sector',
      'dataCollectingTypeCode',
      'description',
      'budget',
      'administrativeAreasOfImplementation',
      'populationGoal',
      'cashPlus',
      'frequencyOfPayments',
    ],
    ['partnerAccess'],
  ];

  if (treeLoading || userPartnerChoicesLoading) return <LoadingComponent />;
  if (!treeData || !userPartnerChoicesData) return null;

  const { allAreasTree } = treeData;
  const { userPartnerChoices } = userPartnerChoicesData;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Programme Management'),
      to: `/${baseUrl}/list/`,
    },
  ];

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        console.log('values', values);
        handleSubmit(values);
      }}
      initialTouched={{
        programmeCode: true,
      }}
      //TODO MS: Uncomment when validation is ready
      // validationSchema={programValidationSchema(t)}
    >
      {({
        submitForm,
        values,
        validateForm,
        setFieldTouched,
        setFieldValue,
      }) => {
        const mappedPartnerChoices = userPartnerChoices
          .filter((partner) => partner.name !== 'UNICEF')
          .map((partner) => ({
            value: partner.value,
            label: partner.name,
            disabled: values.partners.some((p) => p.id === partner.value),
          }));

        const handleNextStep = async () => {
          await handleNext({
            validateForm,
            stepFields,
            step,
            setStep,
            setFieldTouched,
          });
        };

        const stepsData = [
          {
            title: t('Details'),
            description: t(
              'To create a new Programme, please complete all required fields on the form below and save.',
            ),
            dataCy: 'step-button-details',
          },
          {
            title: t('Programme Time Series Fields'),
            description: t(
              'The Time Series Fields feature allows serial updating of individual data through an XLSX file.',
            ),
            dataCy: 'step-button-time-series-fields',
          },
          {
            title: t('Programme Partners'),
            description: '',
            dataCy: 'step-button-partners',
          },
        ];

        const title = stepsData[step].title;
        const description = stepsData[step].description
          ? stepsData[step].description
          : undefined;

        return (
          <>
            <PageHeader
              title={t('New Programme')}
              breadCrumbs={
                hasPermissionInModule(
                  'PROGRAMME_VIEW_LIST_AND_DETAILS',
                  permissions,
                )
                  ? breadCrumbsItems
                  : null
              }
            />
            <BaseSection
              title={title}
              description={description}
              stepper={
                <ProgramStepper
                  step={step}
                  setStep={setStep}
                  stepsData={stepsData}
                />
              }
            >
              <Box p={3}>
                {step === 0 && (
                  <DetailsStep values={values} handleNext={handleNextStep} />
                )}
                {step === 1 && (
                  <ProgramFieldSeriesStep
                    values={values}
                    handleNext={handleNextStep}
                    step={step}
                    setStep={setStep}
                  />
                )}
                {step === 2 && (
                  <PartnersStep
                    values={values}
                    allAreasTreeData={allAreasTree}
                    partnerChoices={mappedPartnerChoices}
                    step={step}
                    setStep={setStep}
                    submitForm={submitForm}
                    setFieldValue={setFieldValue}
                  />
                )}
              </Box>
            </BaseSection>
          </>
        );
      }}
    </Formik>
  );
};
