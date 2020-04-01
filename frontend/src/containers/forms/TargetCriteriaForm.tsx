import React from 'react';
import * as Yup from 'yup';
import styled from 'styled-components';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
  Button,
  DialogActions,
} from '@material-ui/core';
import { Field, Form, Formik, FieldArray } from 'formik';
import { useImportedIndividualFieldsQuery } from '../../__generated__/graphql';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { AddCircleOutline } from '@material-ui/icons';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const DialogContainer = styled.div`
  position: absolute;
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const AddCriteriaWrapper = styled.div`
  text-align: right;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: ${({ theme }) => theme.spacing(3)}px 0;
`;

const AddCriteria = styled.div`
  display: flex;
  align-items: center;
  color: #003c8f;
  text-transform: uppercase;
  cursor: pointer;
  svg {
    margin-right: ${({ theme }) => theme.spacing(2)}px;
  }
`;

const Divider = styled.div`
  border-top: 1px solid #b1b1b5;
  margin: ${({ theme }) => theme.spacing(10)}px 0;
  position: relative;
`;

const DividerLabel = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #253b46;
  text-transform: uppercase;
  padding: 5px;
  border: 1px solid #b1b1b5;
  border-radius: 50%;
  background-color: #fff;
`;

const validationSchema = Yup.object().shape({
  criterias: Yup.array().of(
    Yup.object().shape({
      label: Yup.string().required('Label is required'),
    }),
  ),
});

const SubField = ({ field, form, ...otherProps }) => {
  switch (otherProps.type) {
    case 'SELECT_ONE':
      return <FormikSelectField field={field} form={form} {...otherProps} />;
    default:
      return <div>Other fields</div>;
  }
};

interface ProgramFormPropTypes {
  criteria?;
  onSubmit: (values) => Promise<void>;
  renderSubmit: (submit: () => Promise<void>) => void;
  open: boolean;
  onClose: () => void;
  title: string;
}

export function TargetCriteriaForm({
  criteria,
  //onSubmit,
  addCriteria,
  open,
  onClose,
  title,
}): React.ReactElement {
  const { data, loading } = useImportedIndividualFieldsQuery();

  const initialValue = {
    criterias: [
      {
        label: '',
        value: '',
      },
    ],
  };

  if (loading) return null;

  // if (criteria.core && criteria.core.length > 0) {
  //   initialValue = { criterias: criteria.core };
  // }
  return (
    <DialogContainer>
      <Formik
        initialValues={initialValue}
        onSubmit={(values, bag) => {
          bag.resetForm();
          return addCriteria(values);
        }}
        validationSchema={validationSchema}
        enableReinitialize
      >
        {({ submitForm, values }) => (
          <>
            <Dialog
              open={open}
              onClose={onClose}
              scroll='paper'
              aria-labelledby='form-dialog-title'
            >
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title' disableTypography>
                  <Typography variant='h6'>{title}</Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogDescription>
                  Lorem ipsum dolor sit amet consectetur adipisicing elit. Natus
                  tempora iusto maxime? Odit expedita ipsam natus eos?
                </DialogDescription>
                <FieldArray
                  name='criterias'
                  render={(arrayHelpers) => (
                    <>
                      {values.criterias.map((each, index) => {
                        return (
                          //eslint-disable-next-line
                          <div key={index}>
                            <Field
                              name={`criterias[${index}].label`}
                              label='Choose field type'
                              fullWidth
                              required
                              choices={data.allFieldsAttributes}
                              index={index}
                              component={FormikSelectField}
                            />
                            {each.label && (
                              <Field
                                name={`criterias[${index}].value`}
                                choices={
                                  data.allFieldsAttributes.find(
                                    (attributes) =>
                                      attributes.name === each.label,
                                  ).choices
                                }
                                type={
                                  data.allFieldsAttributes.find(
                                    (attributes) =>
                                      attributes.name === each.label,
                                  ).type
                                }
                                component={SubField}
                              />
                            )}
                            {values.criterias.length === 1 &&
                            index === 0 ||
                            index === values.criterias.length - 1 ? null : (
                              <Divider>
                                <DividerLabel>And</DividerLabel>
                              </Divider>
                            )}
                          </div>
                        );
                      })}
                      <AddCriteriaWrapper>
                        <AddCriteria
                          onClick={() =>
                            arrayHelpers.push({ value: '', label: '' })
                          }
                        >
                          <AddCircleOutline />
                          <span>Add Criteria</span>
                        </AddCriteria>
                      </AddCriteriaWrapper>
                    </>
                  )}
                />
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => onClose()}>Cancel</Button>
                  <Button
                    onClick={() => submitForm()}
                    type='submit'
                    color='primary'
                    variant='contained'
                  >
                    Save
                  </Button>
                </DialogActions>
              </DialogFooter>
            </Dialog>
          </>
        )}
      </Formik>
    </DialogContainer>
  );
}
