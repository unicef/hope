import * as Yup from 'yup';
import moment from 'moment';
import { today } from '@utils/utils';
import { TFunction } from 'i18next';

export const editProgramDetailsValidationSchema = (
  t: TFunction<'translation', undefined>,
  initialValues: any,
): Yup.ObjectSchema<any, any, any, any> => {
  let endDate = Yup.date()
    .transform((curr, orig) => (orig === '' ? null : curr))
    .when('startDate', (startDate, schema) =>
      startDate instanceof Date && !isNaN(startDate.getTime())
        ? schema.min(
            startDate,
            `${t('End date have to be greater than')} ${moment(
              startDate,
            ).format('YYYY-MM-DD')}`,
          )
        : schema,
    )
    .min(today, t('End Date cannot be in the past'))
    .nullable();

  if (initialValues.endDate) {
    endDate = endDate.required(t('End Date is required'));
  }

  return Yup.object().shape({
    editMode: Yup.boolean(),
    name: Yup.string()
      .required(t('Programme Name is required'))
      .min(3, t('Too short'))
      .max(150, t('Too long')),
    programmeCode: Yup.string()
      .min(4, t('Programme code has to be 4 characters'))
      .max(4, t('Programme code has to be 4 characters'))
      .matches(
        /^[A-Za-z0-9\-/.]{4}$/,
        t("Programme code may only contain letters, digits and '-', '/', '.'."),
      )
      .nullable(),
    startDate: Yup.date()
      .required(t('Start Date is required'))
      .transform((v) => (v instanceof Date && !isNaN(v.getTime()) ? v : null)),
    endDate,
    sector: Yup.string().required(t('Sector is required')),
    dataCollectingTypeCode: Yup.string().required(
      t('Data Collecting Type is required'),
    ),
    description: Yup.string()
      .min(3, t('Too short'))
      .max(255, t('Too long'))
      .nullable(),
    budget: Yup.number().min(0).max(99999999, t('Number is too big')),
    administrativeAreasOfImplementation: Yup.string()
      .min(2, t('Too short'))
      .max(255, t('Too long'))
      .nullable(),
    populationGoal: Yup.number().min(0).max(99999999, t('Number is too big')),
  });
};

export const editPartnersValidationSchema = (
  t: TFunction<'translation', undefined>,
): Yup.ObjectSchema<any, any, any, any> => {
  return Yup.object().shape({
    partnerAccess: Yup.string().required(),
    partners: Yup.array().of(
      Yup.object().shape({
        id: Yup.string().required(t('Partner ID is required')),
        areaAccess: Yup.string().required(t('Area Access is required')),
      }),
    ),
  });
};
