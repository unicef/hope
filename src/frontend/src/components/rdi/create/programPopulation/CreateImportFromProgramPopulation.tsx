/* eslint-disable react-hooks/exhaustive-deps */
import { LoadingComponent } from '@components/core/LoadingComponent';
import { useCreateRegistrationProgramPopulationImportMutation } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { FormikRadioGroup } from '@shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { Field, FormikProvider, useFormik } from 'formik';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import * as Yup from 'yup';
import { ScreenBeneficiaryField } from '../ScreenBeneficiaryField';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';

export const CreateImportFromProgramPopulationForm = ({
  setSubmitForm,
  setSubmitDisabled,
}): ReactElement => {
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [createImport] = useCreateRegistrationProgramPopulationImportMutation();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const regex = isSocialDctType
    ? /^\s*(IND)-\d{2}-\d{4}\.\d{4}\s*$/
    : /^\s*(HH)-\d{2}-\d{4}\.\d{4}\s*$/;

  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .required('Title is required')
      .min(4, 'Too short')
      .max(255, 'Too long'),
    importFromProgramId: Yup.string().required('Programme is required'),
    importType: Yup.string(),
    // eslint-disable-next-line @typescript-eslint/no-shadow
    importFromIds: Yup.string().when('importType', ([importType], schema) =>
      importType === 'usingIds'
        ? schema
            .required('IDs are required')
            .test('testName', 'ID is not in the correct format', (ids) => {
              if (!ids?.length) {
                return true;
              }
              const idsArr = ids.split(',');
              return idsArr.every((el) => regex.test(el));
            })
        : schema,
    ),
  });

  const queryVariables = {
    businessAreaSlug: businessArea,
    beneficiaryGroupMatch: programId,
    compatibleDct: programId,
    first: 100,
  };

  const { data: programsData, isLoading: programsDataLoading } =
    useQuery<PaginatedProgramListList>({
      queryKey: ['businessAreasProgramsList', queryVariables],
      queryFn: () => RestService.restBusinessAreasProgramsList(queryVariables),
    });

  const onSubmit = async (values): Promise<void> => {
    setSubmitDisabled(true);
    try {
      const data = await createImport({
        variables: {
          registrationDataImportData: {
            name: values.name,
            screenBeneficiary: values.screenBeneficiary,
            importFromProgramId: values.importFromProgramId,
            importFromIds: values.importFromIds,
            businessAreaSlug: businessArea,
          },
        },
      });
      navigate(
        `/${baseUrl}/registration-data-import/${data.data.registrationProgramPopulationImport.registrationDataImport.id}`,
      );
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
      setSubmitDisabled(false);
    }
  };

  const formik = useFormik({
    initialValues: {
      name: '',
      screenBeneficiary: false,
      importFromIds: '',
      importType: 'all',
      importFromProgramId: '',
    },
    validationSchema,
    onSubmit,
  });

  const { values } = formik;

  useEffect(() => {
    setSubmitForm(formik.submitForm);
  }, [formik.submitForm]);

  useEffect(() => {
    if (formik.values.importType !== 'usingIds') {
      formik.setFieldValue('importFromIds', '');
    }
  }, [formik.values.importType]);

  if (programsDataLoading) return <LoadingComponent />;
  if (!programsData) return null;

  const mappedProgramChoices = programsData.results.map((element) => ({
    name: element.name,
    value: element.id,
  }));

  return (
    <FormikProvider value={formik}>
      <Box mt={2}>
        <Field
          name="name"
          fullWidth
          label={t('Title')}
          required
          variant="outlined"
          component={FormikTextField}
        />
      </Box>
      <ScreenBeneficiaryField />
      <Box mt={2}>
        <Field
          name="importFromProgramId"
          label={t('Programme Name')}
          fullWidth
          variant="outlined"
          choices={mappedProgramChoices}
          component={FormikSelectField}
        />
      </Box>
      <Box mt={2}>
        <Field
          name="importType"
          data-cy="checkbox-verification-channel"
          choices={[
            {
              value: 'all',
              name: 'All Programme Population',
              dataCy: 'radio-all',
            },
            { value: 'usingIds', name: 'Using Ids', dataCy: 'radio-ids' },
          ]}
          component={FormikRadioGroup}
          alignItems="center"
        />
      </Box>
      {values.importType === 'usingIds' && (
        <Box mt={2}>
          <Field
            data-cy="input-import-from-ids"
            name="importFromIds"
            fullWidth
            multiline
            variant="outlined"
            label={t(
              isSocialDctType
                ? `${beneficiaryGroup?.memberLabelPlural} IDs`
                : `${beneficiaryGroup?.groupLabelPlural} IDs`,
            )}
            component={FormikTextField}
          />
        </Box>
      )}
    </FormikProvider>
  );
};
