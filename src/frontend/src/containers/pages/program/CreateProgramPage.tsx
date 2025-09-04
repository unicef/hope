import { BaseSection } from '@components/core/BaseSection';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { DetailsStep } from '@components/programs/CreateProgram/DetailsStep';
import { PartnersStep } from '@components/programs/CreateProgram/PartnersStep';
import { ProgramFieldSeriesStep } from '@components/programs/CreateProgram/ProgramFieldSeriesStep';
import {
  handleNext,
  ProgramStepper,
} from '@components/programs/CreateProgram/ProgramStepper';
import { programValidationSchema } from '@components/programs/CreateProgram/programValidationSchema';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Fade } from '@mui/material';
import { PaginatedAreaTreeList } from '@restgenerated/models/PaginatedAreaTreeList';
import { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import type { ProgramCreate } from '@restgenerated/models/ProgramCreate';
import { UserChoices } from '@restgenerated/models/UserChoices';
import { RestService } from '@restgenerated/services/RestService';
import type { DefaultError } from '@tanstack/query-core';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  mapPartnerChoicesWithoutUnicef,
  showApiErrorMessages,
  deepUnderscore,
} from '@utils/utils';
import { Formik } from 'formik';
import { omit } from 'lodash';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { hasPermissionInModule } from '../../../config/permissions';

export const CreateProgramPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const permissions = usePermissions();
  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { data: treeData, isLoading: treeLoading } =
    useQuery<PaginatedAreaTreeList>({
      queryKey: ['allAreasTree', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasGeoAreasAllAreasTreeList({
          businessAreaSlug: businessArea,
        }),
    });

  const { data: userPartnerChoicesData, isLoading: userPartnerChoicesLoading } =
    useQuery<UserChoices>({
      queryKey: ['userChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasUsersChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<ProgramChoices>({
      queryKey: ['programChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasProgramsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
      staleTime: 1000 * 60 * 10,
      gcTime: 1000 * 60 * 30,
    });

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
      values.partnerAccess === 'SELECTED_PARTNERS_ACCESS'
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
    const pduFieldsToSendRaw = pduFieldsWithReplacedNulls.every(
      arePduFieldsEqual,
    )
      ? null
      : pduFieldsWithReplacedNulls.length > 0
        ? pduFieldsWithReplacedNulls
        : null;
    const pduFieldsToSend = pduFieldsToSendRaw
      ? deepUnderscore(pduFieldsToSendRaw)
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
        endDate:
          requestValues.endDate === '' || requestValues.endDate === undefined
            ? null
            : requestValues.endDate,
        pduFields: pduFieldsToSend || [],
        partners: partnersToSet,
        partnerAccess: values.partnerAccess,
      };

      const response = await createProgram(programData);

      showMessage('Programme created.');
      navigate(`/${baseUrl}/details/${response.slug}`);
    } catch (error: any) {
      showApiErrorMessages(error, showMessage);
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
    partnerAccess: 'ALL_PARTNERS_ACCESS',
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

  if (treeLoading || userPartnerChoicesLoading || choicesLoading)
    return <LoadingComponent />;

  if (!treeData || !userPartnerChoicesData || !choicesData) return null;

  const { partnerChoicesTemp: userPartnerChoices } = userPartnerChoicesData;

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
                        pdusubtypeChoicesData={choicesData.pduSubtypeChoices}
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
                        allAreasTreeData={treeData || []}
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
