import { Typography } from '@material-ui/core';
import { FieldArray, Form, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { CreateEnrollmentHeader } from '../../../components/enrollment/CreateEnrollment/CreateEnrollmentHeader';
import { EnrollmentCriteria } from '../../../components/enrollment/EnrollmentDetails/EnrollmentCriteria/EnrollmentCriteria';
import { Exclusions } from '../../../components/targeting/CreateTargetPopulation/Exclusions';
import { PaperContainer } from '../../../components/targeting/PaperContainer';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';
import {
  getFullNodeFromEdgesById,
  handleValidationErrors,
} from '../../../utils/utils';
import {
  ProgramStatus,
  useAllProgramsForChoicesQuery,
  useCreateTpMutation,
} from '../../../__generated__/graphql';

export const CreateEnrollmentPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const initialValues = {
    name: '',
    criterias: [],
    program: null,
    excludedIds: '',
    exclusionReason: '',
  };
  const [mutate, { loading }] = useCreateTpMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const {
    data: allProgramsData,
    loading: loadingPrograms,
  } = useAllProgramsForChoicesQuery({
    variables: { businessArea, status: [ProgramStatus.Active] },
    fetchPolicy: 'network-only',
  });

  if (loadingPrograms) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .min(2, t('Too short'))
      .max(255, t('Too long')),
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
      const res = await mutate({
        variables: {
          input: {
            programId: values.program,
            name: values.name,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            businessAreaSlug: businessArea,
            ...getTargetingCriteriaVariables(values),
          },
        },
      });
      showMessage(t('Target Population Created'), {
        pathname: `/${businessArea}/target-population/${res.data.createTargetPopulation.targetPopulation.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      const { nonValidationErrors } = handleValidationErrors(
        'createTargetPopulation',
        e,
        setFieldError,
        showMessage,
      );
      if (nonValidationErrors.length > 0) {
        showMessage(t('Unexpected problem while creating Target Population'));
      }
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ submitForm, values }) => (
        <Form>
          <CreateEnrollmentHeader
            handleSubmit={submitForm}
            loading={loading}
            values={values}
            businessArea={businessArea}
            permissions={permissions}
          />
          <FieldArray
            name='criterias'
            render={(arrayHelpers) => (
              <EnrollmentCriteria
                helpers={arrayHelpers}
                rules={values.criterias}
                selectedProgram={getFullNodeFromEdgesById(
                  allProgramsData?.allPrograms?.edges,
                  values.program,
                )}
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
      )}
    </Formik>
  );
};
