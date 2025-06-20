import { Button, Grid2 as Grid, Typography } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { Field, FieldArray } from 'formik';
import camelCase from 'lodash/camelCase';
import { useTranslation } from 'react-i18next';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { FormikFileField } from '@shared/Formik/FormikFileField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { AgencyField } from './AgencyField';
import { DocumentField } from './DocumentField';
import { FormikBoolFieldGrievances } from './FormikBoolFieldGrievances';
import { removeItemById } from './utils/helpers';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';

export interface AddIndividualDataChangeFieldProps {
  field: any;
  flexField?: boolean;
}
export function AddIndividualDataChangeField({
  field,
  flexField,
}: AddIndividualDataChangeFieldProps): ReactElement {
  let fieldProps;
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;

  switch (field.type) {
    case 'DECIMAL':
      fieldProps = {
        component: FormikTextField,
      };
      break;
    case 'INTEGER':
      fieldProps = {
        component: FormikTextField,
        type: 'number',
      };
      break;
    case 'STRING':
      fieldProps = {
        component: FormikTextField,
      };
      break;
    case 'SELECT_ONE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'SELECT_MANY':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
        multiple: true,
      };
      break;
    case 'SELECT_MULTIPLE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'DATE':
      fieldProps = {
        component: FormikDateField,
        decoratorEnd: <CalendarTodayRoundedIcon color="disabled" />,
      };
      break;

    case 'BOOL':
      fieldProps = {
        component: FormikBoolFieldGrievances,
        required: field.required,
      };
      break;
    case 'IMAGE':
      fieldProps = {
        component: FormikFileField,
      };
      break;
    default:
      fieldProps = {};
  }
  return (
    <>
      <Grid size={{ xs: 8 }}>
        <Field
          name={`individualData${flexField ? '.flexFields' : ''}.${camelCase(
            field.name,
          )}`}
          fullWidth
          variant="outlined"
          label={field.labelEn}
          required={field.required}
          disabled={isEditTicket}
          {...fieldProps}
        />
      </Grid>
      <Grid size={{ xs: 4 }} />
    </>
  );
}

export interface AddIndividualDataChangeProps {
  values;
  setFieldValue?;
}

function AddIndividualDataChange({
  values,
  setFieldValue,
}: AddIndividualDataChangeProps): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const { businessAreaSlug } = useBaseUrl();

  const { data, isLoading: loading } = useQuery({
    queryKey: ['addIndividualFieldsAttributes', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsAllAddIndividualsFieldsAttributesList(
        {
          businessAreaSlug,
        },
      ),
  });

  const { data: choicesData, isLoading: choicesLoading } = useQuery({
    queryKey: ['businessAreasGrievanceTicketsChoices', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
        businessAreaSlug,
      }),
  });

  const { data: individualChoicesData, isLoading: individualChoicesLoading } =
    useQuery({
      queryKey: ['individualChoices', businessAreaSlug],
      queryFn: () =>
        RestService.restBusinessAreasIndividualsChoicesRetrieve({
          businessAreaSlug,
        }),
    });

  const { data: countriesData, isLoading: countriesLoading } = useQuery({
    queryKey: ['countriesList'],
    queryFn: () => RestService.restLookupsCountryList({}),
  });

  if (
    loading ||
    choicesLoading ||
    individualChoicesLoading ||
    countriesLoading
  ) {
    return <LoadingComponent />;
  }

  const combinedData = {
    results: data?.results || [],
    countriesChoices: countriesData?.results || [],
    documentTypeChoices: choicesData?.documentTypeChoices || [],
    identityTypeChoices: individualChoicesData?.identityTypeChoices || [],
  };

  const flexFields =
    combinedData.results.filter((item) => item.isFlexField) || [];
  const coreFields =
    combinedData.results.filter((item) => !item.isFlexField) || [];

  return (
    !isEditTicket && (
      <>
        <Title>
          <Typography variant="h6">
            {t(`${beneficiaryGroup?.memberLabel} Data`)}
          </Typography>
        </Title>
        <Grid container spacing={3}>
          <Grid size={{ xs: 12 }}>{t('Core Fields')}</Grid>

          {coreFields.map((item) => (
            <AddIndividualDataChangeField key={item.name} field={item} />
          ))}
          {flexFields.length > 0 && (
            <Grid size={{ xs: 12 }}>{t('Flex Fields')}</Grid>
          )}
          {flexFields.map((item) => (
            <AddIndividualDataChangeField
              key={item.name}
              field={item}
              flexField
            />
          ))}
        </Grid>
        <Grid container spacing={3}>
          <FieldArray
            name="individualData.documents"
            render={(arrayHelpers) => (
              <>
                {values.individualData?.documents?.map((item) => {
                  const existingOrNewId = item.node?.id || item.id;
                  return (
                    <DocumentField
                      id={existingOrNewId}
                      key={`${existingOrNewId}-${item?.country}-${item?.type?.key}`}
                      onDelete={() =>
                        removeItemById(
                          values.individualData.documents,
                          existingOrNewId,
                          arrayHelpers,
                        )
                      }
                      countryChoices={combinedData.countriesChoices}
                      documentTypeChoices={combinedData.documentTypeChoices}
                      baseName="individualData.documents"
                      baseNameArray={values.individualData.documents}
                      setFieldValue={setFieldValue}
                      values={values}
                    />
                  );
                })}
                <Grid size={{ xs: 8 }} />
                <Grid size={{ xs: 12 }}>
                  <Button
                    color="primary"
                    startIcon={<AddCircleOutline />}
                    disabled={isEditTicket}
                    onClick={() => {
                      arrayHelpers.push({
                        id: crypto.randomUUID(),
                        country: null,
                        key: null,
                        number: '',
                      });
                    }}
                  >
                    {t('Add Document')}
                  </Button>
                </Grid>
              </>
            )}
          />
        </Grid>
        <Grid container spacing={3}>
          <FieldArray
            name="individualData.identities"
            render={(arrayHelpers) => (
              <>
                {values.individualData?.identities?.map((item) => {
                  const existingOrNewId = item.node?.id || item.id;
                  return (
                    <AgencyField
                      key={existingOrNewId}
                      id={existingOrNewId}
                      onDelete={() =>
                        removeItemById(
                          values.individualData.identities,
                          existingOrNewId,
                          arrayHelpers,
                        )
                      }
                      countryChoices={combinedData.countriesChoices}
                      identityTypeChoices={combinedData.identityTypeChoices}
                      baseName="individualData.identities"
                      baseNameArray={values.individualData.identities}
                      values={values}
                    />
                  );
                })}
                <Grid size={{ xs: 8 }} />
                <Grid size={{ xs: 12 }}>
                  <Button
                    color="primary"
                    startIcon={<AddCircleOutline />}
                    onClick={() => {
                      arrayHelpers.push({
                        id: crypto.randomUUID(),
                        country: null,
                        partner: null,
                        number: '',
                      });
                    }}
                  >
                    {t('Add Identity')}
                  </Button>
                </Grid>
              </>
            )}
          />
        </Grid>
      </>
    )
  );
}

export default withErrorBoundary(
  AddIndividualDataChange,
  'AddIndividualDataChange',
);
