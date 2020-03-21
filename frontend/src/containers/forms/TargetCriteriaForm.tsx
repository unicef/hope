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

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const MediumLabel = styled.div`
  width: 60%;
  margin: 12px 0;
`;

const DateFields = styled.div`
  display: flex;
  justify-content: space-between;
  margin: 12px 0;
`;

const DateField = styled.div`
  width: 48%;
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

const validationSchema = Yup.object().shape({
  criterias: Yup.array().of(
    Yup.object().shape({
      name: Yup.string().required('Name is required'),
    }),
  ),
});

const SubField = ({ field, form, ...otherProps }) => {
  //eslint-disable-next-line
  // debugger
  // const subSelection = choices.find((each) => each.name === name);
  // switch (subSelection.type) {
  //   case 'SELECT_ONE':
  //     return <div>Select one</div>
  //   case 'INTEGER':
  //     return <div>integer</div>;
  //   default:
  //     return <div>default</div>;
  // }
  return <div>Select one</div>;
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
  //renderSubmit,
  open,
  onClose,
  title,
}): React.ReactElement {
  const { data, loading } = useImportedIndividualFieldsQuery();

  let initialValue = {
    criterias: [
      {
        label: '',
        value: '',
      },
    ],
  };

  if (loading) return null;

  if (criteria.core && criteria.core.length > 0) {
    initialValue = { criterias: criteria.core };
  }
  return (
    <DialogContainer>
      <Formik
        initialValues={initialValue}
        onSubmit={(values) => {
          //eslint-disable-next-line
          debugger;
          return console.log(values);
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
                          <div key={each.label}>
                            <Field
                              name={each.label}
                              label='Choose field type'
                              fullWidth
                              required
                              choices={data.allCoreFieldAttributes}
                              value={each.label}
                              component={FormikSelectField}
                            />
                            {each.label && (
                              <Field
                                name={each.value}
                                // choices={data.allCoreFieldAttributes.map(
                                //   (option) =>{
                                //     if(option.name === each.label) {
                                //       option.choices
                                //     }
                                //   }
                                // )}
                                value={each.value}
                                component={FormikSelectField}
                              />
                            )}
                          </div>
                        );
                      })}
                      <button
                        type='button'
                        onClick={() => arrayHelpers.push({ name: '' })}
                      >
                        Add
                      </button>
                    </>
                  )}
                />
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={onClose}>Cancel</Button>
                  <Button
                    onClick={submitForm}
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
