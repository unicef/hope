import { Box, Fade } from '@mui/material';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ProgramPartnerAccess,
  useAllAreasTreeQuery,
  usePduSubtypeChoicesDataQuery,
  useUserPartnerChoicesQuery,
} from '@generated/graphql';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import type { ProgramCreate } from '@restgenerated/models/ProgramCreate';
import type { DefaultError } from '@tanstack/query-core';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { DetailsStep } from '@components/programs/CreateProgram/DetailsStep';
import { PartnersStep } from '@components/programs/CreateProgram/PartnersStep';
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
import { programValidationSchema } from '@components/programs/CreateProgram/programValidationSchema';
import { useProgramContext } from 'src/programContext';
import { omit } from 'lodash';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { mapPartnerChoicesWithoutUnicef } from '@utils/utils';

export const CreateProgramPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const permissions = usePermissions();
  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { data: treeData, loading: treeLoading } = useAllAreasTreeQuery({
    variables: { businessArea },
  });
  const { data: userPartnerChoicesData, loading: userPartnerChoicesLoading } =
    useUserPartnerChoicesQuery();

  const { data: pdusubtypeChoicesData, loading: pdusubtypeChoicesLoading } =
    usePduSubtypeChoicesDataQuery();

  const queryClient = useQueryClient();

  const { mutateAsync: createProgram, isPending: loadingCreate } = useMutation<
    ProgramCreate,
    DefaultError,
    ProgramCreate
  >({
    mutationFn: (programData: ProgramCreate) => {
      return RestService.restBusinessAreasProgramsCreate({
        businessAreaSlug: businessArea,
        requestBody: programData,
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['programs', businessArea],
      });
      await queryClient.invalidateQueries({
        queryKey: ['programChoices', businessArea],
      });
    },
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
          }))
        : [];

    const requestValues = omit(values, ['editMode']);

    const initialPduFieldState = {
      label: '',
      pduData: {
        subtype: '',
        numberOfRounds: null,
        roundsNames: [],
      },
    };

    const arePduFieldsEqual = (pduField) => {
      const initialRoundsNames = initialPduFieldState.pduData.roundsNames.map(
        (name) => name || '',
      );
      const currentRoundsNames = pduField.pduData.roundsNames.map((name) =>
        name === null || name === undefined ? '' : name,
      );

      return (
        pduField.label === initialPduFieldState.label &&
        pduField.pduData.subtype === initialPduFieldState.pduData.subtype &&
        pduField.pduData.numberOfRounds ===
          initialPduFieldState.pduData.numberOfRounds &&
        currentRoundsNames.length === initialRoundsNames.length &&
        currentRoundsNames.every(
          (name, index) => name === initialRoundsNames[index],
        )
      );
    };

    // Function to replace null and undefined values, and ensure length consistency
    const transformPduField = (pduField) => {
      // Replace null and undefined values with empty strings
      const transformedRoundsNames = pduField.pduData.roundsNames.map((name) =>
        name === null || name === undefined ? '' : name,
      );

      // Adjust roundsNames length to match numberOfRounds
      while (transformedRoundsNames.length < pduField.pduData.numberOfRounds) {
        transformedRoundsNames.push('');
      }

      // Trim roundsNames if it's longer than numberOfRounds
      const finalRoundsNames = transformedRoundsNames.slice(
        0,
        pduField.pduData.numberOfRounds,
      );

      return {
        ...pduField,
        pduData: {
          ...pduField.pduData,
          roundsNames: finalRoundsNames,
        },
      };
    };

    const pduFieldsWithReplacedNulls = values.pduFields.map(transformPduField);

    const pduFieldsToSend = pduFieldsWithReplacedNulls.every(arePduFieldsEqual)
      ? null
      : pduFieldsWithReplacedNulls.length > 0
        ? pduFieldsWithReplacedNulls
        : null;

    try {
      const programData: ProgramCreate = {
        id: '', // Will be set by server
        slug: '', // Will be set by server
        version: 0, // Will be set by server
        status: '', // Will be set by server
        name: requestValues.name,
        programmeCode: requestValues.programmeCode || null,
        sector: requestValues.sector,
        description: requestValues.description || '',
        budget: budgetToFixed.toString(),
        administrativeAreasOfImplementation:
          requestValues.administrativeAreasOfImplementation || '',
        populationGoal: populationGoalParsed,
        cashPlus: requestValues.cashPlus,
        frequencyOfPayments: requestValues.frequencyOfPayments,
        dataCollectingType: requestValues.dataCollectingTypeCode,
        beneficiaryGroup: requestValues.beneficiaryGroup || '',
        startDate: requestValues.startDate,
        endDate: requestValues.endDate,
        pduFields: pduFieldsToSend || [],
        partners: partnersToSet,
        partnerAccess: values.partnerAccess,
      };

      const response = await createProgram(programData);

      showMessage('Programme created.');
      navigate(`/${baseUrl}/details/${response.id}`);
    } catch (error: any) {
      if (error?.body?.detail) {
        showMessage(error.body.detail);
      } else if (error?.message) {
        showMessage(error.message);
      } else {
        showMessage('An error occurred while creating the programme.');
      }
    }
  };

  const initialValues = {
    editMode: false,
    name: '',
    programmeCode: '',
    startDate: '',
    endDate: undefined,
    sector: '',
    dataCollectingTypeCode: '',
    beneficiaryGroup: '',
    description: '',
    budget: '',
    administrativeAreasOfImplementation: '',
    populationGoal: '',
    cashPlus: false,
    frequencyOfPayments: 'REGULAR',
    partners: [],
    partnerAccess: ProgramPartnerAccess.AllPartnersAccess,
    pduFields: [],
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
    ['pduField'],
    ['partnerAccess'],
  ];

  if (treeLoading || userPartnerChoicesLoading || pdusubtypeChoicesLoading)
    return <LoadingComponent />;

  if (!treeData || !userPartnerChoicesData || !pdusubtypeChoicesData)
    return null;

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
        handleSubmit(values);
      }}
      initialTouched={{
        programmeCode: true,
      }}
      validationSchema={programValidationSchema(t)}
      validationContext={{ programHasRdi: false, isCopy: false }}
      validateOnChange={true}
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
        const mappedPartnerChoices = mapPartnerChoicesWithoutUnicef(
          userPartnerChoices,
          values.partners,
        );

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
              `The Time Series Fields feature allows serial updating of ${beneficiaryGroup?.memberLabel} data through an XLSX file.`,
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
                <Fade in={step === 0} timeout={600}>
                  <div>
                    {step === 0 && (
                      <DetailsStep
                        values={values}
                        handleNext={handleNextStep}
                        errors={errors}
                      />
                    )}
                  </div>
                </Fade>
                <Fade in={step === 1} timeout={600}>
                  <div>
                    {step === 1 && (
                      <ProgramFieldSeriesStep
                        values={values}
                        handleNext={handleNextStep}
                        step={step}
                        setStep={setStep}
                        pdusubtypeChoicesData={pdusubtypeChoicesData}
                        errors={errors}
                        setFieldValue={setFieldValue}
                      />
                    )}
                  </div>
                </Fade>
                <Fade in={step === 2} timeout={600}>
                  <div>
                    {step === 2 && (
                      <PartnersStep
                        values={values}
                        allAreasTreeData={allAreasTree}
                        partnerChoices={mappedPartnerChoices}
                        step={step}
                        setStep={setStep}
                        submitForm={submitForm}
                        setFieldValue={setFieldValue}
                        loading={loadingCreate}
                      />
                    )}
                  </div>
                </Fade>
              </Box>
            </BaseSection>
          </>
        );
      }}
    </Formik>
  );
};

export default withErrorBoundary(CreateProgramPage, 'CreateProgramPage');
