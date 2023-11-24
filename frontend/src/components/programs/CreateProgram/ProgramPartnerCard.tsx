import { Box, Button, Grid, IconButton } from '@material-ui/core';
import { Field, Form, Formik } from 'formik';
import EditIcon from '@material-ui/icons/Edit';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikRadioGroup } from '../../../shared/Formik/FormikRadioGroup';
import { BaseSection } from '../../core/BaseSection';
import { DeleteProgramPartner } from './DeleteProgramPartner';

interface ProgramPartnerCardProps {
  partner;
  handleDeleteProgramPartner: (id: string) => void;
  setStep: (step: number) => void;
  step: number;
}

const BigText = styled(Box)`
  font-size: 16;
  font-weight: 400;
`;

const SmallText = styled(Box)`
  font-size: 14;
  font-weight: 400;
`;

export const ProgramPartnerCard: React.FC<ProgramPartnerCardProps> = ({
  partner,
  handleDeleteProgramPartner,
  setStep,
  step,
}): React.ReactElement => {
  const { t } = useTranslation();
  const [isEdit, setEdit] = useState(false);

  const initialValues = {
    id: partner.id,
    partner: '',
    areaAccess: '',
    adminAreas: [],
  };

  const description = t(
    'Provide info about Programme Partner and set Area Access',
  );

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        // eslint-disable-next-line no-console
        console.log(values);
      }}
    >
      {({ submitForm, values }) => {
        let buttons;
        if (isEdit) {
          buttons = (
            <Box display='flex' justifyContent='center' alignItems='center'>
              <Box mr={4}>
                <Button onClick={() => setEdit(false)} variant='contained'>
                  {t('Cancel')}
                </Button>
              </Box>
              <Box mr={4}>
                <DeleteProgramPartner
                  partner={partner}
                  //TODO: add permission
                  canDeleteProgramPartner
                  handleDeleteProgramPartner={handleDeleteProgramPartner}
                />
              </Box>
              <Button
                disabled={!values.areaAccess}
                onClick={submitForm}
                variant='contained'
                color='primary'
              >
                {t('Save')}
              </Button>
            </Box>
          );
        }
        //TODO: check this condition
        else if (initialValues.areaAccess) {
          buttons = (
            <Box display='flex' justifyContent='center' alignItems='center'>
              <IconButton onClick={() => setEdit(true)}>
                <EditIcon />
              </IconButton>
            </Box>
          );
        } else {
          buttons = (
            <Box display='flex' justifyContent='center' alignItems='center'>
              <Box mr={4}>
                <DeleteProgramPartner
                  partner={partner}
                  //TODO: add permission
                  canDeleteProgramPartner
                  handleDeleteProgramPartner={handleDeleteProgramPartner}
                />
              </Box>{' '}
              <Button
                disabled={!values.areaAccess}
                onClick={submitForm}
                variant='contained'
                color='primary'
              >
                {t('Save')}
              </Button>
            </Box>
          );
        }

        const businessAreaOptionLabel = (
          <Box display='flex' flexDirection='column'>
            <BigText>{t('Business Area')}</BigText>
            <SmallText>
              {t('The partner has access to the entire business area')}
            </SmallText>
          </Box>
        );

        const adminAreaOptionLabel = (
          <Box display='flex' flexDirection='column'>
            <BigText>{t('Admin Area')}</BigText>
            <SmallText>
              {t('The partner has access to selected Admin Areas')}
            </SmallText>
            <SmallText>
              Selected Admin Areas:{' '}
              {values.adminAreas.length > 0 ? values.adminAreas.length : 0}
            </SmallText>
          </Box>
        );

        return (
          <Form>
            <BaseSection
              title={t('Programme Partner')}
              buttons={buttons}
              description={description}
            >
              <>
                <Grid container direction='column'>
                  <Grid item xs={6}>
                    <Field
                      name='areaAccess'
                      choices={[
                        {
                          value: 'BUSINESS_AREA',
                          name: t('Business Area'),
                          optionLabel: businessAreaOptionLabel,
                        },
                        {
                          value: 'ADMIN_AREA',
                          name: t('Admin Area'),
                          optionLabel: adminAreaOptionLabel,
                        },
                      ]}
                      component={FormikRadioGroup}
                      withGreyBox
                    />
                  </Grid>
                </Grid>
                <Button variant='outlined' onClick={() => setStep(step - 1)}>
                  {t('Back')}
                </Button>
                <Button
                  variant='contained'
                  color='primary'
                  onClick={() => setStep(step + 1)}
                  disabled={step === 1}
                >
                  {t('Next')}
                </Button>
              </>
            </BaseSection>
          </Form>
        );
      }}
    </Formik>
  );
};
