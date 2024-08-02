// @ts-nocheck
import { Box } from '@mui/material';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import {
  ProgramPartnerAccess,
  useAllAreasTreeQuery,
  usePduSubtypeChoicesDataQuery,
  useProgramQuery,
  useUpdateProgramMutation,
  useUserPartnerChoicesQuery,
} from '@generated/graphql';
import { ALL_LOG_ENTRIES_QUERY } from '../../../apollo/queries/core/AllLogEntries';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { DetailsStep } from '@components/programs/CreateProgram/DetailsStep';
import { PartnersStep } from '@components/programs/CreateProgram/PartnersStep';
import { programValidationSchema } from '@components/programs/CreateProgram/programValidationSchema';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { decodeIdString } from '@utils/utils';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { hasPermissionInModule } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { ProgramFieldSeriesStep } from '@components/programs/CreateProgram/ProgramFieldSeriesStep';
import { BaseSection } from '@components/core/BaseSection';
import {
  handleNext,
  ProgramStepper,
} from '@components/programs/CreateProgram/ProgramStepper';

export const EditProgramPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();

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
  });

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
    programmeCode,
    startDate,
    endDate,
    sector,
    dataCollectingType,
    description,
    budget = '',
    administrativeAreasOfImplementation,
    populationGoal = '',
    cashPlus = false,
    frequencyOfPayments = 'REGULAR',
    version,
    partners,
    partnerAccess = ProgramPartnerAccess.AllPartnersAccess,
    registrationImports,
    pduFields,
  } = data.program;

  console.log(data.program);

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
        ? values.partners.map(({ id: partnerId, areas, areaAccess }) => ({
            partner: partnerId,
            areas: areaAccess === 'ADMIN_AREA' ? areas : [],
            areaAccess,
          }))
        : [];

    const { editMode, ...requestValues } = values;
    const pduFieldsToSend = values.pduFields
      .filter((item) => item.label !== '')
      .map(({ __typename, pduData, ...rest }) => ({
        ...rest,
        pduData: pduData
          ? Object.fromEntries(
              Object.entries(pduData).filter(
                ([key]) => key !== '__typename' && key !== 'id',
              ),
            )
          : pduData,
      }));

    try {
      const response = await mutate({
        variables: {
          programData: {
            id,
            ...requestValues,
            budget: budgetToFixed,
            populationGoal: populationGoalParsed,
            partners: partnersToSet,
            pduFields: pduFieldsToSend,
          },
          version,
        },
      });
      showMessage(t('Programme edited.'));
      navigate(`/${baseUrl}/details/${response.data.updateProgram.program.id}`);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const programHasRdi = registrationImports.totalCount > 0;

  const mappedPduFields = Object.entries(pduFields).map(([, field]) => {
    const { ...rest } = field;
    return {
      ...rest,
      label: JSON.parse(field.label)['English(EN)'],
    };
  });

  const initialValues = {
    editMode: true,
    name,
    programmeCode,
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
    pduFields: programHasRdi
      ? undefined
      : pduFields.length == 0
        ? [
            {
              label: '',
              pduData: {
                subtype: '',
                numberOfRounds: null,
                roundsNames: [],
              },
            },
          ]
        : mappedPduFields,
  };

  initialValues.budget =
    data.program.budget === '0.00' ? '' : data.program.budget;
  initialValues.populationGoal =
    data.program.populationGoal === 0 ? '' : data.program.populationGoal;

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
          <>
            <PageHeader
              title={`${t('Edit Programme')}: (${name})`}
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
                    programHasRdi={programHasRdi}
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
