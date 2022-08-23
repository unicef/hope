import { Typography } from '@material-ui/core';
import { Label } from '@material-ui/icons';
import { Form, Formik, FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import * as Yup from 'yup';
import { TARGET_POPULATION_QUERY } from '../../../apollo/queries/targeting/TargetPopulation';
import { TargetPopulationHouseholdTable } from '../../../containers/tables/targeting/TargetPopulationHouseholdTable';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';
import {
  getFullNodeFromEdgesById,
  handleValidationErrors,
} from '../../../utils/utils';
import {
  useAllProgramsQuery,
  useGoldenRecordByTargetingCriteriaQuery,
  useUpdateTpMutation,
} from '../../../__generated__/graphql';
import { Exclusions } from '../CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../PaperContainer';
import { Results } from '../Results';
import { TargetingCriteria } from '../TargetingCriteria';
import { TargetPopulationProgramme } from '../TargetPopulationProgramme';
import { EditTargetPopulationHeader } from './EditTargetPopulationHeader';

interface EditTargetPopulationProps {
  targetPopulationCriterias?;
  cancelEdit?;
  targetPopulation?;
}

export function EditTargetPopulation({
  targetPopulationCriterias,
  cancelEdit,
  targetPopulation,
}: EditTargetPopulationProps): React.ReactElement {
  const { t } = useTranslation();
  const initialValues = {
    id: targetPopulation.id,
    name: targetPopulation.name || '',
    program: targetPopulation.program?.id || '',
    criterias: targetPopulationCriterias.rules || [],
    targetingCriteria: targetPopulation.targetingCriteria.rules || [],
    excludedIds: targetPopulation.excludedIds || '',
    exclusionReason: targetPopulation.exclusionReason || '',
    candidateListCriterias: targetPopulationCriterias.rules || [],
  };
  console.log('initialValues', initialValues);
  const [mutate, { loading }] = useUpdateTpMutation();
  const { showMessage } = useSnackbar();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const {
    data: allProgramsData,
    loading: loadingPrograms,
  } = useAllProgramsQuery({
    variables: { businessArea, status: ['ACTIVE'] },
    fetchPolicy: 'cache-and-network',
  });

  const handleValidate = (values): { candidateListCriterias?: string } => {
    const { candidateListCriterias } = values;
    const errors: { candidateListCriterias?: string } = {};
    if (!candidateListCriterias.length) {
      errors.candidateListCriterias = t(
        'You need to select at least one targeting criteria',
      );
    }
    return errors;
  };
  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .min(2, 'Too short')
      .max(255, 'Too long'),
    excludedIds: Yup.string().test(
      'testName',
      'ID is not in the correct format',
      (ids) => {
        if (!ids?.length) {
          return true;
        }
        const idsArr = ids.split(',');
        return idsArr.every((el) =>
          /^\s*(IND|HH)-\d{2}-\d{4}\.\d{4}\s*$/.test(el),
        );
      },
    ),
    exclusionReason: Yup.string().max(500, t('Too long')),
  });

  const handleSubmit = async (values, { setFieldError }): Promise<void> => {
    try {
      await mutate({
        variables: {
          input: {
            id: values.id,
            programId: values.program,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            ...(targetPopulation.status === 'DRAFT' && {
              name: values.name,
            }),
            ...getTargetingCriteriaVariables({
              criterias: values.candidateListCriterias,
            }),
          },
        },
        refetchQueries: () => [
          {
            query: TARGET_POPULATION_QUERY,
            variables: {
              id,
            },
          },
        ],
      });
      cancelEdit();
      showMessage(t('Target Population Updated'), {
        pathname: `/${businessArea}/target-population/${values.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      const { nonValidationErrors } = handleValidationErrors(
        'updateTargetPopulation',
        e,
        setFieldError,
        showMessage,
      );
      if (nonValidationErrors.length > 0) {
        showMessage(t('Unexpected problem while creating Target Population'));
      }
    }
  };

  // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
  const selectedProgram = (values) =>
    getFullNodeFromEdgesById(
      allProgramsData?.allPrograms?.edges,
      values.program,
    );

  return (
    <Formik
      initialValues={initialValues}
      validate={handleValidate}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ values, submitForm }) => (
        <Form>
          <EditTargetPopulationHeader
            handleSubmit={submitForm}
            cancelEdit={cancelEdit}
            values={values}
            loading={loading}
            businessArea={businessArea}
            targetPopulation={targetPopulation}
          />
          <TargetPopulationProgramme
            allPrograms={allProgramsData}
            loading={loadingPrograms}
            program={values.program}
          />

          <FieldArray
            name='candidateListCriterias'
            render={(arrayHelpers) => (
              <TargetingCriteria
                helpers={arrayHelpers}
                candidateListRules={values.candidateListCriterias}
                isEdit
                selectedProgram={selectedProgram(values)}
              />
            )}
          />
          <Exclusions initialOpen={Boolean(values.excludedIds)} />
          {values.candidateListCriterias.length && selectedProgram(values) ? (
            <TargetPopulationHouseholdTable
              variables={{
                ...getTargetingCriteriaVariables({
                  criterias: values.targetingCriteria,
                }),
                program: selectedProgram(values).id,
                excludedIds: values.excludedIds,
                businessArea,
              }}
              query={useGoldenRecordByTargetingCriteriaQuery}
              queryObjectName='goldenRecordByTargetingCriteria'
            />
          ) : (
            <PaperContainer>
              <Typography variant='h6'>
                {t('Target Population Entries (Households)')}
              </Typography>
              <Label>{t('Add targeting criteria to see results.')}</Label>
            </PaperContainer>
          )}
        </Form>
      )}
    </Formik>
  );
}
