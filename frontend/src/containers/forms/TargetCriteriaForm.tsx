import React from 'react';
import * as Yup from 'yup';
import styled from 'styled-components';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
  Button,
  IconButton,
  Box,
} from '@material-ui/core';
import { AddCircleOutline, Delete } from '@material-ui/icons';
import { Field, Formik, FieldArray } from 'formik';
import { useImportedIndividualFieldsQuery } from '../../__generated__/graphql';
import { SubField } from '../../components/TargetPopulation/SubField';
import {
  formatCriteriaFilters,
  mapCriteriasToInitialValues,
} from '../../utils/utils';
import { CriteriaAutocomplete } from '../../components/TargetPopulation/TargetingCriteria/CriteriaAutocomplete';
import { DialogActions } from '../dialogs/DialogActions';

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

const StyledBox = styled(Box)`
  width: 100%;
`;

const AddIcon = styled(AddCircleOutline)`
  margin-right: 10px;
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

const FlexWrapper = styled.div`
  display: flex;
  justify-content: space-between;
`;

const SubcriteriaBox = styled.div`
  border: 2px solid red;
`;

const validationSchema = Yup.object().shape({
  filters: Yup.array().of(
    Yup.object().shape({
      fieldName: Yup.string().required('Label is required'),
    }),
  ),
});

interface TargetCriteriaFormPropTypes {
  criteria?;
  addCriteria: (values) => void;
  open: boolean;
  onClose: () => void;
  title: string;
}

export function TargetCriteriaForm({
  criteria,
  addCriteria,
  open,
  onClose,
  title,
}: TargetCriteriaFormPropTypes): React.ReactElement {
  const { data, loading } = useImportedIndividualFieldsQuery();
  const mappedFilters = mapCriteriasToInitialValues(criteria);
  const initialValue = {
    filters: mappedFilters,
  };

  const chooseFieldType = (value, arrayHelpers, index): void => {
    const values = {
      isFlexField: value.isFlexField,
      associatedWith: value.associatedWith,
      fieldAttribute: {
        labelEn: value.labelEn,
        type: value.type,
        choices: null,
      },
      value: null,
    };
    switch (value.type) {
      case 'INTEGER':
        values.value = { from: '', to: '' };
        break;
      case 'SELECT_ONE':
        values.fieldAttribute.choices = value.choices;
        break;
      case 'SELECT_MANY':
        values.value = [];
        values.fieldAttribute.choices = value.choices;
        break;
      default:
        values.value = null;
        break;
    }
    arrayHelpers.replace(index, {
      ...values,
      fieldName: value.name,
      type: value.type,
    });
  };

  const clearField = (arrayHelpers, index): void => {
    return arrayHelpers.replace(index, {});
  };

  if (loading) return null;

  return (
    <DialogContainer>
      <Formik
        initialValues={initialValue}
        onSubmit={(values, bag) => {
          const dataToSend = formatCriteriaFilters(values);
          addCriteria({ filters: dataToSend });
          return bag.resetForm();
        }}
        validationSchema={validationSchema}
        enableReinitialize
      >
        {({ submitForm, values }) => (
          <>
            {console.log('💛values', values)}
            <FieldArray
              name='filters'
              render={(arrayHelpers) => (
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
                        Adding criteria below will target any individuals within
                        a household that meet the filters applied. You may also
                        add individual sub-criteria to further define an
                        individual.
                      </DialogDescription>
                      {values.filters.map((each, index) => {
                        return (
                          //eslint-disable-next-line
                          <div key={index}>
                            <FlexWrapper>
                              <Field
                                name={`filters[${index}].fieldName`}
                                label='Choose field type'
                                required
                                choices={data.allFieldsAttributes}
                                index={index}
                                value={each.fieldName || null}
                                onChange={(e, object) => {
                                  if (object) {
                                    return chooseFieldType(
                                      object,
                                      arrayHelpers,
                                      index,
                                    );
                                  }
                                  return clearField(arrayHelpers, index);
                                }}
                                component={CriteriaAutocomplete}
                              />
                              {values.filters.length > 1 && (
                                <IconButton
                                  onClick={() => arrayHelpers.remove(index)}
                                >
                                  <Delete />
                                </IconButton>
                              )}
                            </FlexWrapper>
                            {each.fieldName && (
                              <div data-cy='autocomplete-target-criteria-values'>
                                {SubField(each, index, `filters[${index}]`)}
                              </div>
                            )}
                            {each.fieldName &&
                              each.associatedWith !== 'Household' &&
                              values.filters.length && (
                                <>
                                  <SubcriteriaBox>
                                    <FieldArray
                                      name={`filters[${index}]].subcriteria`}
                                    >
                                      {(subcriteriaArrayHelpers) => (
                                        <>
                                          {values.filters[
                                            index
                                          ].subcriteria?.map(
                                            (eachSubcriteria, indexSub) => {
                                              return (
                                                //eslint-disable-next-line
                                                <div
                                                  key={`filter-${each.fieldName}-subcriteria-${indexSub}`}
                                                >
                                                  <FlexWrapper>
                                                    <Field
                                                      name={`filters[${index}].subcriteria[${indexSub}].fieldName`}
                                                      label='Choose field type'
                                                      required
                                                      choices={
                                                        data.allFieldsAttributes
                                                      }
                                                      index={indexSub}
                                                      value={
                                                        eachSubcriteria.value ||
                                                        null
                                                      }
                                                      onChange={(e, object) => {
                                                        if (object) {
                                                          return chooseFieldType(
                                                            object,
                                                            subcriteriaArrayHelpers,
                                                            indexSub,
                                                          );
                                                        }
                                                        return clearField(
                                                          subcriteriaArrayHelpers,
                                                          indexSub,
                                                        );
                                                      }}
                                                      component={
                                                        CriteriaAutocomplete
                                                      }
                                                    />
                                                    {values.filters[index]
                                                      ?.subcriteria?.length >
                                                      1 && (
                                                      <IconButton
                                                        onClick={() =>
                                                          subcriteriaArrayHelpers.remove(
                                                            indexSub,
                                                          )
                                                        }
                                                      >
                                                        <Delete />
                                                      </IconButton>
                                                    )}
                                                  </FlexWrapper>
                                                  {eachSubcriteria.fieldName && (
                                                    <div data-cy='autocomplete-target-subcriteria-values'>
                                                      {SubField(
                                                        eachSubcriteria,
                                                        index,
                                                        `filters[${index}].subcriteria[${indexSub}]`,
                                                      )}
                                                    </div>
                                                  )}
                                                </div>
                                              );
                                            },
                                          )}
                                          <Button
                                            onClick={() =>
                                              subcriteriaArrayHelpers.push({
                                                fieldName: '',
                                              })
                                            }
                                            color='primary'
                                          >
                                            <AddIcon /> Add individual
                                            sub-criteria
                                          </Button>
                                        </>
                                      )}
                                    </FieldArray>
                                  </SubcriteriaBox>
                                </>
                              )}

                            {(values.filters.length === 1 && index === 0) ||
                            index === values.filters.length - 1 ? null : (
                              <Divider>
                                <DividerLabel>And</DividerLabel>
                              </Divider>
                            )}
                          </div>
                        );
                      })}
                    </DialogContent>
                    <DialogFooter>
                      <DialogActions>
                        <StyledBox
                          display='flex'
                          justifyContent='space-between'
                        >
                          <div>
                            <Button
                              color='primary'
                              variant='outlined'
                              onClick={() =>
                                arrayHelpers.push({ fieldname: '' })
                              }
                            >
                              Add Next Criteria
                            </Button>
                          </div>
                          <div>
                            <Button onClick={() => onClose()}>Cancel</Button>
                            <Button
                              onClick={() => submitForm()}
                              type='submit'
                              color='primary'
                              variant='contained'
                              data-cy='button-target-population-add-criteria'
                            >
                              Save
                            </Button>
                          </div>
                        </StyledBox>
                      </DialogActions>
                    </DialogFooter>
                  </Dialog>
                </>
              )}
            />
          </>
        )}
      </Formik>
    </DialogContainer>
  );
}
