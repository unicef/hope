import { Typography } from '@material-ui/core';
import { FieldArray, Form, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';
import {
  getFullNodeFromEdgesById,
  handleValidationErrors,
} from '../../../utils/utils';
import {
  ProgramStatus,
  TargetPopulationQuery,
  TargetPopulationStatus,
  useAllProgramsForChoicesQuery,
  useUpdateTpMutation,
} from '../../../__generated__/graphql';
import { Exclusions } from '../../targeting/CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../../targeting/PaperContainer';
import { EnrollmentCriteria } from '../EnrollmentDetails/EnrollmentCriteria/EnrollmentCriteria';
import { EditEnrollmentHeader } from './EditEnrollmentHeader';

interface EditEnrollmentProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
}

export const EditEnrollment = ({
  targetPopulation,
}: EditEnrollmentProps): React.ReactElement => {
  const { t } = useTranslation();
  const initialValues = {
    id: targetPopulation.id,
    name: targetPopulation.name || '',
    program: targetPopulation.program?.id || '',
    targetingCriteria: targetPopulation.targetingCriteria.rules || [],
    excludedIds: targetPopulation.excludedIds || '',
    exclusionReason: targetPopulation.exclusionReason || '',
  };
  const [mutate, { loading }] = useUpdateTpMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const { data: allProgramsData } = useAllProgramsForChoicesQuery({
    variables: { businessArea, status: [ProgramStatus.Active] },
    fetchPolicy: 'cache-and-network',
  });

  const handleValidate = (values): { targetingCriteria?: string } => {
    const { targetingCriteria } = values;
    const errors: { targetingCriteria?: string } = {};
    if (!targetingCriteria.length) {
      errors.targetingCriteria = t(
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
            ...(targetPopulation.status === TargetPopulationStatus.Open && {
              name: values.name,
            }),
            ...getTargetingCriteriaVariables({
              criterias: values.targetingCriteria,
            }),
          },
        },
      });
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

  const selectedProgram = (values): void =>
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
      {({ values, submitForm }) => {
        return (
          <Form>
            <EditEnrollmentHeader
              handleSubmit={submitForm}
              values={values}
              loading={loading}
              businessArea={businessArea}
              targetPopulation={targetPopulation}
            />

            <FieldArray
              name='targetingCriteria'
              render={(arrayHelpers) => (
                <EnrollmentCriteria
                  helpers={arrayHelpers}
                  rules={values.targetingCriteria}
                  selectedProgram={selectedProgram(values)}
                  isEdit
                />
              )}
            />
            {/* //TODO: is it needed? */}
            <Exclusions />
            <PaperContainer>
              <Typography variant='h6'>
                {t('Save to see the list of enrollment entries.')}
              </Typography>
            </PaperContainer>
          </Form>
        );
      }}
    </Formik>
  );
};
