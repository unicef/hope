import styled from 'styled-components';
import { Field, FieldArray } from 'formik';
import { Box, Button } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import React from 'react';
import { ImportedIndividualFieldsQuery } from '../../__generated__/graphql';
import { chooseFieldType, clearField } from '../../utils/targetingUtils';
import { TargetCriteriaBlockFilter } from './TargetCriteriaBlockFilter';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';

const Divider = styled.div`
  border-top: 1px solid #e2e2e2;
  margin: ${({ theme }) => theme.spacing(5)}px 0;
  position: relative;
`;
const DividerLabel = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
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
  text-align: center;
`;
const AndDivider = styled.div`
  border-top: 1px solid #b1b1b5;
  margin: ${({ theme }) => theme.spacing(10)}px 0;
  position: relative;
`;
const ButtonBox = styled.div`
  width: 300px;
`;
const FieldBox = styled.div`
  margin-left: 10px;
`;
const AndDividerLabel = styled.div`
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
const GrayFiltersBlock = styled.div`
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  margin-bottom: 20px;
`;
const AddIcon = styled(AddCircleOutline)`
  margin-right: 10px;
`;
const FilterWrapper = styled.div`
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(5)}px;
`;
export function TargetCriteriaFilterBlocks({
  blockIndex,
  data,
  values,
  onDelete,
}: {
  blockIndex: number;
  data: ImportedIndividualFieldsQuery;
  values;
  onDelete: () => void;
}): React.ReactElement {
  const shouldShowAndDivider =
    blockIndex + 1 < values.individualsFiltersBlocks.length;
  return (
    <div>
      Set Individual Criteria
      <FieldArray
        name={`individualsFiltersBlocks[${blockIndex}].individualBlockFilters`}
        render={(arrayHelpers) => (
          <div>
            <GrayFiltersBlock>
              {values.individualsFiltersBlocks[
                blockIndex
              ].individualBlockFilters.map((each, index) => {
                const shouldShowDivider =
                  index + 1 <
                  values.individualsFiltersBlocks[blockIndex]
                    .individualBlockFilters.length;
                return (
                  <>
                    <FilterWrapper>
                      <TargetCriteriaBlockFilter
                        blockIndex={blockIndex}
                        index={index}
                        data={data}
                        each={each}
                        onChange={(e, object) => {
                          if (object) {
                            return chooseFieldType(object, arrayHelpers, index);
                          }
                          return clearField(arrayHelpers, index);
                        }}
                        onDelete={() => {
                          if (
                            values.individualsFiltersBlocks[blockIndex]
                              .individualBlockFilters.length === 1
                          ) {
                            onDelete();
                            return;
                          }
                          arrayHelpers.remove(index);
                        }}
                      />
                    </FilterWrapper>
                    {shouldShowDivider && (
                      <Divider>
                        <DividerLabel>+</DividerLabel>
                      </Divider>
                    )}
                  </>
                );
              })}
              <Box display='flex' justifyContent='center'>
                <Button
                  color='primary'
                  variant='outlined'
                  startIcon={<AddCircleOutline />}
                  onClick={() =>
                    arrayHelpers.push({
                      fieldName: '',
                    })
                  }
                  style={{
                    position: 'relative',
                    top: 18,
                    backgroundColor: '#fff',
                  }}
                >
                  Add Set of Criteria
                </Button>
              </Box>
            </GrayFiltersBlock>
          </div>
        )}
      />
      {shouldShowAndDivider && (
        <AndDivider>
          <AndDividerLabel>And</AndDividerLabel>
        </AndDivider>
      )}
    </div>
  );
}
