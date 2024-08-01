// @ts-nocheck
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { DetailsStep } from '@components/programs/CreateProgram/DetailsStep';
import { PartnersStep } from '@components/programs/CreateProgram/PartnersStep';
import { programValidationSchema } from '@components/programs/CreateProgram/programValidationSchema';
import {
  AllProgramsForChoicesDocument,
  ProgramPartnerAccess,
  useAllAreasTreeQuery,
  useCopyProgramMutation,
  usePduSubtypeChoicesDataQuery,
  useProgramQuery,
  useUserPartnerChoicesQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { decodeIdString } from '@utils/utils';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { hasPermissionInModule } from '../../../config/permissions';
import { BaseSection } from '@components/core/BaseSection';
import { ProgramFieldSeriesStep } from '@components/programs/CreateProgram/ProgramFieldSeriesStep';
import {
  handleNext,
  ProgramStepper,
} from '@components/programs/CreateProgram/ProgramStepper';

export const DuplicateProgramPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
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
  const { data: userPartnerChoicesData, loading: userPartnerChoicesLoading } =
    useUserPartnerChoicesQuery();

  const { data: pdusubtypeChoicesData, loading: pdusubtypeChoicesLoading } =
    usePduSubtypeChoicesDataQuery();

  const handleSubmit = async (values): Promise<void> => {
    const budgetValue = parseFloat(values.budget) ?? 0;
    const budgetToFixed = !Number.isNaN(budgetValue)
      ? budgetValue.toFixed(2)
      : 0;
    const partnersToSet =
      values.partnerAccess === ProgramPartnerAccess.SelectedPartnersAccess
        ? values.partners.map(({ id: partnerId, areas, areaAccess }) => ({
            partner: partnerId,
            areas: areaAccess === 'ADMIN_AREA' ? areas : [],
            areaAccess,
          }))
        : [];
    const { editMode, ...requestValues } = values;
    const initialPduFieldState = {
      label: '',
      pduData: {
        subtype: '',
        numberOfRounds: null,
        roundsNames: [],
      },
    };

    const pduFieldsToSend = values.pduFields.every(
      (pduField) =>
        pduField.label === initialPduFieldState.label.englishEn &&
        pduField.pduData.subtype === initialPduFieldState.pduData.subtype &&
        pduField.pduData.numberOfRounds ===
          initialPduFieldState.pduData.numberOfRounds &&
        pduField.pduData.roundsNames.length ===
          initialPduFieldState.pduData.roundsNames.length,
    )
      ? null
      : values.pduFields.length > 0
        ? values.pduFields
        : null;

    try {
      const response = await mutate({
        variables: {
          programData: {
            id,
            ...requestValues,
            budget: budgetToFixed,
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
      navigate(`/${baseUrl}/details/${response.data.copyProgram.program.id}`);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  if (
    loadingProgram ||
    treeLoading ||
    userPartnerChoicesLoading ||
    pdusubtypeChoicesLoading
  )
    return <LoadingComponent />;
  if (!data || !treeData || !userPartnerChoicesData || !pdusubtypeChoicesData)
    return null;

  const {
    name,
    startDate,
    endDate,
    sector,
    dataCollectingType,
    description,
    budget = '',
    administrativeAreasOfImplementation,
    populationGoal = 0,
    cashPlus = false,
    frequencyOfPayments = 'REGULAR',
    partners,
    partnerAccess = ProgramPartnerAccess.AllPartnersAccess,
  } = data.program;

  const initialValues = {
    editMode: false,
    name: `Copy of Programme: (${name})`,
    programmeCode: '',
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
    partners: partners
      .filter((partner) => partner.name !== 'UNICEF')
      .map((partner) => ({
        id: partner.id,
        areas: partner.areas.map((area) => decodeIdString(area.id)),
        areaAccess: partner.areaAccess,
      })),
    partnerAccess,
    pduFields: [
      {
        label: '',
        pduData: {
          subtype: '',
          numberOfRounds: null,
          roundsNames: [],
        },
      },
    ],
  };
  initialValues.budget =
    data.program.budget === '0.00' ? '' : data.program.budget;

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

  const { allAreasTree } = treeData;
  const { userPartnerChoices } = userPartnerChoicesData;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Programme'),
      to: `/${baseUrl}/details/${id}`,
    },
  ];

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

  const stepTitle = stepsData[step].title;
  const stepDescription = stepsData[step].description
    ? stepsData[step].description
    : undefined;

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        handleSubmit(values);
      }}
      validationSchema={programValidationSchema(t)}
    >
      {({
        submitForm,
        values,
        validateForm,
        setFieldTouched,
        setFieldValue,
        errors,
        setErrors,
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
            values,
            setErrors,
          });
        };

        return (
          <>
            <PageHeader
              title={`${t('Copy of Programme')}: (${name})`}
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
              title={stepTitle}
              description={stepDescription}
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
                    pdusubtypeChoicesData={pdusubtypeChoicesData}
                    errors={errors}
                    setErrors={setErrors}
                    setFieldTouched={setFieldTouched}
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
