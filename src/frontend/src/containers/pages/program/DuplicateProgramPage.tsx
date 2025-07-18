import { BaseSection } from '@components/core/BaseSection';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { DetailsStep } from '@components/programs/CreateProgram/DetailsStep';
import { editProgramDetailsValidationSchema } from '@components/programs/CreateProgram/editProgramValidationSchema';
import { PartnersStep } from '@components/programs/CreateProgram/PartnersStep';
import { ProgramFieldSeriesStep } from '@components/programs/CreateProgram/ProgramFieldSeriesStep';
import {
  handleNext,
  ProgramStepper,
} from '@components/programs/CreateProgram/ProgramStepper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Fade } from '@mui/material';
import { PaginatedAreaTreeList } from '@restgenerated/models/PaginatedAreaTreeList';
import { PartnerAccessEnum } from '@restgenerated/models/PartnerAccessEnum';
import { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { ProgramCopy } from '@restgenerated/models/ProgramCopy';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { UserChoices } from '@restgenerated/models/UserChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  decodeIdString,
  isPartnerVisible,
  mapPartnerChoicesWithoutUnicef,
  showApiErrorMessages,
} from '@utils/utils';
import { Formik } from 'formik';
import { omit } from 'lodash';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { hasPermissionInModule } from '../../../config/permissions';

const DuplicateProgramPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const [step, setStep] = useState(0);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();

  const queryClient = useQueryClient();

  const { mutateAsync: copyProgram, isPending: loadingCopy } = useMutation({
    mutationFn: (programData: ProgramCopy) => {
      return RestService.restBusinessAreasProgramsCopyCreate({
        businessAreaSlug: businessArea,
        slug: id,
        requestBody: programData,
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['businessAreaPrograms', businessArea],
      });
    },
  });

  const { data: treeData, isLoading: treeLoading } =
    useQuery<PaginatedAreaTreeList>({
      queryKey: ['allAreasTree', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasGeoAreasAllAreasTreeList({
          businessAreaSlug: businessArea,
        }),
    });
  const { data: program, isLoading: loadingProgram } = useQuery<ProgramDetail>({
    queryKey: ['businessAreaProgram', businessArea, id],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRetrieve({
        businessAreaSlug: businessArea,
        slug: id,
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

  const handleSubmit = async (values): Promise<void> => {
    const budgetValue = parseFloat(values.budget) ?? 0;
    const budgetToFixed = !Number.isNaN(budgetValue)
      ? budgetValue.toFixed(2)
      : 0;
    const partnersToSet =
      values.partnerAccess === 'SELECTED_PARTNERS_ACCESS'
        ? values.partners.map(({ id: partnerId, areas, areaAccess }) => ({
            partner: partnerId,
            areas: areaAccess === 'ADMIN_AREA' ? areas : [],
            areaAccess,
          }))
        : [];

    const requestValues = omit(values, ['editMode', 'beneficiaryGroup']);
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
      ? []
      : pduFieldsWithReplacedNulls.length > 0
        ? pduFieldsWithReplacedNulls
        : [];

    try {
      const programData = {
        programmeCode: requestValues.programmeCode,
        name: requestValues.name,
        sector: requestValues.sector,
        description: requestValues.description,
        budget: budgetToFixed.toString(),
        administrativeAreasOfImplementation:
          requestValues.administrativeAreasOfImplementation,
        populationGoal: parseInt(requestValues.populationGoal, 10) || 0,
        cashPlus: requestValues.cashPlus,
        frequencyOfPayments: requestValues.frequencyOfPayments,
        dataCollectingType: requestValues.dataCollectingTypeCode,
        beneficiaryGroup: requestValues.beneficiaryGroup,
        startDate: requestValues.startDate,
        endDate:
          requestValues.endDate === '' || requestValues.endDate === undefined
            ? null
            : requestValues.endDate,
        pduFields: pduFieldsToSend,
        partners: partnersToSet.map(({ partner, areas }) => ({
          partner,
          areas,
        })),
        partnerAccess: values.partnerAccess as PartnerAccessEnum,
      };

      await copyProgram(programData);
      showMessage('Programme created.');
      navigate(`/${baseUrl}/list`);
    } catch (e: any) {
      showApiErrorMessages(
        e,
        showMessage,
        t('Programme create action failed.'),
      );
    }
  };

  if (
    loadingProgram ||
    treeLoading ||
    userPartnerChoicesLoading ||
    choicesLoading
  )
    return <LoadingComponent />;
  if (!program || !treeData || !userPartnerChoicesData || !choicesData)
    return null;

  const {
    name,
    startDate,
    endDate,
    sector,
    dataCollectingType,
    beneficiaryGroup,
    description,
    budget = '',
    administrativeAreasOfImplementation,
    populationGoal = 0,
    cashPlus = false,
    frequencyOfPayments = 'REGULAR',
    partners,
    partnerAccess = 'ALL_PARTNERS_ACCESS',
  } = program;

  const initialValues = {
    editMode: true,
    name: `Copy of Programme: (${name})`,
    programmeCode: null,
    startDate,
    endDate,
    sector,
    dataCollectingTypeCode: dataCollectingType?.code,
    beneficiaryGroup: beneficiaryGroup?.id,
    description,
    budget,
    administrativeAreasOfImplementation: administrativeAreasOfImplementation,
    populationGoal,
    cashPlus,
    frequencyOfPayments,
    partners: partners
      .filter((partner) => isPartnerVisible(partner.name))
      .map((partner) => ({
        id: partner.id,
        areas: partner.areas.map((area) => decodeIdString(area.id)),
        areaAccess: partner.areaAccess,
      })),
    partnerAccess: partnerAccess,
    pduFields: [],
  };
  initialValues.budget = program.budget === '0.00' ? '' : program.budget;

  const stepFields = [
    [
      'name',
      'programmeCode',
      'startDate',
      'endDate',
      'sector',
      'dataCollectingTypeCode',
      'beneficiaryGroup',
      'description',
      'budget',
      'administrativeAreasOfImplementation',
      'populationGoal',
      'cashPlus',
      'frequencyOfPayments',
    ],
    ['partnerAccess'],
  ];

  const allAreasTree = treeData?.results || [];
  const { partnerChoicesTemp: userPartnerChoices } = userPartnerChoicesData;

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
      validationSchema={editProgramDetailsValidationSchema(t, initialValues)}
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
                <Fade in={step === 0} timeout={600}>
                  <div>
                    {step === 0 && (
                      <DetailsStep
                        values={values}
                        handleNext={handleNextStep}
                        programId={id}
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
                        programId={id}
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
                        programId={id}
                        loading={loadingCopy}
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
export default withErrorBoundary(DuplicateProgramPage, 'DuplicateProgramPage');
